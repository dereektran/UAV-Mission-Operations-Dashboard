import time
import random
from db import get_connection

#list of operators that will be assigned to a task
OPERATORS = ["Operator_A", "Operator_B", "Operator_C", "Operator_D"]

#Function for creating alerts when telemetry thresholds are exceeded (Note: High & Critical alerts will automatically become incidents)
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

#Function for recording and logging the initial operator action
def create_incident(alert_id, asset_id, severity, alert_type, description):
    conn = get_connection()
    cursor = conn.cursor()

    #Critical incidents are immediately assigned to supervisor while any other incidents will be assigned to an operator from the list of operators
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

#Function determines the fleet readiness based on these factors: battery lvl, GPS, Comms, and temp
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

#Function for loggin significant mission events for operational awareness
def create_mission_event(asset_id, battery, gps_status, comms_status):
    conn = get_connection()
    cursor = conn.cursor()

    mission_id = "MISSION_ALPHA"

    #Determine which mission event occurred
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

#Function for escalating incidents that are unresolved
def escalate_old_incidents():
    conn = get_connection()
    cursor = conn.cursor()

    #Escalate incidents older than 15 minutes
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

#Function used to simulate operators resolving incidents (made it to where ~20% of incidents are automatically resolved)
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

#Function for processing the most recent telemetry record for each asset in the fleet
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

    #Evaluate each asset independently
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
    #One monitoring cyle is executed every 10 seconds
    while True:
        print("Checking telemetry for alerts, incidents, readiness, and mission_events...")
        check_latest_telemetry()
        escalate_old_incidents()
        auto_resolve_some_incidents()
        time.sleep(10)

if __name__ == "__main__":
    main()
