import random
import time
from db import get_connection



ASSETS = [f"DRONE_{i:03d}" for i in range(1, 21)]  #20 drones

def generate_telemetry(asset_id):
    return {
        "asset_id": asset_id,
        "asset_type": "USAS",
        "battery": random.randint(5, 100),  # Battery percentage
        "altitude": random.uniform(50, 500),  # Altitude in meters
        "speed": random.uniform(0, 100),  # Speed in km/h
        "gps_status": random.choice(["GOOD","GOOD", "GOOD", "WEAK", "LOST"]),
        "comms_status": random.choice(["ONLINE", "ONLINE", "ONLINE", "DEGRADED", "OFFLINE"]),
        "temperature": random.uniform(20, 95),  # Temperature in Celsius
    }

def insert_telemetry(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO telemetry (asset_id, asset_type, battery, altitude, speed, gps_status, comms_status, temperature)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["asset_id"],
        data["asset_type"],
        data["battery"],
        data["altitude"],
        data["speed"],
        data["gps_status"],
        data["comms_status"],
        data["temperature"]
    ))
    conn.commit()
    cursor.close()
    conn.close()

def main():
    while True:
        for asset in ASSETS:
            data = generate_telemetry(asset)
            insert_telemetry(data)
            print(f"Inserted telemetry: {data}")
            time.sleep(5)
            
if __name__ == "__main__":
    main()