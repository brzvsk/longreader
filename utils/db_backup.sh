#!/bin/bash

# CONFIGURATION
BACKUP_DIR="/root/longreader/mongo_backups"
DB_NAME="longreader"
SPACE_NAME="longreader-backups"
SPACE_REGION="fra1"
DAYS_TO_KEEP=7
S3_ENDPOINT="https://fra1.digitaloceanspaces.com"

# TIMESTAMP
DATE=$(date +"%Y-%m-%d")

# Create MongoDB Backup
echo "[INFO] Creating MongoDB backup..."
mongodump --host localhost --port 27017 --db $DB_NAME --out $BACKUP_DIR/backup_$DATE
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create MongoDB backup!"
    exit 1
fi

# Compress the Backup
echo "[INFO] Compressing backup..."
tar -czvf $BACKUP_DIR/longreader_$DATE.tar.gz -C $BACKUP_DIR backup_$DATE
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to compress the backup!"
    exit 1
fi

# Remove Uncompressed Backup Folder
rm -rf $BACKUP_DIR/backup_$DATE

# Upload to DigitalOcean Spaces
echo "[INFO] Uploading to DigitalOcean Spaces..."
aws --profile do-spaces --endpoint-url $S3_ENDPOINT s3 cp $BACKUP_DIR/longreader_$DATE.tar.gz s3://$SPACE_NAME/
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to upload the backup to DigitalOcean Spaces!"
    exit 1
fi

# Delete Old Backups Locally
echo "[INFO] Cleaning up local backups older than $DAYS_TO_KEEP days..."
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +$DAYS_TO_KEEP -exec rm {} \;
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to delete old local backups!"
    exit 1
fi

echo "[SUCCESS] Backup process completed!"