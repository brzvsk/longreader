#!/bin/bash

# CONFIGURATION
BACKUP_DIR="/root/longreader/mongo_backups"
DB_NAME="longreader"

# TIMESTAMP FUNCTION
timestamp() {
    date +"%Y-%m-%dT%H:%M:%S"
}


# CHECK IF ARGUMENT IS PROVIDED
if [[ -z "$1" ]]; then
    echo "[$(timestamp)] [ERROR] No backup file provided! Usage: ./restore_local.sh <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"

# CHECK IF FILE EXISTS
if [[ ! -f "$BACKUP_FILE" ]]; then
    echo "[$(timestamp)] [ERROR] Backup file $BACKUP_FILE does not exist!"
    exit 1
fi

echo "[$(timestamp)] [INFO] Restoring MongoDB from local backup: $BACKUP_FILE"

# EXTRACT BACKUP
echo "[$(timestamp)] [INFO] Extracting backup archive..."
tar -xzvf "$BACKUP_FILE" -C "$BACKUP_DIR"
if [[ $? -ne 0 ]]; then
    echo "[$(timestamp)] [ERROR] Failed to extract backup archive!"
    exit 1
fi

# FIND THE EXTRACTED FOLDER
EXTRACTED_DIR=$(tar -tzf "$BACKUP_FILE" | head -1 | cut -f1 -d"/")

if [[ -z "$EXTRACTED_DIR" ]]; then
    echo "[$(timestamp)] [ERROR] Could not determine extracted directory!"
    exit 1
fi

echo "[$(timestamp)] [INFO] Restoring MongoDB database..."
mongorestore --host localhost --port 27017 --drop --nsInclude="$DB_NAME.*" --dir="$BACKUP_DIR/$EXTRACTED_DIR/"