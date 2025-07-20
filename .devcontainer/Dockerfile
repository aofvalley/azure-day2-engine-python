FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        postgresql-client \
        vim \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI (already included in base image but ensure latest)
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Create app directory
WORKDIR /workspaces/${containerWorkspaceFolder}

# Install Python tools for development
RUN pip install --upgrade pip \
    && pip install black isort flake8 pylint pytest pytest-asyncio

# Expose port for FastAPI
EXPOSE 8000

# Keep container running
CMD ["sleep", "infinity"]