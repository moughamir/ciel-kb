import os
import re
import json
from pathlib import Path
import yaml
from datetime import date

# --- LLM Simulation (Replace with actual LLM API call) ---
def generate_llm_suggestions(content: str) -> dict:
    """
    Simulates an LLM call to generate tags, topics, and category.
    In a real scenario, this would involve an API call to a large language model.
    """
    # Placeholder logic: In a real scenario, the LLM would analyze 'content'
    # and return relevant suggestions.
    
    # For demonstration, let's make some dummy suggestions based on keywords
    suggested_tags = []
    suggested_topics = []
    suggested_category = "Uncategorized"

    if "Cognitive Internet Project" in content:
        suggested_tags.append("CognitiveInternet")
        suggested_topics.append("Cognitive Internet Project")
        suggested_category = "Project"
    if "Arch Linux" in content:
        suggested_tags.append("Linux")
        suggested_topics.append("Arch Linux")
        suggested_category = "OperatingSystem"
    if "Tinder" in content:
        suggested_tags.append("Dating")
        suggested_topics.append("Social Media Profile")
        suggested_category = "Personal"
    if "Python" in content:
        suggested_tags.append("Programming")
        suggested_topics.append("Python Development")
        suggested_category = "SoftwareDevelopment"
    
    if not suggested_tags:
        suggested_tags.append("general")
    if not suggested_topics:
        suggested_topics.append("General Notes")

    return {
        "tags": list(set(suggested_tags)), # Remove duplicates
        "topics": list(set(suggested_topics)),
        "category": suggested_category
    }
# --- End LLM Simulation ---

def get_all_markdown_files(root_dir: Path) -> list[Path]:
    """Recursively get all markdown files in the root_dir."""
    return list(root_dir.rglob("*.md"))

def filter_markdown_files(files: list[Path], root_dir: Path) -> list[Path]:
    """Filter out template, archive, and other irrelevant markdown files."""
    excluded_paths = [
        root_dir / "99-Templates",
        root_dir / "31-Archive",
        root_dir / "GEMINI.md",
        root_dir / "repomix-index.md",
        root_dir / "Organizing Your Linux Home Directory.md",
        root_dir / "Excalidraw", # Exclude all Excalidraw files
    ]

    filtered_files = []
    for file_path in files:
        is_excluded = False
        for excluded_path in excluded_paths:
            # Check if the file_path is within an excluded directory or is an excluded file
            try:
                file_path.relative_to(excluded_path)
                is_excluded = True
                break
            except ValueError:
                # file_path is not a subpath of excluded_path
                pass
            if file_path == excluded_path:
                is_excluded = True
                break
        if not is_excluded:
            filtered_files.append(file_path)
    return filtered_files

def read_note_content(file_path: Path) -> str:
    """Reads the content of a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extracts YAML frontmatter and content from a markdown string."""
    frontmatter = {}
    body = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            try:
                # Use safe_load to prevent arbitrary code execution
                loaded_frontmatter = yaml.safe_load(parts[1])
                if isinstance(loaded_frontmatter, dict):
                    frontmatter = loaded_frontmatter
                body = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"Error parsing YAML frontmatter: {e}")
    return frontmatter, body

