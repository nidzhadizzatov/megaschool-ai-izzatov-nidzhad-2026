FROM python:3.11-slim

WORKDIR /app

# Install git, supervisor, curl
RUN apt-get update && apt-get install -y \
    git \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Git config
RUN git config --global user.email "coding-agent@github.com" \
    && git config --global user.name "Coding Agent"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create directories
RUN mkdir -p /app/repos /app/data /var/log/supervisor

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose webhook port
EXPOSE 8000

# Run supervisor (starts all 3 processes)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
