import os

# Read the content of 00 Index.md from the file system
index_file_path = "/home/odin/Documents/Vaults/ciel-kb/ciel-kb/40-Summary-Notes/00 Index.md"
try:
    with open(index_file_path, "r", encoding="utf-8") as f:
        index_content = f.read() # Read the entire file
except FileNotFoundError:
    print(f"Error: {index_file_path} not found.")
    exit(1)
except Exception as e:
    print(f"Error reading {index_file_path}: {e}")
    exit(1)

# Debug: Print repr of raw index_content
print("--- Raw Index Content (repr) ---")
print(repr(index_content))
print("--------------------------------")

# Extract links using string manipulation
extracted_links_manual = []
start_index = 0
while True:
    start_bracket = index_content.find('[[', start_index)
    if start_bracket == -1:
        break
    end_bracket = index_content.find(']]', start_bracket + 2)
    if end_bracket == -1:
        break
    
    link_text = index_content[start_bracket + 2:end_bracket]
    extracted_links_manual.append(link_text)
    start_index = end_bracket + 2

print("\n--- Extracted Links (Manual String Manipulation) ---")
print(extracted_links_manual)
print("------------------------------------")

# Debug: Check for "Islamic Studies" in extracted_links_manual
print(f"Debug: 'Islamic Studies' in extracted_links_manual: {'Islamic Studies' in extracted_links_manual}")


# Construct expected filenames from extracted links
linked_files_in_index = {link + ".md" for link in extracted_links_manual}

# Debug: Print linked_files_in_index set
print("\n--- linked_files_in_index Set ---")
print(linked_files_in_index)
print("---------------------------------")


# Get actual files in the 40-Summary-Notes directory
summary_notes_dir = "/home/odin/Documents/Vaults/ciel-kb/ciel-kb/40-Summary-Notes"
all_actual_files = {f for f in os.listdir(summary_notes_dir) if f.endswith(".md")}

# Debug prints
print(f"Debug: linked_files_in_index count: {len(linked_files_in_index)}")
print(f"Debug: all_actual_files count: {len(all_actual_files)}")
print(f"Debug: 'Islamic Studies.md' in linked_files_in_index: {'Islamic Studies.md' in linked_files_in_index}")
print(f"Debug: 'Islamic Studies.md' in all_actual_files: {'Islamic Studies.md' in all_actual_files}")


# Identify missing files (linked in index but not found)
missing_files = linked_files_in_index - all_actual_files

# Identify unlinked files (found but not linked in index, excluding the index itself)
unlinked_files = all_actual_files - linked_files_in_index - {"00 Index.md"}

if not missing_files and not unlinked_files:
    print("Vault verification successful: All linked files exist and no unlinked files found.")
else:
    if missing_files:
        print("--- Missing Files (linked in 00 Index.md but not found in 40-Summary-Notes) ---")
        for f in sorted(list(missing_files)):
            print(f"- {f}")
    if unlinked_files:
        print("\n--- Unlinked Files (found in 40-Summary-Notes but not linked in 00 Index.md) ---")
        for f in sorted(list(unlinked_files)):
            print(f"- {f}")