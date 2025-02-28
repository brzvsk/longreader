#!/bin/bash

# Define the cron job
CRON_JOB="0 2 * * * /root/longreader/db_utils/db_backup.sh"

# Check if the cron job already exists
crontab -l 2>/dev/null | grep -F "$CRON_JOB" > /dev/null

if [[ $? -eq 0 ]]; then
    echo "[INFO] Cron job already exists. No changes made."
else
    # Add the new cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    if [[ $? -eq 0 ]]; then
        echo "[SUCCESS] Cron job added successfully!"
    else
        echo "[ERROR] Failed to add the cron job!"
        exit 1
    fi
fi