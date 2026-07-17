# Mission Operations Monitoring & Incident Management Platform

## Overview

This project simulates a mission operations platform for monitoring a fleet of autonomous assets. It generates real-time telemetry, detects operational issues, creates alerts and incidents, tracks asset readiness, logs operator actions, and visualizes operational KPIs through Grafana dashboards.

The goal of this project is to model how technical operations, product operations, and mission operations teams monitor deployed systems and respond to incidents.

## Tech Stack

* Python
* PostgreSQL
* Docker / Docker Compose
* Grafana
* SQL
* Linux

## Features

* Simulated telemetry generation for 20 autonomous assets
* Real-time ingestion into PostgreSQL
* Automated alert detection for low battery, GPS loss, communications loss, and high temperature
* Incident creation for high-severity alerts
* Incident escalation and resolution tracking
* Fleet readiness classification: READY, DEGRADED, UNAVAILABLE
* Operator action logging
* Mission event timeline
* Grafana dashboards for operational monitoring

## Architecture

Telemetry Generator → PostgreSQL → Alert Engine → Incidents / Readiness / Mission Events → Grafana Dashboard

## Database Tables

* telemetry
* alerts
* incidents
* asset_readiness
* operator_actions
* mission_events

## Dashboard Panels

The Grafana dashboard includes:

* Fleet Readiness %
* Open Incidents
* Critical Incidents
* MTTR
* Readiness Distribution
* Battery Levels by Asset
* Incident Trend Over Time
* Incident Severity Breakdown
* Mission Timeline
* Operator Activity Feed

## How to Run

Clone the repository and start the full stack:

```bash
docker compose up -d
```

Open Grafana:

```text
http://localhost:3000
```

Default login:

```text
Username: admin
Password: admin
```

To stop the stack:

```bash
docker compose down
```

## What I Learned

This project helped me gain hands-on experience with containerized deployments, SQL database design, telemetry processing, alerting logic, incident management workflows, operational dashboards, and fleet readiness tracking.

## Future Improvements

* Add authentication and role-based access
* Add more realistic telemetry behavior
* Add historical incident reports
* Add automated notification workflows
* Deploy to a remote Linux server
* Add Kubernetes as an advanced deployment option
