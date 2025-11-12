import re
import os

# Read the content of 00 Index.md from the file system
index_file_path = "/home/odin/Documents/Vaults/ciel-kb/ciel-kb/40-Summary-Notes/00 Index.md"
try:
    with open(index_file_path, "r", encoding="utf-8") as f:
        index_content = f.read()
except FileNotFoundError:
    print(f"Error: {index_file_path} not found.")
    exit(1)
except Exception as e:
    print(f"Error reading {index_file_path}: {e}")
    exit(1)

# Debug: Print raw index_content
print("--- Raw Index Content ---")
print(index_content)
print("-------------------------")

# Extract links from the index content using a simpler regex
links = re.findall(r'\[\[.*\]\]', index_content) # Simpler regex
print("\n--- Extracted Links ---")
print(links)
print("-----------------------")
