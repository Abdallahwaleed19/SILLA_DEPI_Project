# ==========================================
# Stage 1: Build the React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /build

# Copy frontend package manifests and install dependencies
COPY ["silla-project (1)/silla/package.json", "./"]
COPY ["silla-project (1)/silla/package-lock.json*", "./"]
RUN npm install --legacy-peer-deps

# Copy frontend source and build static bundle
COPY ["silla-project (1)/silla/", "./"]
RUN npm run build

# ==========================================
# Stage 2: Production Python Backend & Runner
# ==========================================
FROM python:3.11-slim AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    PORT=8000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-cache FastEmbed multilingual model into image for zero-latency cold start
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')"

# Copy core Python modules and databases
COPY SILLA_Data_Engineering/ ./SILLA_Data_Engineering/
COPY SILLA_NLP/ ./SILLA_NLP/
COPY SILLA_Recommendation/ ./SILLA_Recommendation/
COPY SILLA_Data_Science/ ./SILLA_Data_Science/
COPY backend/ ./backend/

# Copy compiled frontend from frontend-builder stage
COPY --from=frontend-builder /build/dist /app/dist
COPY --from=frontend-builder /build/public /app/public

# Expose default HTTP port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
