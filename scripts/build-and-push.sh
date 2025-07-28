#!/bin/bash

# Azure Day 2 Engine - Build and Push Docker Images to ACR
# ========================================================

set -e

# Configuration
ACR_NAME="${ACR_NAME:-advaks}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PROJECT_NAME="azure-day2-engine"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏗️  Azure Day 2 Engine - Docker Build and Push${NC}"
echo "=================================================="

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verify prerequisites
echo -e "${BLUE}🔍 Verifying prerequisites...${NC}"

# Check if ACR_NAME is set
if [ -z "$ACR_NAME" ]; then
    print_error "ACR_NAME environment variable is not set"
    echo "Please set ACR_NAME to your Azure Container Registry name"
    echo "Example: export ACR_NAME=myregistry"
    exit 1
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running or not accessible"
    exit 1
fi

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed"
    exit 1
fi

if ! az account show >/dev/null 2>&1; then
    print_error "Not logged in to Azure CLI"
    echo "Please run: az login"
    exit 1
fi

print_status "Prerequisites verified"

# Login to ACR
echo -e "${BLUE}🔐 Logging in to Azure Container Registry...${NC}"
az acr login --name "$ACR_NAME"
print_status "Logged in to ACR: $ACR_NAME"

# Build backend image
echo -e "${BLUE}🏗️  Building backend Docker image...${NC}"
docker build \
    -f docker/backend.Dockerfile \
    -t "$ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG" \
    .

print_status "Backend image built: $ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG"

# Build frontend image
echo -e "${BLUE}🎨 Building frontend Docker image...${NC}"
docker build \
    -f docker/frontend.Dockerfile \
    -t "$ACR_NAME.azurecr.io/$PROJECT_NAME-frontend:$IMAGE_TAG" \
    .

print_status "Frontend image built: $ACR_NAME.azurecr.io/$PROJECT_NAME-frontend:$IMAGE_TAG"

# Push backend image
echo -e "${BLUE}📤 Pushing backend image to ACR...${NC}"
docker push "$ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG"
print_status "Backend image pushed to registry"

# Push frontend image
echo -e "${BLUE}📤 Pushing frontend image to ACR...${NC}"
docker push "$ACR_NAME.azurecr.io/$PROJECT_NAME-frontend:$IMAGE_TAG"
print_status "Frontend image pushed to registry"

# Verify images in registry
echo -e "${BLUE}🔍 Verifying images in registry...${NC}"
echo "Backend repositories:"
az acr repository show-tags --name "$ACR_NAME" --repository "$PROJECT_NAME-backend" --output table

echo "Frontend repositories:"
az acr repository show-tags --name "$ACR_NAME" --repository "$PROJECT_NAME-frontend" --output table

print_status "Build and push completed successfully!"

echo ""
echo -e "${GREEN}🎉 Images are ready for deployment:${NC}"
echo "   Backend:  $ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG"
echo "   Frontend: $ACR_NAME.azurecr.io/$PROJECT_NAME-frontend:$IMAGE_TAG"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "   1. Update your AKS cluster to use these images"
echo "   2. Run: ./scripts/deploy-to-aks.sh"