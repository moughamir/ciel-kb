## Installation Instructions

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install CPU-optimized PyTorch first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
pip install -r requirements.txt
```

**Why these changes:**
- **Intel MKL**: Optimizes matrix operations for your CPU's AVX2 instructions
- **CPU-only PyTorch**: ~2GB smaller than CUDA version, faster load times
- **intel-openmp**: Better thread management for dual-core hyperthreaded CPUs

**Alternative (if MKL conflicts occur):**
Remove `mkl` and `intel-openmp` lines - PyTorch includes basic optimizations by default.
