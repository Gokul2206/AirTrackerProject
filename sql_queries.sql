-- ============================================================
-- QUERY 1: Total flights per aircraft model
-- ============================================================
SELECT a.model, COUNT(f.flight_id) AS total_flights
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY a.model
ORDER BY total_flights DESC;



-- ============================================================
-- QUERY 2: Aircraft assigned to more than 5 flights
-- ============================================================
SELECT a.registration, a.model, COUNT(f.flight_id) AS flight_count
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY a.registration, a.model
HAVING flight_count > 5;



-- ============================================================
-- QUERY 3: Outbound flights per airport (more than 5 flights)
-- ============================================================
SELECT ap.name AS airport_name, COUNT(f.flight_id) AS outbound_flights
FROM flights f
JOIN airports ap ON f.origin_iata = ap.iata_code
GROUP BY ap.name
HAVING outbound_flights > 5;



-- ============================================================
-- QUERY 4: Top 3 destination airports by number of arrivals
-- ============================================================
SELECT ap.name AS dest_name, ap.city AS dest_city, COUNT(f.flight_id) AS arrivals
FROM flights f
JOIN airports ap ON f.destination_iata = ap.iata_code
GROUP BY ap.name, ap.city
ORDER BY arrivals DESC
LIMIT 3;



-- ============================================================
-- QUERY 5: Domestic or International flights
-- ============================================================
SELECT f.flight_number, f.origin_iata, f.destination_iata,
       CASE
           WHEN ap1.country = ap2.country THEN 'Domestic'
           ELSE 'International'
       END AS flight_type
FROM flights f
JOIN airports ap1 ON f.origin_iata = ap1.iata_code
JOIN airports ap2 ON f.destination_iata = ap2.iata_code;



-- ============================================================
-- QUERY 6: 5 most recent arrivals at DEL
-- ============================================================
SELECT f.flight_number, f.aircraft_registration, ap.name AS departure_airport, f.actual_arrival
FROM flights f
JOIN airports ap ON f.origin_iata = ap.iata_code
WHERE f.destination_iata = 'DEL'
ORDER BY f.actual_arrival DESC
LIMIT 5;



-- ============================================================
-- QUERY 7: Airports with no arriving flights
-- ============================================================
SELECT name, iata_code
FROM airports
WHERE iata_code NOT IN (SELECT DISTINCT destination_iata FROM flights);



-- ============================================================
-- QUERY 8: Flights by airline & status
-- ============================================================
SELECT f.airline_code,
       SUM(CASE WHEN f.status = 'On Time' THEN 1 ELSE 0 END) AS on_time,
       SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) AS delayed,
       SUM(CASE WHEN f.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM flights f
GROUP BY f.airline_code;



-- ============================================================
-- QUERY 9: All cancelled flights ordered by departure time
-- ============================================================
SELECT f.flight_number, f.aircraft_registration, f.origin_iata, f.destination_iata, f.scheduled_departure
FROM flights f
WHERE f.status = 'Cancelled'
ORDER BY f.scheduled_departure DESC;



-- ============================================================
-- QUERY 10: City pairs with more than 2 aircraft models
-- ============================================================
SELECT f.origin_iata, f.destination_iata, COUNT(DISTINCT a.model) AS model_count
FROM flights f
JOIN aircraft a ON f.aircraft_registration = a.registration
GROUP BY f.origin_iata, f.destination_iata
HAVING model_count > 2;



-- ============================================================
-- QUERY 11: Percentage of delayed flights per destination
-- ============================================================
SELECT f.destination_iata,
       ROUND(100.0 * SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) 
             / COUNT(f.flight_id), 2) AS percent_delayed
FROM flights f
GROUP BY f.destination_iata
ORDER BY percent_delayed DESC;