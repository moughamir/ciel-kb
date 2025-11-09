"""
Optimized cross-platform vector embedding generator for knowledge bases.
Tuned for low-power dual-core CPUs (Intel i7-5600U and similar).
"""

import os
import json
import logging
import hashlib
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

# Lazy imports for hardware detection
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available - using fallback hardware detection")

from sentence_transformers import SentenceTransformer
import torch

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class HardwareConfig:
    """Hardware configuration for optimal embedding generation."""

    cpu_count: int
    memory_gb: float
    workers: int
    batch_size: int
    device: str

    def __str__(self) -> str:
        return (
            f"Hardware Config:\n"
            f"  CPU Cores: {self.cpu_count}\n"
            f"  Memory: {self.memory_gb:.1f} GB\n"
            f"  Workers: {self.workers}\n"
            f"  Batch Size: {self.batch_size}\n"
            f"  Device: {self.device}"
        )


def detect_hardware() -> HardwareConfig:
    """
    Detect system hardware and calculate optimal processing configuration.
    Optimized for dual-core mobile CPUs.
    """
    # Detect CPU count
    try:
        if PSUTIL_AVAILABLE:
            cpu_count = psutil.cpu_count(logical=False) or os.cpu_count() or 2
        else:
            cpu_count = os.cpu_count() or 2
    except Exception as e:
        logger.warning(f"CPU detection failed: {e}. Using fallback: 2 cores")
        cpu_count = 2

    # Detect memory
    try:
        if PSUTIL_AVAILABLE:
            memory_bytes = psutil.virtual_memory().total
            memory_gb = memory_bytes / (1024**3)
        else:
            memory_gb = 4.0
            logger.warning("Memory detection unavailable. Using fallback: 4 GB")
    except Exception as e:
        logger.warning(f"Memory detection failed: {e}. Using fallback: 4 GB")
        memory_gb = 4.0

    # Detect CUDA availability
    try:
        cuda_available = torch.cuda.is_available()
        device = "cuda" if cuda_available else "cpu"
    except Exception:
        device = "cpu"

    # Optimize for dual-core CPUs (hyperthreading doesn't help compute-bound tasks)
    if cpu_count <= 2:
        workers = 1  # Single worker, avoid context switching
    elif cpu_count <= 4:
        workers = 2
    else:
        workers = min(4, cpu_count // 2)

    # Conservative batch size for low-power CPUs
    if device == "cuda":
        try:
            gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            batch_size = min(64, max(8, int(gpu_memory_gb * 4)))
        except Exception:
            batch_size = 32
    else:
        # Smaller batches for mobile CPUs: 2-8 range
        batch_size = min(8, max(2, int(memory_gb * 0.25)))

    config = HardwareConfig(
        cpu_count=cpu_count,
        memory_gb=memory_gb,
        workers=workers,
        batch_size=batch_size,
        device=device,
    )

    logger.info(f"\n{config}")
    return config


def compute_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a file using chunked reading."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to hash {file_path}: {e}")
        return ""


def find_markdown_files(
    root_dir: Path, exclude_dirs: Optional[List[str]] = None
) -> List[Path]:
    """Find all markdown files, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = [".obsidian", ".git", "node_modules", "__pycache__", "venv"]

    markdown_files = []
    try:
        for item in root_dir.rglob("*.md"):
            if not any(excluded in item.parts for excluded in exclude_dirs):
                markdown_files.append(item)

        logger.info(f"Found {len(markdown_files)} markdown files")
        return markdown_files

    except Exception as e:
        logger.error(f"Error scanning directory {root_dir}: {e}")
        return []


def read_file_safe(file_path: Path) -> Optional[str]:
    """Safely read file content with multiple encoding attempts."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None

    logger.warning(f"Could not decode {file_path} with any encoding")
    return None


def main():
    """Main function to generate vector embeddings."""

    logger.info("=== Vector Embedding Generator ===")

    # Detect hardware and configure
    hw_config = detect_hardware()

    # Optimize threading for Intel CPUs
    os.environ["MKL_NUM_THREADS"] = str(hw_config.workers)
    os.environ["OMP_NUM_THREADS"] = str(hw_config.workers)
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Prevent OpenMP conflicts
    torch.set_num_threads(hw_config.workers)

    # Define paths
    script_dir = Path(__file__).parent
    kb_root = script_dir.parent.resolve()
    output_path = script_dir / "vectors.json"

    logger.info(f"Knowledge base root: {kb_root}")

    # Find markdown files
    markdown_files = find_markdown_files(kb_root)

    if not markdown_files:
        logger.error("No markdown files found!")
        return

    # Load model
    model_name = "all-MiniLM-L6-v2"
    logger.info(f"Loading model: {model_name}")

    try:
        model = SentenceTransformer(model_name)
        if hw_config.device == "cuda":
            model = model.to("cuda")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return

    # Process files sequentially (best for dual-core)
    vector_data = {}
    failed_files = []

    logger.info(f"Processing {len(markdown_files)} files...")

    for idx, file_path in enumerate(markdown_files, 1):
        try:
            content = read_file_safe(file_path)
            if content is None:
                failed_files.append(file_path)
                continue

            # Generate embedding
            embedding = model.encode(
                content,
                batch_size=hw_config.batch_size,
                show_progress_bar=False,
                convert_to_tensor=False,
                normalize_embeddings=True,
            )

            # Store results
            rel_path = str(file_path.relative_to(kb_root))
            file_hash = compute_file_hash(file_path)

            vector_data[rel_path] = {
                "embedding": embedding.tolist(),
                "hash": file_hash,
                "size_bytes": file_path.stat().st_size,
            }

            # Progress logging every 10 files
            if idx % 10 == 0 or idx == len(markdown_files):
                logger.info(f"Progress: {idx}/{len(markdown_files)} files")

        except Exception as e:
            logger.error(f"Failed to process {file_path}: {e}")
            failed_files.append(file_path)

    # Save results
    logger.info(f"Saving embeddings to {output_path}")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(vector_data, f, indent=2)

        logger.info(f"\n=== Summary ===")
        logger.info(f"Successfully processed: {len(vector_data)} files")
        logger.info(f"Failed: {len(failed_files)} files")
        logger.info(f"Output: {output_path}")

        if failed_files:
            logger.warning(f"Failed files: {[str(f) for f in failed_files[:5]]}")

    except Exception as e:
        logger.error(f"Failed to save results: {e}")


if __name__ == "__main__":
    main()
