import os
import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import networkx as nx
from sentence_transformers import util
import torch
import matplotlib.pyplot as plt

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
    tags = re.findall(r"..\[(.*?) ..\]", content)
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
        cosine_scores_matrix = util.cos_sim(corpus_embeddings, corpus_embeddings)

        for i in range(len(doc_paths_with_embeddings)):
            for j in range(i + 1, len(doc_paths_with_embeddings)):
                score = cosine_scores_matrix[i][j].item()
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

def draw_graph(graph: nx.Graph, output_file: Path, highlighted_nodes: Optional[List[str]] = None):
    """Draws the graph and saves it to a file."""
    plt.figure(figsize=(16, 12)) # Increased figure size for better readability
    
    if highlighted_nodes is None:
        highlighted_nodes = []

    node_colors = []
    node_sizes = []
    for node in graph.nodes(data=True):
        if node[0] in highlighted_nodes:
            node_colors.append('gold') # Highlighted color
            node_sizes.append(1500) # Larger size for highlighted nodes
        elif node[1].get('type') == 'document':
            node_colors.append('skyblue')
            node_sizes.append(1000)
        elif node[1].get('type') == 'tag':
            node_colors.append('lightcoral')
            node_sizes.append(700)
        else:
            node_colors.append('lightgray')
            node_sizes.append(500)

    edge_colors = []
    edge_widths = []
    for u, v, data in graph.edges(data=True):
        if data.get('type') == 'explicit_tag':
            edge_colors.append('gray')
            edge_widths.append(0.5)
        elif data.get('type') == 'semantic_link':
            edge_colors.append('blue')
            edge_widths.append(data['weight'] * 3) # Scale width by similarity
        else:
            edge_colors.append('lightgray')
            edge_widths.append(0.2)

    pos = nx.spring_layout(graph, k=0.5, iterations=50) # Layout algorithm
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_edges(graph, pos, edge_color=edge_colors, width=edge_widths, alpha=0.7)
    nx.draw_networkx_labels(graph, pos, font_size=8, font_weight="bold")
    
    plt.title("Knowledge Graph Visualization")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close() # Close the plot to free memory

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
        choices=["text", "graphml", "png"],
        help="Output format for the graph (text, graphml, or png).",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="knowledge_graph.png",
        help="Output file name for graphml or png formats.",
    )
    parser.add_argument(
        "--highlight_nodes",
        nargs='*', # 0 or more arguments
        default=[],
        help="List of node IDs (file paths) to highlight in the visualization.",
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
        output_file = script_dir / args.output_file
        nx.write_graphml(graph, output_file)
        print(f"\nKnowledge graph saved to {output_file}")
    elif args.output_format == "png":
        output_file = script_dir / args.output_file
        draw_graph(graph, output_file, args.highlight_nodes)
        print(f"\nKnowledge graph visualization saved to {output_file}")

if __name__ == "__main__":
    main()
