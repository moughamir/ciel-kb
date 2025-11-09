#!/bin/bash

# --- Configuration ---
INCOMING_JSON_DIR="/home/odin/Documents/Vaults/ciel-kb/ciel-kb/attachements"
PROCESSED_JSON_DIR="/home/odin/Documents/Vaults/ciel-kb/ciel-kb/attachements/processed_chats"
CHAT_TO_MD_SCRIPT="/home/odin/Documents/Vaults/ciel-kb/ciel-kb/scripts/chat_to_md.py"
MARKDOWN_OUTPUT_DIR="/home/odin/Documents/Vaults/ciel-kb/ciel-kb/00-Inbox/Chat Exports"
VENV_ACTIVATE="/home/odin/Documents/Vaults/ciel-kb/ciel-kb/scripts/venv/bin/activate"

LOG_FILE="/home/odin/Documents/Vaults/ciel-kb/ciel-kb/scripts/automate_chat_processing.log"

# Ensure log file exists
touch "$LOG_FILE"

# Function for logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "--- Starting Automated Chat Processing ---"

# Ensure processed directory exists
mkdir -p "$PROCESSED_JSON_DIR"

# Activate virtual environment
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
    log "Virtual environment activated."
else
    log "ERROR: Virtual environment activation script not found at $VENV_ACTIVATE. Exiting."
    exit 1
fi

# Find and process new JSON files
found_new_files=false
for json_file in "$INCOMING_JSON_DIR"/chat-export-*.json; do
    if [ -f "$json_file" ]; then
        filename=$(basename "$json_file")
        if [ ! -f "$PROCESSED_JSON_DIR/$filename" ]; then
            found_new_files=true
            log "Processing new chat export: $filename"
            
            # Run the Python script
            python3 "$CHAT_TO_MD_SCRIPT" "$json_file" "$MARKDOWN_OUTPUT_DIR" >> "$LOG_FILE" 2>&1
            
            if [ $? -eq 0 ]; then
                log "Successfully processed $filename. Moving to $PROCESSED_JSON_DIR."
                mv "$json_file" "$PROCESSED_JSON_DIR/"
            else
                log "ERROR: Failed to process $filename. Check log for details."
            fi
        else
            log "Skipping $filename: Already processed."
        fi
    fi
done

if ! $found_new_files; then
    log "No new chat export files found to process."
fi

# Deactivate virtual environment
deactivate
log "Virtual environment deactivated."
log "--- Automated Chat Processing Finished ---"
