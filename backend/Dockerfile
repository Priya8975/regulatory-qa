# Backend Dockerfile
#
# This builds a container that runs the FastAPI server.
# It installs Python dependencies, copies the code, and starts uvicorn.

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer separately,
# so if only code changes but not dependencies, it won't reinstall everything)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose port 8000 so the frontend container can reach us
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
