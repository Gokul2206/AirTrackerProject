"""
API Scripts: AeroDataBox Flight Explorer
----------------------------------------
This module handles data extraction from AeroDataBox and AviationStack APIs.
It includes functions for fetching airport, flight, aircraft, and delay data,
with error handling and safe handling of missing values.
"""

import requests
import time
import sqlite3

# -----------------------------
# CONFIGURATION
# -----------------------------
API_HOST = "aerodatabox.p.rapidapi.com"
API_KEY = "your_api_key_here"   # replace with your key
AVIATIONSTACK_KEY = "your_aviationstack_key_here"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_connection(db_file="aviation.db"):
    """Create SQLite connection."""
    return sqlite3.connect(db_file)

# -----------------------------
# AIRPORT DATA
# -----------------------------
def fetch_airport(iata_code: str) -> dict:
    """Fetch airport details by IATA code."""
    try:
        url = f"https://{API_HOST}/airports/iata/{iata_code}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json() or {}
    except requests.exceptions.RequestException as e:
        print(f"✖ Airport fetch failed: {iata_code}, Error: {e}")
        return {}

def insert_airport(cur, data: dict):
    """Insert airport record into DB."""
    cur.execute("""
        INSERT OR IGNORE INTO airport
        (icao_code, iata_code, name, city, country, continent, latitude, longitude, timezone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("icao"),
        data.get("iata"),
        data.get("name"),
        data.get("municipalityName"),
        (data.get("country") or {}).get("name"),
        (data.get("continent") or {}).get("name"),
        (data.get("location") or {}).get("lat"),
        (data.get("location") or {}).get("lon"),
        data.get("timeZone")
    ))

# -----------------------------
# AIRCRAFT DATA
# -----------------------------
def fetch_aircraft(registration: str) -> dict:
    """Fetch aircraft details by registration."""
    try:
        url = f"https://{API_HOST}/aircrafts/reg/{registration}/registrations"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json() or {}
    except requests.exceptions.RequestException as e:
        print(f"✖ Aircraft fetch failed: {registration}, Error: {e}")
        return {}

def insert_aircraft(cur, reg: str, data: dict):
    """Insert aircraft record into DB."""
    if not data:
        return
    a = data[0]  # first record
    cur.execute("""
        INSERT OR IGNORE INTO aircraft
        (registration, model, manufacturer, icao_type_code, owner)
        VALUES (?, ?, ?, ?, ?)
    """, (
        reg,
        a.get("model"),
        a.get("manufacturer"),
        a.get("icaoTypeCode"),
        a.get("owner")
    ))

# -----------------------------
# FLIGHT DATA (AviationStack)
# -----------------------------
def fetch_flights(dep_iata: str, limit: int = 50) -> list:
    """Fetch flights departing from a given airport using AviationStack API."""
    try:
        url = "http://api.aviationstack.com/v1/flights"
        params = {"access_key": AVIATIONSTACK_KEY, "dep_iata": dep_iata, "limit": limit}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"✖ Flights fetch failed: {dep_iata}, Error: {e}")
        return []

def insert_flight(cur, f: dict):
    """Insert flight record into DB."""
    aircraft = f.get("aircraft") or {}
    departure = f.get("departure") or {}
    arrival = f.get("arrival") or {}
    flight = f.get("flight") or {}
    airline = f.get("airline") or {}

    flight_id = flight.get("iata") or flight.get("icao")
    if not flight_id:
        return

    cur.execute("""
        INSERT OR IGNORE INTO flights
        (flight_id, flight_number, aircraft_registration,
         origin_iata, destination_iata,
         scheduled_departure, actual_departure,
         scheduled_arrival, actual_arrival,
         status, airline_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        flight_id,
        flight.get("iata"),
        aircraft.get("registration") or aircraft.get("icao24"),
        departure.get("iata"),
        arrival.get("iata"),
        departure.get("scheduled"),
        departure.get("actual"),
        arrival.get("scheduled"),
        arrival.get("actual"),
        f.get("flight_status"),
        airline.get("iata")
    ))

# -----------------------------
# SAMPLE USAGE
# -----------------------------
if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()

    airport_codes = ["DEL", "BOM", "BLR", "MAA", "HYD"]

    # Example: fetch and insert airports
    for code in airport_codes:
        data = fetch_airport(code)
        if data:
            insert_airport(cur, data)
            conn.commit()
            print(f"✔ Airport inserted: {code}")
        time.sleep(1)

    # Example: fetch and insert aircraft
    regs = ["VP-BZP"]
    for reg in regs:
        data = fetch_aircraft(reg)
        if data:
            insert_aircraft(cur, reg, data)
            conn.commit()
            print(f"✔ Aircraft inserted: {reg}")
        time.sleep(1)

    # Example: fetch and insert flights
    for code in airport_codes:
        flights = fetch_flights(code)
        print(f"✔ {code} flights fetched:", len(flights))
        for f in flights:
            insert_flight(cur, f)
        conn.commit()
        time.sleep(1)

    conn.close()
    print("All data inserted successfully!")
