FROM python:3.11-slim

# Install system dependencies (FFmpeg, OpenCV & audio dependencies)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    fonts-dejavu-core \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependencies and install
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev -o requirements.txt && pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default port for Render
ENV PORT=10000
EXPOSE 10000

CMD ["python", "server.py"]
