import random
import time
from dbconnect import connection

def generate_data():
    """Generate random sensor data."""
    temperature = round(random.uniform(0, 50), 2)  # Temperature in Celsius
    pressure = round(random.uniform(900, 1100), 2)  # Pressure in hPa
    depth = round(random.uniform(0, 500), 2)  # Depth in meters
    leak = random.choice(["Yes", "No"])  # Leak status
    
    return {
        "temperature": temperature,
        "pressure": pressure,
        "depth": depth,
        "leak": leak,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")  # Human-readable timestamp
    }

def main():
    collection = connection("sensors")  # Connecting to MongoDB collection
    max_entries = 500  # Maximum number of data points
    
    for _ in range(max_entries):
        data = generate_data()
        collection.insert_one(data)  # Insert data into MongoDB
        print(f"Inserted: {data}")
        time.sleep(1)  # Wait for 1 second

if __name__ == "__main__":
    main()
