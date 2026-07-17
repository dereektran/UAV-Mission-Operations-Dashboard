CREATE TABLE IF NOT EXISTS telemetry (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(50),
    asset_type VARCHAR(50),
    battery INTEGER,
    altitude INTEGER,
    speed INTEGER,
    gps_status VARCHAR(20),
    comms_status VARCHAR(20),
    temperature INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(50),
    severity VARCHAR(20),
    alert_type VARCHAR(50),
    message TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)