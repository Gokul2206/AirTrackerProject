# Air Tracker: Flight Analytics

PROJECT OVERVIEW
An interactive aviation analytics dashboard built using Python, SQLite, and Streamlit.
The application allows users to explore airports, flight schedules, and operational details,
providing insights on flight delays, busiest routes, and airport operations.

SKILLS ACQUIRED

* Python scripting
* API integration for data collection (used in Colab for database creation)
* SQL database design and management
* Data visualization using Streamlit and Altair

FEATURES

* Homepage dashboard with summary statistics
* Flight search and filtering by status, airline, origin, and date range
* Airport details viewer
* Delay analysis with charts
* Route leaderboards and busiest routes analysis

DATABASE

* SQLite database (aviation.db) contains all flight, airport, and aircraft data
* SQL queries are provided in sql\_queries.sql
* Note: The database is pre-populated. API fetch scripts are not included
  as the app runs fully using this database

HOW TO RUN

1. Install required packages:
   pip install -r requirements.txt
2. Run the Streamlit app:
   streamlit run app.py
3. The app will open in your browser and load all data from aviation.db
   Note: No API key or external fetch scripts are required for this demo

SQL QUERIES

* All required SQL queries for analytics are provided in sql\_queries.sql.
* Queries include:

  * Total flights per aircraft model
  * Aircraft with more than 5 flights
  * Outbound flights per airport
  * Top 3 destination airports
  * Domestic vs International flights
  * Recent arrivals at DEL airport
  * Airports with no arriving flights
  * Flights count by airline and status
  * Cancelled flights
  * City pairs with more than 2 aircraft models
  * Percentage of delayed flights per destination

NOTES

* SQLite is used for local demonstration; queries are compatible with MySQL/PostgreSQL
* The app is fully functional with the provided database
* API scripts used to fetch data in Colab are not included
* You can safely share or run the project without access to the API
