# scripts/chat_to_md.py
import json
import os
import sys
from datetime import datetime

def convert_chat_to_markdown(chat_export_data: dict, output_dir: str):
    """
    Converts a single chat export dictionary into a markdown file.
    """
    chat_id = chat_export_data.get("id", "unknown_id")
    title = chat_export_data.get("title", f"Chat Export {chat_id}")
    
    # Sanitize title for filename
    filename = "".join(c for c in title if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()
    filename = filename.replace(" ", "_") + ".md"
    
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"**Chat ID:** `{chat_id}`\n")
        
        created_at_ts = chat_export_data.get("created_at")
        if created_at_ts:
            f.write(f"**Created At:** {datetime.fromtimestamp(created_at_ts / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        updated_at_ts = chat_export_data.get("updated_at")
        if updated_at_ts:
            f.write(f"**Updated At:** {datetime.fromtimestamp(updated_at_ts / 1000).strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        f.write("\n## Chat History\n\n")

        messages_map = chat_export_data.get("chat", {}).get("history", {}).get("messages", {})
        
        # Convert message map to a list and sort by timestamp if available
        # Assuming 'timestamp' is available in each message object
        sorted_messages = []
        for msg_id, message in messages_map.items():
            message['msg_id_key'] = msg_id # Store the key for later reference if needed
            sorted_messages.append(message)
        
        # Sort by timestamp, if not present, fall back to message ID (which is a UUID, so not truly chronological)
        try:
            sorted_messages.sort(key=lambda x: x.get("timestamp", 0))
        except TypeError: # Fallback if some timestamps are missing or invalid
            pass # Keep original order if sorting fails

        for message in sorted_messages:
            role = message.get("role", "unknown").capitalize()
            content = message.get("content", "")
            
            f.write(f"### {role}:\n")
            f.write(f"{content}\n\n")

            if message.get("files"):
                f.write("#### Attached Files:\n")
                for file_info in message["files"]:
                    file_name = file_info.get("name", "Unknown File")
                    file_url = file_info.get("url", "#")
                    f.write(f"- [{file_name}]({file_url})\n")
                f.write("\n")
    print(f"Generated markdown for '{title}' at '{filepath}'")

def process_chat_exports(json_filepath: str, output_dir: str):
    """
    Reads a JSON file containing an array of chat exports and converts each to a markdown file.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(json_filepath, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if isinstance(json_data, dict) and 'data' in json_data:
        chat_exports = json_data['data']
    else:
        chat_exports = json_data

    if not isinstance(chat_exports, list):
        print("Warning: JSON file does not contain a list of chat exports. Attempting to process as a single export.")
        chat_exports = [chat_exports]

    for chat_export in chat_exports:
        convert_chat_to_markdown(chat_export, output_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 chat_to_md.py <json_filepath> <output_dir>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_folder = sys.argv[2]
    process_chat_exports(json_file, output_folder)
