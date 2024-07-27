import json
import os
import random
import statistics
import time
from datetime import datetime, timedelta
import logging

# logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# defined Constants
N = 5000  # Number of JSON files to generate
M = (50, 100)  # Range of random size for each JSON file
K = (100, 200)  # Range of total cities
L = (0.005, 0.001)  # Range of probability for NULL values

# flight data generation phase 
def generate_flights():
    logger.info("Generating flights data...")
    cities = [f"City {i}" for i in range(random.randint(*K))]
    for i in range(N):
        file_path = f"/tmp/flights/{datetime.now().strftime('%m-%y')}-{random.choice(cities)}-flights.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            flights = []
            for _ in range(random.randint(*M)):
                flight = {
                    "date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
                    "origin_city": random.choice(cities),
                    "destination_city": random.choice(cities),
                    "flight_duration_secs": random.randint(3600, 7200),  # 1-2 hours
                    "passengers_on_board": random.randint(50, 200)
                }
                if random.random() < random.uniform(*L):
                    flight[random.choice(list(flight.keys()))] = None
                flights.append(flight)
            json.dump(flights, f)
    logger.info("Flights data generated successfully!")

# flight data analysis & Cleaning phase
def analyze_flights():
    logger.info("Analyzing flights data...")
    start_time = time.time()
    total_records = 0
    dirty_records = 0
    flight_durations = {}
    passengers_arrived = {}
    passengers_left = {}

    for root, dirs, files in os.walk("/tmp/flights"):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    flights = json.load(f)
                    for flight in flights:
                        total_records += 1
                        if any(val is None for val in flight.values()):
                            dirty_records += 1
                        destination_city = flight["destination_city"]
                        flight_durations.setdefault(destination_city, []).append(flight["flight_duration_secs"])
                        passengers_arrived[destination_city] = passengers_arrived.get(destination_city, 0) + (flight["passengers_on_board"] or 0)
                        passengers_left[flight["origin_city"]] = passengers_left.get(flight["origin_city"], 0) + (flight["passengers_on_board"] or 0)

    # Calculate AVG and P95 of flight duration for Top 25 destination cities
    top_cities = sorted(flight_durations, key=lambda city: len(flight_durations[city]), reverse=True)[:25]
    avg_flight_durations = {city: statistics.mean([x for x in flight_durations[city] if x is not None]) for city in top_cities}
    p95_flight_durations = {city: statistics.quantiles(flight_durations[city], n=20)[-1] for city in top_cities}

    # Find two cities with MAX passengers arrived and left
    max_arrived = sorted(passengers_arrived.items(), key=lambda x: x[1], reverse=True)[:2]
    max_left = sorted(passengers_left.items(), key=lambda x: x[1], reverse=True)[:2]

    logger.info("Analysis complete!")
    logger.info(f"Total records processed: {total_records}")
    logger.info(f"Dirty records: {dirty_records}")
    logger.info(f"Total run duration: {time.time() - start_time:.2f} seconds")
    logger.info("AVG flight duration for Top 25 destination cities:")
    for city, avg in avg_flight_durations.items():
        logger.info(f"  {city}: {avg:.2f} seconds")
    logger.info("P95 flight duration for Top 25 destination cities:")
    for city, p95 in p95_flight_durations.items():
        logger.info(f"  {city}: {p95:.2f} seconds")
    logger.info("Cities with MAX passengers arrived:")
    for city, passengers in max_arrived:
        logger.info(f"  {city}: {passengers} passengers")
    logger.info("Cities with MAX passengers left:")
    for city, passengers in max_left:
        logger.info(f"  {city}: {passengers} passengers")

if __name__ == "__main__":
    generate_flights()
    analyze_flights()