def get_first_h1_heading(content: str) -> str | None:
    """Extracts the first H1 heading from markdown content."""
    match = re.search(r'^#\s+(.*)', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def sanitize_filename(name: str) -> str:
    """Sanitizes a string to be a valid filename."""
    name = re.sub(r'[^\w\s.-]', '', name) # Allow alphanumeric, spaces, hyphens, periods
    name = re.sub(r'\s+', '_', name)     # Replace spaces with underscores
    name = name.strip()
    if not name: # Ensure filename is not empty
        return "untitled"
    return name

def convert_dates_to_strings(obj):
    """Recursively converts date objects in a dictionary to ISO format strings."""
    if isinstance(obj, dict):
        return {k: convert_dates_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_to_strings(elem) for elem in obj]
    elif isinstance(obj, date):
        return obj.isoformat()
    return obj

def process_note(file_path: Path, root_dir: Path, dry_run: bool = True):
    """Processes a single note for renaming, tagging, and categorization."""
    original_content = read_note_content(file_path)
    original_frontmatter, body = extract_frontmatter(original_content)

    # Determine primary topic/new filename
    h1_heading = get_first_h1_heading(body)
    current_filename_stem = file_path.stem
    
    new_title = h1_heading if h1_heading else current_filename_stem
    new_filename_stem = sanitize_filename(new_title)

    # Generate LLM suggestions
    llm_suggestions = generate_llm_suggestions(original_content)
    suggested_tags = llm_suggestions.get("tags", [])
    suggested_topics = llm_suggestions.get("topics", [])
    suggested_category = llm_suggestions.get("category", "Uncategorized")

    # Merge/update frontmatter
    updated_frontmatter = original_frontmatter.copy()
    
    # Handle 'tags'
    current_tags = updated_frontmatter.get('tags', [])
    if not isinstance(current_tags, list):
        current_tags = [current_tags]
    for tag in suggested_tags:
        if tag not in current_tags:
            current_tags.append(tag)
    updated_frontmatter['tags'] = sorted(list(set(current_tags))) # Ensure unique and sorted

    # Handle 'topics'
    current_topics = updated_frontmatter.get('topics', [])
    if not isinstance(current_topics, list):
        current_topics = [current_topics]
    for topic in suggested_topics:
        if topic not in current_topics:
            current_topics.append(topic)
    updated_frontmatter['topics'] = sorted(list(set(current_topics))) # Ensure unique and sorted

    # Handle 'category'
    if 'category' not in updated_frontmatter or updated_frontmatter['category'] == "Uncategorized":
        updated_frontmatter['category'] = suggested_category
    
    # Construct new content
    new_frontmatter_str = ""
    if updated_frontmatter:
        # Use default_flow_style=False for block style YAML
        new_frontmatter_str = "---" + "\n" + yaml.dump(updated_frontmatter, sort_keys=False, allow_unicode=True, default_flow_style=False) + "---" + "\n"
    
    new_content = new_frontmatter_str + body

    # Report changes
    relative_path = file_path.relative_to(root_dir)
    new_relative_path = relative_path.parent / f"{new_filename_stem}.md"

    print(f"--- Processing: {relative_path} ---")
    if new_filename_stem != current_filename_stem:
        print(f"  Proposed Rename: {relative_path} -> {new_relative_path}")
    else:
        print(f"  No Rename Proposed.")
    
    # Convert dates to strings for JSON serialization in print output
    printable_original_frontmatter = convert_dates_to_strings(original_frontmatter)
    printable_updated_frontmatter = convert_dates_to_strings(updated_frontmatter)

    print(f"  Original Frontmatter: {json.dumps(printable_original_frontmatter)}")
    print(f"  Updated Frontmatter: {json.dumps(printable_updated_frontmatter)}")
    print(f"  Proposed Content (first 200 chars):\n{new_content[:200]}...")
    print("-" * 50)

    if not dry_run:
        # Implement actual file operations here
        # Rename file if necessary
        if new_filename_stem != current_filename_stem:
            new_file_path = file_path.parent / f"{new_filename_stem}.md"
            os.rename(file_path, new_file_path)
            print(f"  Renamed: {file_path.name} to {new_file_path.name}")
            file_path = new_file_path # Update file_path for content writing

        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  Updated content for {file_path.name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Process Obsidian notes for renaming, tagging, and categorization."
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True,
        help="Simulate changes without writing to disk (default: True)."
    )
    parser.add_argument(
        "--no-dry-run", action="store_false", dest="dry_run",
        help="Apply changes and write to disk."
    )
    args = parser.parse_args()

    current_dir = Path(__file__).parent
    root_dir = current_dir.parent # Assuming the script is in 'scripts/' and vault root is its parent

    all_md_files = get_all_markdown_files(root_dir)
    processable_files = filter_markdown_files(all_md_files, root_dir)

    print(f"Found {len(all_md_files)} total markdown files.")
    print(f"Will process {len(processable_files)} files after filtering.\n")

    for file_path in processable_files:
        process_note(file_path, root_dir, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
