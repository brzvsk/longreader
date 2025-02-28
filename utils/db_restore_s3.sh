#!/bin/bash

# CONFIGURATION
BACKUP_DIR="/root/longreader/mongo_backups"

# DB configs

DB_NAME=""
DB_USERNAME=""
DB_PASSWORD=""
AUTH_DB=""

# S3 configs

SPACE_NAME="longreader-backups"
SPACE_REGION="fra1"
S3_ENDPOINT="https://$SPACE_REGION.digitaloceanspaces.com"

# TIMESTAMP FUNCTION
timestamp() {
    date +"%Y-%m-%dT%H:%M:%S"
}

# GET LIST OF BACKUPS FROM S3
echo "[$(timestamp)] [INFO] Fetching list of backups from DigitalOcean Spaces..."
BACKUP_LIST=$(aws --profile do-spaces --endpoint-url "$S3_ENDPOINT" s3 ls "s3://$SPACE_NAME/" --recursive | awk '{print $4}')

# CHECK IF BACKUP LIST IS EMPTY
if [[ -z "$BACKUP_LIST" ]]; then
    echo "[$(timestamp)] [ERROR] No backup files found in the Space!"
    exit 1
fi

# DISPLAY AVAILABLE BACKUPS
echo "[$(timestamp)] [INFO] Available backups:"
select BACKUP_FILE in $BACKUP_LIST; do
    if [[ -n "$BACKUP_FILE" ]]; then
        echo "[$(timestamp)] [INFO] You selected: $BACKUP_FILE"
        break
    else
        echo "[$(timestamp)] [ERROR] Invalid selection. Please choose a valid number."
    fi
done

# DOWNLOAD THE SELECTED BACKUP FROM S3
LOCAL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"
echo "[$(timestamp)] [INFO] Downloading backup from S3 Bucket: $BACKUP_FILE"
aws --profile do-spaces --endpoint-url "$S3_ENDPOINT" s3 cp "s3://$SPACE_NAME/$BACKUP_FILE" "$LOCAL_BACKUP_PATH"
if [[ $? -ne 0 ]]; then
    echo "[$(timestamp)] [ERROR] Failed to download backup from S3!"
    exit 1
fi

# EXTRACT BACKUP
echo "[$(timestamp)] [INFO] Extracting backup archive..."
tar -xzvf "$LOCAL_BACKUP_PATH" -C "$BACKUP_DIR"
if [[ $? -ne 0 ]]; then
    echo "[$(timestamp)] [ERROR] Failed to extract backup archive!"
    exit 1
fi

# FIND THE EXTRACTED FOLDER
EXTRACTED_DIR=$(tar -tzf "$LOCAL_BACKUP_PATH" | head -1 | cut -f1 -d"/")

if [[ -z "$EXTRACTED_DIR" ]]; then
    echo "[$(timestamp)] [ERROR] Could not determine extracted directory!"
    exit 1
fi

echo "[$(timestamp)] [INFO] Restoring MongoDB database..."
mongorestore --host localhost --port 27017 --username $DB_USERNAME --password $DB_PASSWORD --authenticationDatabase $AUTH_DB --drop --nsInclude="$DB_NAME.*" --dir="$BACKUP_DIR/$EXTRACTED_DIR/"
if [[ $? -ne 0 ]]; then
    echo "[$(timestamp)] [ERROR] MongoDB restore failed!"
    exit 1
fi