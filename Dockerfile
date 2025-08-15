# Use a slim Python base image
FROM python:3.13.3-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency list first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src src

# Default command
CMD ["python"]
