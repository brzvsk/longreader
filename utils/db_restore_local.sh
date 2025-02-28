#!/bin/bash

# CONFIGURATION
BACKUP_DIR="/root/longreader/mongo_backups"


# DB configs
DB_NAME=""
DB_USERNAME=""
DB_PASSWORD=""
AUTH_DB=""

# TIMESTAMP FUNCTION
timestamp() {
    date +"%Y-%m-%dT%H:%M:%S"
}

# LIST AVAILABLE BACKUP FILES
echo "[$(timestamp)] [INFO] Available backup files in $BACKUP_DIR:"
if [[ ! -d "$BACKUP_DIR" ]]; then
    echo "[$(timestamp)] [ERROR] Backup directory $BACKUP_DIR does not exist!"
    exit 1
fi

BACKUP_FILES=($(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null))
if [[ ${#BACKUP_FILES[@]} -eq 0 ]]; then
    echo "[$(timestamp)] [ERROR] No backup files found in $BACKUP_DIR!"
    exit 1
fi

for i in "${!BACKUP_FILES[@]}"; do
    echo "$((i + 1)). ${BACKUP_FILES[$i]}"
done

# PROMPT USER TO SELECT A BACKUP FILE
read -p "[$(timestamp)] [PROMPT] Enter the number of the backup file to restore: " FILE_INDEX
if ! [[ "$FILE_INDEX" =~ ^[0-9]+$ ]] || ((FILE_INDEX < 1 || FILE_INDEX > ${#BACKUP_FILES[@]})); then
    echo "[$(timestamp)] [ERROR] Invalid selection!"
    exit 1
fi

BACKUP_FILE="${BACKUP_FILES[$((FILE_INDEX - 1))]}"

# CONFIRM RESTORE OPERATION
read -p "[$(timestamp)] [PROMPT] Are you sure you want to restore the backup from $BACKUP_FILE? (yes/no): " CONFIRM
if [[ "$CONFIRM" != "yes" ]]; then
    echo "[$(timestamp)] [INFO] Restore operation cancelled."
    exit 0
fi

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
mongorestore --host localhost --port 27017 --username $DB_USERNAME --password $DB_PASSWORD --authenticationDatabase $AUTH_DB --drop --nsInclude="$DB_NAME.*" --dir="$BACKUP_DIR/$EXTRACTED_DIR/"