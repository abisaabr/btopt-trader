# Use the official Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the project code
COPY . /app

# Run the FastAPI app with Uvicorn on port 8080
CMD ["uvicorn", "live.main:app", "--host", "0.0.0.0", "--port", "8080"]
