# AeroDataBox Flight Explorer ✈️

## 📌 Project Overview
The **AeroDataBox Flight Explorer** is a Streamlit-based application designed to manage, visualize, and analyze aviation data extracted from the AeroDataBox API. The project demonstrates end-to-end workflow:  
- **Data Extraction** from API endpoints  
- **Transformation** of JSON into relational schema  
- **Storage** in a SQL database  
- **Analysis** using SQL queries  
- **Visualization** with interactive dashboards  

This tool assists aviation enthusiasts, analysts, and organizations in exploring airport networks, flight patterns, and operational insights.

---

## 🎯 Objectives
- Provide detailed airport exploration (location, timezone, linked flights).  
- Enable flight trend analysis by airline, status, and time.  
- Deliver operational insights into delays and cancellations.  
- Support decision-making for airport managers and travel planners.  

---

## 🛠️ Workflow
1. **Data Extraction**  
   - Fetch airport, flight, aircraft, and delay data using AeroDataBox API.  
   - Parse nested JSON responses into structured Python objects.  

2. **Data Transformation**  
   - Flatten JSON into tabular format.  
   - Ensure consistent data types (e.g., dates, codes).  

3. **Data Storage**  
   - Store structured data in SQLite (`aviation.db`).  
   - Tables: `airports`, `aircraft`, `flights`, `airport_delays`.  

4. **Analysis**  
   - Write SQL queries for insights (e.g., busiest routes, delay percentages).  
   - Use joins and aggregations to simulate relationships.  

5. **Visualization**  
   - Build Streamlit dashboards with filters, charts, and tables.  
   - Provide pagination for large datasets.  

---

## 🗄️ Schema Design
### Airports
```sql
CREATE TABLE airports (
    airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
    icao_code TEXT UNIQUE,
    iata_code TEXT UNIQUE,
    name TEXT,
    city TEXT,
    country TEXT,
    continent TEXT,
    latitude REAL,
    longitude REAL,
    timezone TEXT
);
```

### Aircraft
```sql
CREATE TABLE aircraft (
    aircraft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration TEXT UNIQUE,
    model TEXT,
    manufacturer TEXT,
    icao_type_code TEXT,
    owner TEXT
);
```

### Flights
```sql
CREATE TABLE flights (
    flight_id TEXT PRIMARY KEY,
    flight_number TEXT,
    aircraft_registration TEXT,
    origin_iata TEXT,
    destination_iata TEXT,
    scheduled_departure TEXT,
    actual_departure TEXT,
    scheduled_arrival TEXT,
    actual_arrival TEXT,
    status TEXT,
    airline_code TEXT
);
```

### Airport Delays
```sql
CREATE TABLE airport_delays (
    delay_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_iata TEXT,
    delay_date TEXT,
    total_flights INTEGER,
    delayed_flights INTEGER,
    avg_delay_min INTEGER,
    median_delay_min INTEGER,
    canceled_flights INTEGER
);
```

---

## 📊 Key SQL Queries
- Flights per aircraft model  
- Aircraft with >5 flights  
- Outbound flights per airport  
- Top 3 destination airports  
- Domestic vs International classification  
- Most recent arrivals at DEL  
- Airports with no arrivals  
- Airline flight counts by status  
- Cancelled flights ordered by departure  
- City pairs with >2 aircraft models  
- Delay percentage per destination  

---

## 💻 Streamlit Application Features
- **Homepage Dashboard**: Total airports, flights, average delay.  
- **Search & Filter Flights**: By number, airline, status, date range.  
- **Airport Details Viewer**: Info + linked flights.  
- **Delay Analysis**: Charts and tables of delay statistics.  
- **Route Leaderboards**: Busiest routes and most delayed airports.  

---

## 🚧 Challenges
- Handling nested JSON structures from API.  
- Ensuring consistent schema design without enforced foreign keys.  
- Managing large datasets with pagination and caching.  
- Dealing with API rate limits and missing data.  

---

## 🌟 Insights
- Most delays cluster around specific airports.  
- Certain aircraft models dominate flight schedules.  
- Domestic vs International classification provides operational context.  
- Route leaderboards highlight busiest connections.  

---

## ⚙️ Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aerodatabox-flight-explorer.git
   cd aerodatabox-flight-explorer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
4. Ensure `aviation.db` is present in the project root.

---

## 🎥 Demo
- Launch the app locally with Streamlit.  
- Navigate through dashboards: airports, flights, delays, routes.  
- Apply filters to explore specific insights interactively.  

---
