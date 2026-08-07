# Mission Operations Monitoring & Incident Management Platform

## Overview

This project simulates a mission operations platform for monitoring a fleet of autonomous assets. It generates real-time telemetry, detects operational issues, creates alerts and incidents, tracks asset readiness, logs operator actions, and visualizes operational KPIs through Grafana dashboards.

The goal of this project is to model how an operations team monitor deployed systems and respond to incidents.

<img width="2170" height="1013" alt="image" src="https://github.com/user-attachments/assets/41424b79-d1f9-47b0-90b9-d7f4357be2bb" />

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
* Assets Requiring Immediate Attention
* Open Incidents
* Battery Levels by Asset
* Incident Status
* Incident Trend Over Time
* Assets with the Most Issues
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
## Optional: Secure Remote Access

Tailscale provides an encrypted overlay network that allows authorized devices to access the running Grafana dashboard from different networks without intentionally exposing Grafana directly to the public internet.

### Ubuntu Host

Install Tailscale:

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Check the connection and find the host's Tailscale IP:

```bash
tailscale status
tailscale ip -4
```

### Remote Device

Install Tailscale:

[Tailscale Download](https://tailscale.com/download)

After the remote device is authorized, access Grafana using:

```text
http://<TAILSCALE-IP>:3000
```

## What I Learned

Building this project helped me understand how raw telemetry can be transformed into actionable operational intelligence. Rather than simply collecting sensor data, I designed workflows that automatically evaluate asset health, generate alerts, create incidents, track fleet readiness, and visualize KPIs in real time. I also learned how to deploy a multi-service application using Docker so the entire stack could be started with a single command, eliminating manual dependency installation and ensuring the application runs consistently across different machines.
