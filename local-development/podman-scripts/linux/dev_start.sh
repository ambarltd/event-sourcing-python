#!/bin/bash
set -e

cd ../../
mkdir -p data/event-sourcing-event-bus data/event-sourcing-event-store/pg-data data/event-sourcing-projection-store/db-data data/event-sourcing-projection-store/db-config
podman compose down
podman compose up -d --build --force-recreate

all_services_fully_healthy() {
    ! podman compose ps --format "table {{.ID}}\t{{.Name}}\t{{.Status}}" | grep -q -E "(unhealthy|starting)"
}

while ! all_services_fully_healthy; do
    echo "Waiting for all services to be healthy..."
    podman compose ps --format "table {{.ID}}\t{{.Name}}\t{{.Status}}"
    echo ""
    sleep 5
done

podman compose ps --format "table {{.ID}}\t{{.Name}}\t{{.Status}}"

echo ""
echo "======================================================================="
echo "||                     All services are healthy!                     ||"
echo "======================================================================="
echo ""

echo "======================================================================="
echo "|| You can now run the dev_demo.sh script!                           ||"
echo "======================================================================="
echo "|| You can navigate to localhost:8080 to hit your backend.           ||"
echo "======================================================================="
echo "|| You can navigate to localhost:8081 to view your event store.      ||"
echo "======================================================================="
echo "|| You can navigate to localhost:8082 to view your projection store. ||"
echo "======================================================================="
