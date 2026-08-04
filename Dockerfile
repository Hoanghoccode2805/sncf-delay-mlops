# 1. Use Base Image Python 3.10 slim (Lightweight, optimized for storage space)
FROM python:3.10-slim

# 2. Set the default working directory in the Container.
WORKDIR /app

# 3. Install the necessary system libraries for C++ (XGBoost) and Git.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file first to take advantage of Docker Cache.
COPY requirements.txt .

# 5. Install Python libraries (do not cache to minimize image size).
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the entire project source code into the Container.
COPY . .

# 7. Open port 8000 for FastAPI
EXPOSE 8000

# 8. The default command when the container starts (running FastAPI Server)
CMD ["uvicorn", "entrypoint.api:app", "--host", "0.0.0.0", "--port", "8000"]