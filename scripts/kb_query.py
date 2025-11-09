import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
import torch
import networkx as nx # Import networkx for graph building
import matplotlib.pyplot as plt # Import matplotlib for drawing

# Import functions from kb_visualize.py
from kb_visualize import build_knowledge_graph, draw_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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

def get_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Loads the SentenceTransformer model."""
    try:
        model = SentenceTransformer(model_name)
        # Ensure model is on CPU as per optimization for i7-5600U
        model.to("cpu")
        return model
    except Exception as e:
        logger.error(f"Error loading SentenceTransformer model '{model_name}': {e}")
        raise

def search_knowledge_base(
    query: str,
    vector_data: Dict[str, Any],
    model: SentenceTransformer,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Searches the knowledge base for documents semantically similar to the query.
    """
    if not query or not vector_data:
        return []

    logger.info(f"Encoding query: '{query}'")
    query_embedding = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)

    corpus_embeddings = []
    corpus_ids = []
    for doc_id, data in vector_data.items():
        corpus_ids.append(doc_id)
        corpus_embeddings.append(torch.tensor(data["embedding"]))

    if not corpus_embeddings:
        logger.warning("No document embeddings found in vector data.")
        return []

    corpus_embeddings = torch.stack(corpus_embeddings).to("cpu") # Ensure on CPU

    logger.info("Calculating cosine similarities...")
    cosine_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]

    # Sort by score in descending order
    top_results = torch.topk(cosine_scores, k=min(top_n, len(cosine_scores)))

    results = []
    for score, idx in zip(top_results[0], top_results[1]):
        doc_id = corpus_ids[idx]
        results.append({"file_path": doc_id, "score": score.item()})

    return results

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Interactive semantic search for the knowledge base."
    )
    parser.add_argument(
        "--top_n", type=int, default=5, help="Number of top results to return for each query."
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Generate a graph visualization of the search results."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="search_graph.png",
        help="Output file name for the visualization if --visualize is used.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    kb_root = script_dir.parent.resolve()
    vectors_path = script_dir / "vectors.json"

    vector_data = load_vector_data(vectors_path)
    if not vector_data:
        logger.error("Exiting: Could not load vector data.")
        return

    model = get_model()
    logger.info("Knowledge base search ready. Type 'exit' or 'quit' to stop.")

    while True:
        query = input("\nEnter your query (or 'exit'/'quit' to stop): ").strip()
        if query.lower() in ["exit", "quit"]:
            break

        if not query:
            print("Query cannot be empty. Please try again.")
            continue

        results = search_knowledge_base(query, vector_data, model, args.top_n)

        if results:
            print("\n--- Search Results ---")
            highlighted_nodes = []
            for r in results:
                print(f"Score: {r['score']:.4f} - File: {r['file_path']}")
                highlighted_nodes.append(r['file_path'])
            
            if args.visualize:
                logger.info(f"Generating visualization to {args.output_file} with highlighted results.")
                graph = build_knowledge_graph(kb_root, vector_data)
                draw_graph(graph, script_dir / args.output_file, highlighted_nodes)
                print(f"Visualization saved to {script_dir / args.output_file}")

        else:
            print("No relevant documents found.")

if __name__ == "__main__":
    main()
