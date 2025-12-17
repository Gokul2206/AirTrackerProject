/* =========================================================
   Air Tracker: Flight Analytics
   SQL Queries Document
   ========================================================= */


/* ---------------------------------------------------------
   Query 1:
   Show the total number of flights for each aircraft model
--------------------------------------------------------- */
SELECT 
    a.model,
    COUNT(f.flight_id) AS total_flights
FROM flights f
JOIN aircraft a 
    ON f.aircraft_registration = a.registration
GROUP BY a.model
ORDER BY total_flights DESC;


/* ---------------------------------------------------------
   Query 2:
   List all aircraft (registration, model) assigned
   to more than 5 flights
--------------------------------------------------------- */
SELECT 
    a.registration,
    a.model,
    COUNT(f.flight_id) AS flight_count
FROM flights f
JOIN aircraft a 
    ON f.aircraft_registration = a.registration
GROUP BY a.registration, a.model
HAVING COUNT(f.flight_id) > 5;


/* ---------------------------------------------------------
   Query 3:
   For each airport, display its name and the number of
   outbound flights (only airports with more than 5 flights)
--------------------------------------------------------- */
SELECT 
    ap.name AS airport_name,
    COUNT(f.flight_id) AS outbound_flights
FROM flights f
JOIN airports ap 
    ON f.origin_iata = ap.iata_code
GROUP BY ap.name
HAVING COUNT(f.flight_id) > 5;


/* ---------------------------------------------------------
   Query 4:
   Top 3 destination airports by number of arriving flights
--------------------------------------------------------- */
SELECT 
    ap.name AS destination_airport,
    ap.city AS destination_city,
    COUNT(f.flight_id) AS arrivals
FROM flights f
JOIN airports ap 
    ON f.destination_iata = ap.iata_code
GROUP BY ap.name, ap.city
ORDER BY arrivals DESC
LIMIT 3;


/* ---------------------------------------------------------
   Query 5:
   Show each flight with label Domestic / International
--------------------------------------------------------- */
SELECT 
    f.flight_number,
    f.origin_iata,
    f.destination_iata,
    CASE
        WHEN ap1.country = ap2.country THEN 'Domestic'
        ELSE 'International'
    END AS flight_type
FROM flights f
JOIN airports ap1 
    ON f.origin_iata = ap1.iata_code
JOIN airports ap2 
    ON f.destination_iata = ap2.iata_code;


/* ---------------------------------------------------------
   Query 6:
   Show the 5 most recent arrivals at DEL airport
--------------------------------------------------------- */
SELECT 
    f.flight_number,
    f.aircraft_registration,
    ap.name AS departure_airport,
    f.actual_arrival
FROM flights f
JOIN airports ap 
    ON f.origin_iata = ap.iata_code
WHERE f.destination_iata = 'DEL'
ORDER BY f.actual_arrival DESC
LIMIT 5;


/* ---------------------------------------------------------
   Query 7:
   Find all airports with no arriving flights
--------------------------------------------------------- */
SELECT 
    ap.name,
    ap.iata_code
FROM airports ap
WHERE ap.iata_code NOT IN (
    SELECT DISTINCT destination_iata 
    FROM flights
);


/* ---------------------------------------------------------
   Query 8:
   For each airline, count the number of flights by status
--------------------------------------------------------- */
SELECT 
    airline_code,
    SUM(CASE WHEN status = 'On Time' THEN 1 ELSE 0 END) AS on_time,
    SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) AS delayed,
    SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM flights
GROUP BY airline_code;


/* ---------------------------------------------------------
   Query 9:
   Show all cancelled flights ordered by departure time
--------------------------------------------------------- */
SELECT 
    flight_number,
    aircraft_registration,
    origin_iata,
    destination_iata,
    scheduled_departure
FROM flights
WHERE status = 'Cancelled'
ORDER BY scheduled_departure DESC;


/* ---------------------------------------------------------
   Query 10:
   List city pairs that have more than 2 different
   aircraft models operating between them
--------------------------------------------------------- */
SELECT 
    f.origin_iata,
    f.destination_iata,
    COUNT(DISTINCT a.model) AS model_count
FROM flights f
JOIN aircraft a 
    ON f.aircraft_registration = a.registration
GROUP BY f.origin_iata, f.destination_iata
HAVING COUNT(DISTINCT a.model) > 2;


/* ---------------------------------------------------------
   Query 11:
   For each destination airport, compute the percentage
   of delayed flights among all arrivals
--------------------------------------------------------- */
SELECT 
    destination_iata,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END)
        / COUNT(flight_id),
        2
    ) AS percent_delayed
FROM flights
GROUP BY destination_iata
ORDER BY percent_delayed DESC;
