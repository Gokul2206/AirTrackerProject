"""
Air Tracker – Flight Analytics Application

Guidelines implemented:
- Coding Standards: Meaningful names, PEP8 formatting
- Modularization: Functions for pages and utilities
- Error handling: try-except for database and SQL queries
- Documentation: Docstrings included
- SQL Practices: Assumes normalized tables, indexes added externally
- Streamlit UI: Responsive, filterable widgets
- Performance: Pagination and caching
"""

import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from typing import List, Optional

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def create_connection(db_file: str = "aviation.db") -> Optional[sqlite3.Connection]:
    """Create SQLite connection with error handling."""
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

conn = create_connection()

# -----------------------------
# CACHED SQL EXECUTION
# -----------------------------
@st.cache_data(show_spinner=False)
def execute_query(sql_query: str, params: Optional[List] = None) -> pd.DataFrame:
    """Execute SQL query and return DataFrame."""
    try:
        if params:
            return pd.read_sql(sql_query, conn, params=params)
        return pd.read_sql(sql_query, conn)
    except Exception as e:
        st.error(f"Query failed: {e}")
        return pd.DataFrame()

# -----------------------------
# PAGINATION UTILITY
# -----------------------------
def display_paginated_table(df: pd.DataFrame, rows_per_page: int = 20, key: str = None):
    """
    Display DataFrame with pagination.
    Args:
        df: DataFrame to display
        rows_per_page: Number of rows per page
        key: unique Streamlit widget key
    """
    total_rows = len(df)
    if total_rows == 0:
        st.info("No data to display.")
        return

    total_pages = (total_rows - 1) // rows_per_page + 1
    current_page = st.number_input(
        "Page", min_value=1, max_value=total_pages, value=1, step=1, key=key
    )
    start_idx = (current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    st.write(f"Showing rows {start_idx + 1} to {min(end_idx, total_rows)} of {total_rows}")
    st.dataframe(df[start_idx:end_idx], use_container_width=True)

# -----------------------------
# HOME DASHBOARD
# -----------------------------
def home_dashboard():
    """Display summary metrics for airports, flights, and average delay."""
    total_airports = execute_query(
        "SELECT COUNT(*) AS cnt FROM airports WHERE name IS NOT NULL AND name <> ''"
    )["cnt"][0]

    total_flights = execute_query("SELECT COUNT(*) AS cnt FROM flights")["cnt"][0]

    avg_delay = execute_query(
        "SELECT ROUND(AVG(avg_delay_min),2) AS avg_delay FROM airport_delays"
    )["avg_delay"][0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Airports", total_airports)
    c2.metric("Total Flights", total_flights)
    c3.metric("Average Delay (mins)", avg_delay if avg_delay else 0)

# -----------------------------
# SEARCH & FILTER FLIGHTS
# -----------------------------
def search_flights():
    """Search flights with filters: number, airline, origin, status, date range."""
    st.subheader("Search and Filter Flights")
    flight_no = st.text_input("Search by Flight Number")

    airlines = execute_query(
        "SELECT DISTINCT airline_code FROM flights WHERE airline_code IS NOT NULL AND airline_code <> ''"
    )["airline_code"].tolist()

    origins = execute_query(
        "SELECT DISTINCT origin_iata FROM flights WHERE origin_iata IS NOT NULL AND origin_iata <> ''"
    )["origin_iata"].tolist()

    airline = st.selectbox("Filter by Airline", ["All"] + airlines)
    origin = st.selectbox("Filter by Origin Airport", ["All"] + origins)

    status = st.multiselect(
        "Filter by Status",
        ["Completed", "Delayed", "Cancelled"],
        default=["Completed", "Delayed", "Cancelled"]
    )

    date_range = st.date_input("Filter by Date Range", [])

    # Build SQL query dynamically
    query = f"""
        SELECT flight_number, airline_code, origin_iata, destination_iata,
               scheduled_departure, actual_arrival, status
        FROM flights
        WHERE status IN ({','.join(['?']*len(status))})
    """
    params = status.copy()

    if flight_no:
        query += " AND flight_number LIKE ?"
        params.append(f"%{flight_no}%")
    if airline != "All":
        query += " AND airline_code = ?"
        params.append(airline)
    if origin != "All":
        query += " AND origin_iata = ?"
        params.append(origin)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        query += " AND DATE(scheduled_departure) BETWEEN ? AND ?"
        params.extend([date_range[0], date_range[1]])

    df = execute_query(query, params)
    display_paginated_table(df, key="search_flights_table")

# -----------------------------
# AIRPORT DETAILS
# -----------------------------
def airport_details():
    """Display airport information and linked flights."""
    airports = execute_query(
        "SELECT iata_code FROM airports WHERE iata_code IS NOT NULL AND iata_code <> ''"
    )["iata_code"].tolist()

    selected_airport = st.selectbox("Select Airport", airports)

    airport_info = execute_query(
        """
        SELECT name, city, country, timezone, latitude, longitude
        FROM airports
        WHERE iata_code = ?
        """,
        [selected_airport]
    )
    st.markdown("### Airport Information")
    st.table(airport_info)

    linked_flights = execute_query(
        """
        SELECT flight_number, origin_iata, destination_iata, status
        FROM flights
        WHERE origin_iata = ? OR destination_iata = ?
        """,
        [selected_airport, selected_airport]
    )
    st.markdown("### Linked Flights")
    display_paginated_table(linked_flights, key=f"linked_flights_{selected_airport}")

# -----------------------------
# DELAY ANALYSIS
# -----------------------------
def delay_analysis():
    """Display average delays per airport in chart and table."""
    delay_df = execute_query(
        "SELECT airport_iata, avg_delay_min FROM airport_delays WHERE avg_delay_min IS NOT NULL"
    )
    if not delay_df.empty:
        chart = alt.Chart(delay_df).mark_bar().encode(x="airport_iata", y="avg_delay_min")
        st.altair_chart(chart, use_container_width=True)
        display_paginated_table(delay_df, key="delay_analysis_table")
    else:
        st.info("No delay data available.")

# -----------------------------
# ROUTE LEADERBOARDS
# -----------------------------
def route_leaderboards():
    """Display busiest routes and most delayed airports."""
    busiest = execute_query(
        """
        SELECT origin_iata, destination_iata, COUNT(*) AS flights
        FROM flights
        WHERE origin_iata IS NOT NULL AND destination_iata IS NOT NULL
        GROUP BY origin_iata, destination_iata
        ORDER BY flights DESC
        LIMIT 10
        """
    )
    st.subheader("Busiest Routes")
    display_paginated_table(busiest, key="busiest_routes_table")

    delayed = execute_query(
        "SELECT airport_iata, avg_delay_min FROM airport_delays ORDER BY avg_delay_min DESC"
    )
    st.subheader("Most Delayed Airports")
    display_paginated_table(delayed, key="most_delayed_airports_table")

# -----------------------------
# SQL INSIGHTS
# -----------------------------
def sql_insights():
    """Run predefined SQL queries (11 queries) and display results."""
    sql_queries = {
        "1. Flights per Aircraft Model": """
            SELECT a.model, COUNT(f.flight_id) total_flights
            FROM flights f
            JOIN aircraft a ON f.aircraft_registration = a.registration
            WHERE a.model IS NOT NULL AND a.model <> ''
            GROUP BY a.model
        """,
        "2. Aircraft used in more than 5 flights": """
            SELECT a.registration, a.model, COUNT(*) flight_count
            FROM flights f
            JOIN aircraft a ON f.aircraft_registration = a.registration
            WHERE a.model IS NOT NULL AND a.model <> ''
            GROUP BY a.registration, a.model
            HAVING flight_count > 5
        """,
        "3. Outbound flights per airport (>5)": """
            SELECT ap.name, COUNT(*) outbound_flights
            FROM flights f
            JOIN airports ap ON f.origin_iata = ap.iata_code
            WHERE ap.name IS NOT NULL AND ap.name <> ''
            GROUP BY ap.name
            HAVING outbound_flights > 5
        """,
        "4. Top 3 destination airports": """
            SELECT ap.name, ap.city, COUNT(*) arrivals
            FROM flights f
            JOIN airports ap ON f.destination_iata = ap.iata_code
            GROUP BY ap.name, ap.city
            ORDER BY arrivals DESC
            LIMIT 3
        """,
        "5. Domestic vs International flights": """
            SELECT f.flight_number, f.origin_iata, f.destination_iata,
            CASE WHEN o.country = d.country THEN 'Domestic'
                 ELSE 'International' END flight_type
            FROM flights f
            JOIN airports o ON f.origin_iata = o.iata_code
            JOIN airports d ON f.destination_iata = d.iata_code
        """,
        "6. 5 recent arrivals at DEL": """
            SELECT flight_number, aircraft_registration, origin_iata, actual_arrival
            FROM flights
            WHERE destination_iata = 'DEL'
            ORDER BY actual_arrival DESC
            LIMIT 5
        """,
        "7. Airports with no arrivals": """
            SELECT name, iata_code
            FROM airports
            WHERE iata_code NOT IN (SELECT DISTINCT destination_iata FROM flights)
        """,
        "8. Flights by airline & status": """
            SELECT airline_code,
            SUM(CASE WHEN status='On Time' THEN 1 ELSE 0 END) on_time,
            SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) delayed,
            SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) cancelled
            FROM flights
            WHERE airline_code IS NOT NULL AND airline_code <> ''
            GROUP BY airline_code
        """,
        "9. Cancelled flights": """
            SELECT flight_number, aircraft_registration, origin_iata, destination_iata
            FROM flights
            WHERE status='Cancelled'
            ORDER BY scheduled_departure DESC
        """,
        "10. City pairs with >2 aircraft models": """
            SELECT origin_iata, destination_iata,
                   COUNT(DISTINCT a.model) models
            FROM flights f
            JOIN aircraft a ON f.aircraft_registration = a.registration
            WHERE a.model IS NOT NULL AND a.model <> ''
            GROUP BY origin_iata, destination_iata
            HAVING models > 2
        """,
        "11. % delayed flights per destination": """
            SELECT destination_iata,
            ROUND(100.0 * SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END)
                  / COUNT(*), 2) delay_percentage
            FROM flights
            GROUP BY destination_iata
            ORDER BY delay_percentage DESC
        """
    }

    st.subheader("SQL Query Insights")
    for i, (title, sql) in enumerate(sql_queries.items()):
        st.markdown(f"### {title}")
        df = execute_query(sql)
        display_paginated_table(df, key=f"sql_insight_{i}")

# -----------------------------
# ABOUT / CREATOR
# -----------------------------
def about_page():
    """Display project and creator information."""
    st.subheader("Creator Information")
    st.markdown("""
    **Name:** Gokulraj K  
    **Project:** Air Tracker – Flight Analytics  
    **Skills Used:** Python, SQL, API Integration, Streamlit, Data Analytics  

    This project demonstrates end-to-end aviation analytics
    using real-world API data and SQL-based insights.
    """)

# -----------------------------
# MAIN NAVIGATION
# -----------------------------
st.set_page_config(page_title="Air Tracker", layout="wide")
st.title("✈️ Air Tracker: Flight Analytics")

pages = {
    "Home Dashboard": home_dashboard,
    "Search & Filter Flights": search_flights,
    "Airport Details": airport_details,
    "Delay Analysis": delay_analysis,
    "Route Leaderboards": route_leaderboards,
    "SQL Insights": sql_insights,
    "About / Creator": about_page
}

menu_selection = st.sidebar.radio("Navigation", list(pages.keys()))
pages[menu_selection]()
