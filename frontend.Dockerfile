# Frontend (Streamlit) Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements from root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend source
COPY frontend/ /app/frontend/

# Set Environment Variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Start Streamlit
CMD ["streamlit", "run", "frontend/app.py"]
