##### \- Air Tracker – Flight Analytics

##### 

##### \- Project Overview

##### &nbsp; - Air Tracker is a Python and Streamlit-based aviation analytics tool.

##### &nbsp; - Provides insights on airports, flights, delays, busiest routes, and aircraft usage.

##### &nbsp; - Uses SQL queries and interactive dashboards.

##### 

##### \- Features

##### &nbsp; - Home Dashboard: Summary of total airports, flights, and average delays.

##### &nbsp; - Search and Filter Flights: Filter by flight number, airline, origin, status, and date range.

##### &nbsp; - Airport Details: Provides airport information and linked flights.

##### &nbsp; - Delay Analysis: Shows airport-wise average delay with charts.

##### &nbsp; - Route Leaderboards: Displays busiest routes and most delayed airports.

##### &nbsp; - SQL Insights: 11 advanced SQL queries for analytics.

##### &nbsp; - About / Creator: Project and creator information.

##### 

##### \- Technologies Used

##### &nbsp; - Python 3.x

##### &nbsp; - Streamlit

##### &nbsp; - SQLite (aviation.db)

##### &nbsp; - Pandas

##### &nbsp; - Altair (for charts)

##### 

##### \- Folder Structure

##### &nbsp; - `app.py` – Main Streamlit application

##### &nbsp; - `aviation.db` – SQLite database

##### &nbsp; - `requirements.txt` – Python dependencies

##### &nbsp; - `README.md` – This documentation

##### 

##### \- Features Explained

##### &nbsp; - Pagination: Tables with many rows use pagination for performance. Each table uses a unique key in Streamlit to avoid duplicate widget ID errors.

##### &nbsp; - Cached SQL Queries: Queries are cached using `st.cache\_data` for faster performance.

##### &nbsp; - Responsive UI: Streamlit widgets like filters and date selectors update tables dynamically. Layout is minimalist and beginner-friendly.

##### 

##### \- Best Practices Implemented

##### &nbsp; - Coding Standards: PEP8, meaningful variable names, modular functions.

##### &nbsp; - SQL Practices: Normalized tables, indexes created for performance.

##### &nbsp; - Streamlit UI: Interactive widgets, pagination, responsive layout.

##### &nbsp; - Performance: Cached queries and paginated tables.

##### &nbsp; - Documentation \& Testing: Docstrings in code, tested components, this README.

##### 

##### \- Creator

##### &nbsp; - Name: Gokulraj K

##### &nbsp; - Skills Used: Python, SQL, API Integration, Streamlit, Data Analytics

##### 

##### \- Demo

##### &nbsp; - Run the app locally using `streamlit run app.py`.

##### &nbsp; - Explore dashboards, filter flights, and analyze delays.

##### &nbsp; - Check SQL Insights for detailed flight analytics.

##### 

