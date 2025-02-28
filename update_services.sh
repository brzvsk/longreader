#!/bin/bash

# update_services.sh - Script to update specified Docker Compose services
# Usage: ./update_services.sh [service1] [service2] ...

# Exit on any error
set -e

# Check if at least one service is specified
if [ $# -eq 0 ]; then
  echo "Error: No services specified."
  echo "Usage: ./update_services.sh [service1] [service2] ..."
  exit 1
fi

# Store the services as an array
SERVICES=("$@")

# Print the services that will be updated
echo "Updating the following services:"
for service in "${SERVICES[@]}"; do
  echo "- $service"
done

# Navigate to the project directory
cd /root/longreader

# Pull the latest images for the specified services
echo -e "\n=== Pulling latest images ==="
docker compose pull "${SERVICES[@]}"

# Stop the specified services
echo -e "\n=== Stopping services ==="
docker compose stop "${SERVICES[@]}"
docker compose rm -f "${SERVICES[@]}"

# Start the services with the new images
echo -e "\n=== Starting services with new images ==="
docker compose up -d "${SERVICES[@]}"

echo -e "\n=== Update completed successfully ===" 

# Check the status of the services
echo -e "\n=== Service status ==="
docker compose ps "${SERVICES[@]}"