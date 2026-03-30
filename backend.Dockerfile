# Backend (FastAPI) Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements from root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend logic
COPY backend/ /app/backend/

# Set Python path to ensure imports from 'backend' folder work
ENV PYTHONPATH=/app/backend

# Run the API
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
