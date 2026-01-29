FROM python:3.11-slim

WORKDIR /app

# Install git and supervisor
RUN apt-get update && apt-get install -y \
    git \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "coding-agent@github.com" \
    && git config --global user.name "Coding Agent"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directories
RUN mkdir -p /app/repos /app/data /var/log/supervisor

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default: run with supervisor (auto-restart)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
