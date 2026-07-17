#!/bin/bash

cd ~/mission-ops-dashboard

echo "Starting docker containers..."
docker compose up -d

echo "Waiting for PostgreSQL to load..."
until docker exec mission_postgres pg_isready -U mission_user > /dev/null 2>&1
do
    sleep 2
done

cd app
source ../.venv/bin/activate

cleanup() {
    echo "Stopping services..."
    pkill -f telemetry_generator.py
    pkill -f alert_engine.py
    docker compose down
    
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting telemetry generator..."
python telemetry_generator.py &

echo "Starting alert engine..."
python alert_engine.py &

echo "All services are running."
echo "Press Ctrl+C to stop."

wait

