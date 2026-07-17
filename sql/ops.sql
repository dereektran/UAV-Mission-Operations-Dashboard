CREATE TABLE IF NOT EXISTS incidents (
    indicident_id SERIAL PRIMARY KEY,
    alert_id INTEGER,
    asset_id VARCHAR(50),
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'Open',
    owner VARCHAR(50) DEFAULT 'Unassigned',
    incident_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    escalated BOOLEAN DEFAULT FALSE
);


CREATE TABLE IF NOT EXISTS asset_readiness (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(50),
    readiness_status VARCHAR(30),
    battery INTEGER,
    gps_status VARCHAR(20),
    comms_status VARCHAR(20),
    temperature INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS operator_actions (
    id SERIAL PRIMARY KEY,
    operator_name VARCHAR(50),
    asset_id VARCHAR(50),
    action VARCHAR(50),
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mission_events (
    id SERIAL PRIMARY KEY,
    mission_id VARCHAR(50),
    asset_id VARCHAR(50),
    event_type VARCHAR(50),
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);