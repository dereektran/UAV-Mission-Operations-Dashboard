import time
import random
from db import get_connection


OPERATORS = ["Operator_A", "Operator_B", "Operator_C", "Operator_D"]

def create_alert(asset_id, severity, alert_type, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (asset_id, severity, alert_type, message)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (asset_id, severity, alert_type, message))

    alert_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    if severity in ["CRITICAL", "HIGH"]:
        create_incident(alert_id, asset_id, severity, alert_type, message)

def create_incident(alert_id, asset_id, severity, alert_type, description):
    conn = get_connection()
    cursor = conn.cursor()

    owner = "Mission_Supervisor" if severity == "CRITICAL" else random.choice(OPERATORS)

    cursor.execute("""
        INSERT INTO incidents
        (alert_id, asset_id, severity, status, owner, incident_type, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        alert_id,
        asset_id,
        severity,
        "OPEN",
        owner,
        alert_type,
        description
    ))

    cursor.execute("""
        INSERT INTO operator_actions
        (operator_name, asset_id, action, notes)
        VALUES (%s, %s, %s, %s)
    """, (
        owner,
        asset_id,
        "ACKNOWLEDGE_ALERT",
        f"Incident created for {alert_type}"
    ))

    conn.commit()
    cursor.close()
    conn.close()

def update_asset_readiness(asset_id, battery, gps_status, comms_status, temperature):
    if battery < 20 or comms_status == "OFFLINE":
        readiness = "UNAVAILABLE"
    elif gps_status == "WEAK" or gps_status == "LOST" or comms_status == "DEGRADED" or temperature > 80:
        readiness = "DEGRADED"
    else:
        readiness = "READY"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO asset_readiness
        (asset_id, readiness_status, battery, gps_status, comms_status, temperature)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        asset_id,
        readiness,
        battery,
        gps_status,
        comms_status,
        temperature
    ))

    conn.commit()
    cursor.close()
    conn.close()

def create_mission_event(asset_id, battery, gps_status, comms_status):
    conn = get_connection()
    cursor = conn.cursor()

    mission_id = "MISSION_ALPHA"

    if battery < 20:
        event_type = "BATTERY_CRITICAL"
        description = f"{asset_id} battery criticaly low at {battery}%"
    elif comms_status == "OFFLINE":
        event_type = "COMMS_LOST"
        description = f"{asset_id} lost communications"
    elif gps_status == "LOST":
        event_type = "GPS_LOST"
        description = f"{asset_id} GPS signal lost"
    elif gps_status == "WEAK":
        event_type = "GPS_DEGRADED"
        description = f"{asset_id} GPS degraded"
    else:
        event_type = "WAYPOINT_REACHED"
        description = f"{asset_id} reached waypoint"

    cursor.execute("""
        INSERT INTO mission_events
        (mission_id, asset_id, event_type, description)
        VALUES (%s, %s, %s, %s)
    """, (
        mission_id,
        asset_id,
        event_type,
        description
    ))

    conn.commit()
    cursor.close()
    conn.close()

def escalate_old_incidents():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE incidents
        SET escalated = TRUE,
            status = 'ESCALATED'
        WHERE status = 'OPEN'
            AND escalated = FALSE
            AND created_at < NOW() - INTERVAL '15 minutes'
    """)

    cursor.execute("""
        INSERT INTO operator_actions
        (operator_name, asset_id, action, notes)
        SELECT
            'Mission_Control',
            asset_id,
            'ESCALATE_INCIDENT',
            'Incident escalated after 15 minutes'
        FROM incidents
        WHERE status = 'ESCALATED'
            AND escalated = TRUE
            AND created_at < NOW() - INTERVAL '15 minutes'
    """)

    conn.commit()
    cursor.close()
    conn.close()

def auto_resolve_some_incidents():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE incidents
        SET status = 'RESOLVED'
        WHERE status IN ('OPEN', 'ESCALATED')
            AND created_at < NOW() - INTERVAL '5 minutes'
            AND RANDOM() < 0.20
    """)

    conn.commit()
    cursor.close()
    conn.close()


def check_latest_telemetry():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT ON (asset_id)
            asset_id, battery, gps_status, comms_status, temperature
        FROM telemetry
        ORDER BY asset_id, timestamp DESC
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    for row in rows:
        asset_id, battery, gps_status, comms_status, temperature = row

        update_asset_readiness(asset_id, battery, gps_status, comms_status, temperature)
        create_mission_event(asset_id, battery, gps_status, comms_status)
        
        if battery < 20:
            create_alert(asset_id, "HIGH", "LOW_BATTERY", f"{asset_id}Battery at {battery}%")
        
        if gps_status == "LOST":
            create_alert(asset_id, "HIGH", "GPS_LOST", f"{asset_id} GPS status: {gps_status}")
        
        if comms_status == "OFFLINE":
            create_alert(asset_id, "CRITICAL", "COMMS_OFFLINE", f"{asset_id}Comms status: {comms_status}")
        
        if temperature > 80:
            create_alert(asset_id, "MEDIUM", "HIGH_TEMP", f"{asset_id} Temperature at {temperature}°C")


def main():
    while True:
        print("Checking telemetry for alerts, incidents, readiness, and mission_events...")
        check_latest_telemetry()
        escalate_old_incidents()
        auto_resolve_some_incidents()
        time.sleep(10)

if __name__ == "__main__":
    main()