#!/bin/bash

# CONFIGURATION
BACKUP_DIR="/root/longreader/mongo_backups"
DB_NAME="longreader"
SPACE_NAME="longreader-backups"
SPACE_REGION="fra1"
DAYS_TO_KEEP=7
S3_ENDPOINT="https://fra1.digitaloceanspaces.com"
LOG_FILE="/root/longreader/logs/backup_log.txt"

# TIMESTAMP FUNCTION
timestamp() {
    date +"%Y-%m-%dT%H:%M:%S"
}

# TIMESTAMPED LOGGING FUNCTION
log() {
    echo "[$(timestamp)] $1" | tee -a $LOG_FILE
}

# START BACKUP PROCESS
log "[INFO] Starting MongoDB backup..."

# Create MongoDB Backup
log "[INFO] Creating MongoDB backup..."
mongodump --host localhost --port 27017 --db $DB_NAME --out $BACKUP_DIR/backup_$(date +"%Y-%m-%d")
if [[ $? -ne 0 ]]; then
    log "[ERROR] MongoDB backup failed!"
    exit 1
fi

# Compress the Backup
log "[INFO] Compressing backup..."
tar -czvf $BACKUP_DIR/longreader_$(date +"%Y-%m-%d").tar.gz -C $BACKUP_DIR backup_$(date +"%Y-%m-%d")
if [[ $? -ne 0 ]]; then
    log "[ERROR] Backup compression failed!"
    exit 1
fi

# Remove Uncompressed Backup Folder
rm -rf $BACKUP_DIR/backup_$(date +"%Y-%m-%d")

# Upload to DigitalOcean Spaces
log "[INFO] Uploading to DigitalOcean Spaces..."
aws --profile do-spaces --endpoint-url $S3_ENDPOINT s3 cp $BACKUP_DIR/longreader_$(date +"%Y-%m-%d").tar.gz s3://$SPACE_NAME/
if [[ $? -ne 0 ]]; then
    log "[ERROR] Upload to DigitalOcean Spaces failed!"
    exit 1
fi

# Delete Old Backups Locally
log "[INFO] Cleaning up local backups older than $DAYS_TO_KEEP days..."
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +$DAYS_TO_KEEP -exec rm {} \;
if [[ $? -ne 0 ]]; then
    log "[ERROR] Failed to clean up old backups!"
    exit 1
fi

log "[SUCCESS] Backup process completed!"