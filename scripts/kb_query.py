import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
import torch

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
        description="Search the knowledge base using semantic similarity."
    )
    parser.add_argument("query", type=str, help="The natural language query to search for.")
    parser.add_argument(
        "--top_n", type=int, default=5, help="Number of top results to return."
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    vectors_path = script_dir / "vectors.json"

    vector_data = load_vector_data(vectors_path)
    if not vector_data:
        logger.error("Exiting: Could not load vector data.")
        return

    model = get_model()

    results = search_knowledge_base(args.query, vector_data, model, args.top_n)

    if results:
        print("\n--- Search Results ---")
        for r in results:
            print(f"Score: {r['score']:.4f} - File: {r['file_path']}")
    else:
        print("No relevant documents found.")

if __name__ == "__main__":
    main()
