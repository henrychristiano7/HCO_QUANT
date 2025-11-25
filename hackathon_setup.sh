#!/bin/bash

# =========================================================
# HCO Quant AI Dashboard - All-in-One Hackathon Setup Script
# Author: Henry Christian
# Docker Hub Username: henrychristiano7
# =========================================================

set -e

DOCKER_USERNAME="henrychristiano7"
PROJECT_NAME="hco-quant-ai-dashboard"

echo "============================================"
echo "Starting HCO Quant AI Dashboard Setup..."
echo "============================================"

# -----------------------------
# 0. Check if Docker is installed
# -----------------------------
if ! command -v docker &> /dev/null
then
    echo "⚠ Docker not found. Installing Docker..."
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io

    # Allow current user to run Docker without sudo
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. Please log out and log back in or run 'newgrp docker' to use Docker without sudo."
else
    echo "✅ Docker is already installed."
fi

# -----------------------------
# 1. Build Docker Images
# -----------------------------
echo "[1/5] Building Docker images..."

# Backend Dockerfile
cat > backend/Dockerfile <<EOL
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "hco_quant_api.py"]
EOL

# Frontend Dockerfile
cat > frontend/Dockerfile <<EOL
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./ 
RUN npm install
COPY . .
CMD ["npm", "start"]
EOL

# Build Docker images
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-backend:latest ./backend
docker build -t $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest ./frontend

echo "Docker images built successfully!"

# -----------------------------
# 2. Setup Auto-Update Bot
# -----------------------------
echo "[2/5] Setting up auto-update bot..."

cat > auto_update.py <<EOL
import asyncio
from hco_quant_api import run_multi_update, run_single_update

async def auto_update(interval=600):
    while True:
        print("Updating Multi-Symbol Dashboard...")
        await run_multi_update()
        print("Updating Single-Symbol Dashboard...")
        await run_single_update(symbols=["AAPL", "TSLA", "MSFT"])
        print(f"Update completed. Waiting {interval} seconds...")
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(auto_update())
EOL

docker build -t $DOCKER_USERNAME/$PROJECT_NAME-bot:latest .

echo "Auto-update bot ready."

# -----------------------------
# 3. Generate GitHub Actions Workflow
# -----------------------------
echo "[3/5] Creating GitHub Actions workflow..."

mkdir -p .github/workflows

cat > .github/workflows/ci-cd.yml <<EOL
name: HCO Quant CI/CD

on:
  push:
    branches:
      - main
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Backend Dependencies
        run: pip install -r backend/requirements.txt
      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm install
      - name: Build Docker Images
        run: |
          docker build -t $DOCKER_USERNAME/$PROJECT_NAME-backend:latest ./backend
          docker build -t $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest ./frontend
      - name: Push to Docker Hub
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: $DOCKER_USERNAME/$PROJECT_NAME-backend:latest
EOL

echo "GitHub Actions workflow created."

# -----------------------------
# 4. Generate Kubernetes Manifests
# -----------------------------
echo "[4/5] Creating Kubernetes manifests..."

mkdir -p k8s

cat > k8s/deployment.yaml <<EOL
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hco-quant-ai-dashboard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hco-quant
  template:
    metadata:
      labels:
        app: hco-quant
    spec:
      containers:
      - name: backend
        image: $DOCKER_USERNAME/$PROJECT_NAME-backend:latest
        ports:
        - containerPort: 8000
      - name: frontend
        image: $DOCKER_USERNAME/$PROJECT_NAME-frontend:latest
        ports:
        - containerPort: 3000
EOL

cat > k8s/service.yaml <<EOL
apiVersion: v1
kind: Service
metadata:
  name: hco-quant-service
spec:
  selector:
    app: hco-quant
  type: LoadBalancer
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
EOL

echo "Kubernetes manifests ready."

# -----------------------------
# 5. Cloud Deployment Templates
# -----------------------------
echo "[5/5] Generating cloud deployment templates..."

cat > aws_deploy.json <<EOL
{
  "family": "$PROJECT_NAME",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "$DOCKER_USERNAME/$PROJECT_NAME-backend:latest",
      "portMappings": [{"containerPort": 8000}]
    },
    {
      "name": "frontend",
      "image": "$DOCKER_USERNAME/$PROJECT_NAME-frontend:latest",
      "portMappings": [{"containerPort": 3000}]
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024"
}
EOL

cat > render.yaml <<EOL
services:
  - type: web
    name: hco-quant-frontend
    env: docker
    dockerfilePath: ./frontend/Dockerfile
    autoDeploy: true
  - type: web
    name: hco-quant-backend
    env: docker
    dockerfilePath: ./backend/Dockerfile
    autoDeploy: true
EOL

echo "Cloud deployment templates ready."

echo "============================================"
echo "All-in-one Hackathon setup completed!"
echo "Next steps:"
echo "- Push your code to GitHub"
echo "- Run Docker containers or deploy to cloud/K8s"
echo "- Start auto-update bot if needed"
echo "============================================"
