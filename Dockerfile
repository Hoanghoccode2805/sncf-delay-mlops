# 1. Use a lightweight Linux base image with Python 3.11 installed
FROM python:3.11-slim

# 2. Set the default working directory inside the container
WORKDIR /app

# 3. Copy the dependencies file first to leverage Docker cache, then install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all source code, configurations, and MLflow models into the container
# COPY [Source_on_your_computer] [Destination_inside_the_container]
COPY src/ src/              
COPY entrypoint/ entrypoint/
COPY config/ config/
COPY mlruns/ mlruns/
COPY mlflow.db .

# 5. Expose port 8000 to allow external traffic to the API
EXPOSE 8000

# 6. Command to start the FastAPI server when the container runs
CMD ["uvicorn", "entrypoint.api:app", "--host", "0.0.0.0", "--port", "8000"]