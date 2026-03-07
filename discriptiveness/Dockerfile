# Use official Python slim image
FROM python:3.10-slim

# ---- Set cache directories FIRST ----
# All model downloads will go to /tmp/.cache (writable runtime disk)
ENV HF_HOME=/tmp/.cache/huggingface \
    TRANSFORMERS_CACHE=/tmp/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/tmp/.cache/sentence-transformers \
    SPACY_DATA=/tmp/.cache/spacy \
    NLTK_DATA=/tmp/.cache/nltk

# ---- Install system dependencies (if any) ----
# (none required for this project, but keep if needed)

# ---- Set working directory ----
WORKDIR /app

# ---- Copy requirements first (for Docker layer caching) ----
COPY requirements.txt .

# ---- Install Python dependencies ----
# This does NOT download any models (spacy model is NOT downloaded here)
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy the rest of the application ----
COPY . .

# ---- Expose the port Hugging Face Spaces expects ----
EXPOSE 7860

# ---- Start the FastAPI server ----
# Models will be downloaded automatically on first request to /tmp/.cache
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]