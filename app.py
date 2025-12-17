import streamlit as st
import sqlite3
import pandas as pd
import altair as alt

# -------------------- DATABASE CONNECTION --------------------
@st.cache_resource
def get_connection():
    return sqlite3.connect("aviation.db", check_same_thread=False)

conn = get_connection()

st.set_page_config(page_title="Air Tracker: Flight Analytics", layout="wide")

# -------------------- SIDEBAR --------------------
st.sidebar.title("✈ Air Tracker")
page = st.sidebar.radio(
    "Navigation",
    [
        "Home Dashboard",
        "Flights Explorer",
        "Airport Details",
        "Delay Analysis",
        "Route Leaderboards",
        "SQL Insights",
        "Creator Info"
    ]
)

# ==================== HOME DASHBOARD ====================
if page == "Home Dashboard":
    st.title("Air Tracker: Flight Analytics")

    total_airports = pd.read_sql(
        "SELECT COUNT(*) cnt FROM airports", conn
    )["cnt"][0]

    total_flights = pd.read_sql(
        "SELECT COUNT(*) cnt FROM flights", conn
    )["cnt"][0]

    avg_delay = pd.read_sql(
        """
        SELECT ROUND(AVG(avg_delay_min),2) avg_delay
        FROM airport_delays
        WHERE avg_delay_min IS NOT NULL
        """,
        conn
    )["avg_delay"][0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Airports", total_airports)
    c2.metric("Total Flights", total_flights)
    c3.metric("Average Delay (min)", avg_delay)

# ==================== FLIGHTS EXPLORER ====================
elif page == "Flights Explorer":
    st.title("Search & Filter Flights")

    status_filter = st.multiselect(
        "Flight Status",
        ["On Time", "Delayed", "Cancelled"],
        default=["On Time", "Delayed", "Cancelled"]
    )

    airline_filter = st.text_input("Airline Code")
    flight_filter = st.text_input("Flight Number")

    query = "SELECT * FROM flights WHERE 1=1"
    params = []

    if status_filter:
        query += f" AND status IN ({','.join(['?']*len(status_filter))})"
        params.extend(status_filter)

    if airline_filter:
        query += " AND airline_code LIKE ?"
        params.append(f"%{airline_filter}%")

    if flight_filter:
        query += " AND flight_number LIKE ?"
        params.append(f"%{flight_filter}%")

    df = pd.read_sql(query, conn, params=params)
    st.dataframe(df, use_container_width=True)

# ==================== AIRPORT DETAILS ====================
elif page == "Airport Details":
    st.title("Airport Details Viewer")

    airports = pd.read_sql(
        "SELECT iata_code FROM airports ORDER BY iata_code", conn
    )

    airport = st.selectbox("Select Airport", airports["iata_code"])

    info = pd.read_sql(
        "SELECT * FROM airports WHERE iata_code = ?",
        conn, params=(airport,)
    )
    st.subheader("Airport Information")
    st.dataframe(info)

    flights = pd.read_sql(
        """
        SELECT flight_number, destination_iata, status
        FROM flights
        WHERE origin_iata = ?
        """,
        conn, params=(airport,)
    )

    st.subheader("Outbound Flights")
    st.dataframe(flights)

# ==================== DELAY ANALYSIS ====================
elif page == "Delay Analysis":
    st.title("Delay Analysis")

    delay_df = pd.read_sql(
        """
        SELECT airport_iata, total_flights, delayed_flights, avg_delay_min
        FROM airport_delays
        WHERE total_flights >= 3
          AND avg_delay_min IS NOT NULL
        """,
        conn
    )

    chart = alt.Chart(delay_df).mark_bar(size=40).encode(
        x=alt.X("airport_iata:N", title="Airport"),
        y=alt.Y("avg_delay_min:Q", title="Average Delay (minutes)")
    )

    st.altair_chart(chart, use_container_width=True)

    st.subheader("Delay Percentage by Destination")

    pct = pd.read_sql(
        """
        SELECT
            destination_iata,
            COUNT(*) AS total_flights,
            SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) AS delayed_flights,
            ROUND(
                100.0 * SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END)
                / NULLIF(COUNT(*),0), 2
            ) AS delay_percentage
        FROM flights
        WHERE destination_iata IS NOT NULL
        GROUP BY destination_iata
        HAVING COUNT(*) >= 3
        ORDER BY delay_percentage DESC
        """,
        conn
    )

    st.dataframe(pct)

# ==================== ROUTE LEADERBOARDS ====================
elif page == "Route Leaderboards":
    st.title("Route Leaderboards")

    busiest = pd.read_sql(
        """
        SELECT
            origin_iata,
            destination_iata,
            COUNT(*) AS flight_count
        FROM flights
        WHERE origin_iata IS NOT NULL
          AND destination_iata IS NOT NULL
        GROUP BY origin_iata, destination_iata
        HAVING flight_count >= 2
        ORDER BY flight_count DESC
        """,
        conn
    )

    st.subheader("Busiest Routes")
    st.dataframe(busiest)

    delayed = pd.read_sql(
        """
        SELECT airport_iata, avg_delay_min
        FROM airport_delays
        WHERE avg_delay_min IS NOT NULL
        ORDER BY avg_delay_min DESC
        """,
        conn
    )

    st.subheader("Most Delayed Airports")
    st.dataframe(delayed)

# ==================== SQL INSIGHTS (ALL 11) ====================
elif page == "SQL Insights":
    st.title("SQL Insights")

    queries = {
        "Flights per Aircraft Model": """
        SELECT a.model, COUNT(f.flight_id) total_flights
        FROM flights f
        JOIN aircraft a ON f.aircraft_registration = a.registration
        WHERE a.model IS NOT NULL AND a.model <> ''
        GROUP BY a.model
        ORDER BY total_flights DESC
        """,

        "Aircraft with More Than 5 Flights": """
        SELECT a.registration, a.model, COUNT(f.flight_id) flight_count
        FROM flights f
        JOIN aircraft a ON f.aircraft_registration = a.registration
        WHERE a.model IS NOT NULL AND a.model <> ''
        GROUP BY a.registration, a.model
        HAVING flight_count > 5
        """,

        "Outbound Flights per Airport": """
        SELECT ap.name, COUNT(f.flight_id) outbound_flights
        FROM flights f
        JOIN airports ap ON f.origin_iata = ap.iata_code
        WHERE f.origin_iata IS NOT NULL AND f.origin_iata <> ''
        GROUP BY ap.name
        HAVING outbound_flights > 5
        """,

        "Top 3 Destination Airports": """
        SELECT ap.name, ap.city, COUNT(*) arrivals
        FROM flights f
        JOIN airports ap ON f.destination_iata = ap.iata_code
        GROUP BY ap.name, ap.city
        ORDER BY arrivals DESC
        LIMIT 3
        """,

        "Domestic vs International Flights": """
        SELECT f.flight_number, f.origin_iata, f.destination_iata,
        CASE
            WHEN a1.country = a2.country THEN 'Domestic'
            ELSE 'International'
        END AS flight_type
        FROM flights f
        JOIN airports a1 ON f.origin_iata = a1.iata_code
        JOIN airports a2 ON f.destination_iata = a2.iata_code
        """,

        "Recent Arrivals at DEL": """
        SELECT flight_number, aircraft_registration, origin_iata, actual_arrival
        FROM flights
        WHERE destination_iata = 'DEL'
        ORDER BY actual_arrival DESC
        LIMIT 5
        """,

        "Airports with No Arrivals": """
        SELECT name, iata_code
        FROM airports
        WHERE iata_code NOT IN (
            SELECT DISTINCT destination_iata FROM flights
        )
        """,

        "Flights by Airline and Status": """
        SELECT airline_code,
            SUM(CASE WHEN status='On Time' THEN 1 ELSE 0 END) on_time,
            SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END) delayed,
            SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) cancelled
        FROM flights
        GROUP BY airline_code
        """,

        "Cancelled Flights": """
        SELECT flight_number, aircraft_registration,
               origin_iata, destination_iata, scheduled_departure
        FROM flights
        WHERE status='Cancelled'
        ORDER BY scheduled_departure DESC
        """,

        "City Pairs with >2 Aircraft Models": """
        SELECT f.origin_iata, f.destination_iata,
               COUNT(DISTINCT a.model) model_count
        FROM flights f
        JOIN aircraft a ON f.aircraft_registration = a.registration
        WHERE a.model IS NOT NULL
        GROUP BY f.origin_iata, f.destination_iata
        HAVING model_count > 2
        """,

        "Delay Percentage per Destination": """
        SELECT destination_iata,
        ROUND(
            100.0 * SUM(CASE WHEN status='Delayed' THEN 1 ELSE 0 END)
            / NULLIF(COUNT(*),0), 2
        ) AS delay_percentage
        FROM flights
        GROUP BY destination_iata
        HAVING COUNT(*) >= 3
        ORDER BY delay_percentage DESC
        """
    }

    for title, sql in queries.items():
        st.subheader(title)
        st.dataframe(pd.read_sql(sql, conn))

# ==================== CREATOR INFO ====================
elif page == "Creator Info":
    st.title("Creator Information")
    st.write("""
    Name: Gokulraj K  
    Skills Used: Python, SQL, Streamlit, Data Analytics  
    Project: Air Tracker – Flight Analytics Dashboard  
    """)

st.caption("© 2025 | Air Tracker | Created by Gokulraj K")
