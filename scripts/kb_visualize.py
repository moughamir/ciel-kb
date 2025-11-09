import os
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import networkx as nx
from sentence_transformers import util
import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def find_markdown_files(
    root_dir: Path,
    exclude_dirs: Optional[List[str]] = None
) -> List[Path]:
    """Find all markdown files, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = [".obsidian", ".git", "node_modules", "__pycache__", "venv"]

    markdown_files = []
    try:
        for item in root_dir.rglob("*.md"):
            if not any(excluded in item.parts for excluded in exclude_dirs):
                markdown_files.append(item)

        logger.info(f"Found {len(markdown_files)} markdown files for visualization")
        return markdown_files

    except Exception as e:
        logger.error(f"Error scanning directory {root_dir}: {e}")
        return []

def parse_virtual_tags(file_path: Path) -> List[str]:
    """Parses a markdown file for [[virtual tags]]."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    tags = re.findall(r"\[\[(.*?)\]\]", content)
    return [tag.strip() for tag in tags if tag.strip()]

def load_vector_data(vectors_path: Path) -> Dict[str, Any]:
    """Loads the vector embeddings from the specified JSON file."""
    if not vectors_path.exists():
        logger.error(f"Vector data file not found: {vectors_path}")
        return {}
    try:
        with open(vectors_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading vector data from {vectors_path}: {e}")
        return {}

def build_knowledge_graph(
    kb_root: Path,
    vector_data: Dict[str, Any],
    similarity_threshold: float = 0.7,
) -> nx.Graph:
    """
    Builds a graph of the knowledge base, including explicit tags and semantic links.
    """
    G = nx.Graph()

    markdown_files = find_markdown_files(kb_root)
    file_paths_str = [str(f.relative_to(kb_root)) for f in markdown_files]

    # Add nodes for all markdown files
    for file_path_str in file_paths_str:
        G.add_node(file_path_str, type="document")

    # Add explicit links from virtual tags
    for file_path in markdown_files:
        rel_path_str = str(file_path.relative_to(kb_root))
        tags = parse_virtual_tags(file_path)
        for tag in tags:
            # Add tag as a node if it doesn't exist
            if tag not in G:
                G.add_node(tag, type="tag")
            # Add edge between document and tag
            G.add_edge(rel_path_str, tag, type="explicit_tag")

    # Add implicit links from semantic similarity
    doc_embeddings = []
    doc_paths_with_embeddings = []
    for doc_path, data in vector_data.items():
        if doc_path in file_paths_str: # Only consider files that actually exist
            doc_embeddings.append(torch.tensor(data["embedding"]))
            doc_paths_with_embeddings.append(doc_path)

    if doc_embeddings:
        corpus_embeddings = torch.stack(doc_embeddings).to("cpu")
        logger.info("Calculating pairwise semantic similarities...")
        # Compute cosine similarity between all pairs of embeddings
        cosine_scores = util.cos_sim(corpus_embeddings, corpus_embeddings)

        for i in range(len(doc_paths_with_embeddings)):
            for j in range(i + 1, len(doc_paths_with_embeddings)):
                score = cosine_scores[i][j].item()
                if score >= similarity_threshold:
                    G.add_edge(
                        doc_paths_with_embeddings[i],
                        doc_paths_with_embeddings[j],
                        type="semantic_link",
                        weight=score,
                    )
    else:
        logger.warning("No document embeddings available for semantic linking.")

    return G

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize the knowledge base as a graph."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Cosine similarity threshold for semantic links (0.0 to 1.0).",
    )
    parser.add_argument(
        "--output_format",
        type=str,
        default="text",
        choices=["text", "graphml"],
        help="Output format for the graph (text or graphml).",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    kb_root = script_dir.parent.resolve()
    vectors_path = script_dir / "vectors.json"

    vector_data = load_vector_data(vectors_path)
    if not vector_data:
        logger.warning("Proceeding without semantic links due to missing vector data.")

    graph = build_knowledge_graph(kb_root, vector_data, args.threshold)

    if args.output_format == "text":
        print("\n--- Knowledge Graph (Text Representation) ---")
        print(f"Nodes ({graph.number_of_nodes()}):")
        for node, data in graph.nodes(data=True):
            print(f"  - {node} (Type: {data.get('type', 'unknown')})")
        print(f"\nEdges ({graph.number_of_edges()}):")
        for u, v, data in graph.edges(data=True):
            link_type = data.get('type', 'unknown')
            weight_str = f", Weight: {data['weight']:.4f}" if 'weight' in data else ""
            print(f"  - {u} --({link_type}{weight_str})-- {v}")
    elif args.output_format == "graphml":
        output_file = script_dir / "knowledge_graph.graphml"
        nx.write_graphml(graph, output_file)
        print(f"\nKnowledge graph saved to {output_file}")

if __name__ == "__main__":
    main()
