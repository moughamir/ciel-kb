import os
import json
from sentence_transformers import SentenceTransformer

def find_markdown_files(root_dir):
    """Find all markdown files in a directory."""
    markdown_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                # Exclude files in .obsidian directory
                if ".obsidian" not in root:
                    markdown_files.append(os.path.join(root, file))
    return markdown_files

def read_file_content(file_path):
    """Read the content of a file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def generate_embedding(text, model):
    """Generate a vector embedding for a text."""
    return model.encode(text).tolist()

def main():
    """Main function to generate vector data."""
    # Load the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Find all markdown files in the knowledge base
    kb_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    markdown_files = find_markdown_files(kb_root)

    # Generate and store embeddings
    vector_data = {}
    for file_path in markdown_files:
        content = read_file_content(file_path)
        embedding = generate_embedding(content, model)
        relative_path = os.path.relpath(file_path, kb_root)
        vector_data[relative_path] = embedding

    # Save the vector data to a JSON file
    output_path = os.path.join(kb_root, "scripts", "vectors.json")
    with open(output_path, "w") as f:
        json.dump(vector_data, f, indent=4)

    print(f"Vector data generated for {len(markdown_files)} files and saved to {output_path}")

if __name__ == "__main__":
    main()