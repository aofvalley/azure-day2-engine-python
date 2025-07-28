#!/bin/bash

# Azure Day 2 Engine - Build and Push Docker Images to ACR
# ========================================================
# Updated: Fixed ImagePullBackOff issues by:
# - Building for AMD64 architecture (AKS node compatibility)
# - Enhanced error handling for Azure CLI authentication
# - Automatic Docker buildx setup

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/load-env.sh"

PROJECT_NAME="azure-day2-engine"

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

# Enable Docker buildx for multi-platform builds
if ! docker buildx version >/dev/null 2>&1; then
    print_warning "Docker buildx not available, enabling..."
    docker buildx create --use --name multiarch --driver docker-container
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

# Login to ACR with error handling
echo -e "${BLUE}🔐 Logging in to Azure Container Registry...${NC}"

# Try ACR login with error handling for known Azure CLI issues
if ! az acr login --name "$ACR_NAME" 2>/dev/null; then
    print_warning "ACR login failed. This might be due to Azure CLI cache issues."
    echo -e "${YELLOW}Attempting to fix Azure CLI cache...${NC}"
    
    # Clear Azure CLI cache
    print_warning "Clearing Azure CLI cache..."
    rm -rf ~/.azure/msal_http_cache
    rm -rf ~/.azure/msal_token_cache.bin
    
    # Try login again
    echo -e "${BLUE}Retrying ACR login...${NC}"
    if ! az acr login --name "$ACR_NAME"; then
        print_error "ACR login failed even after clearing cache."
        echo ""
        echo "Possible solutions:"
        echo "1. Clear all Azure CLI cache: rm -rf ~/.azure && az login"
        echo "2. Downgrade Azure CLI: brew uninstall azure-cli && brew install azure-cli@2.70.0"
        echo "3. Use Docker login directly: docker login $ACR_NAME.azurecr.io"
        echo ""
        echo "If using Docker login, you'll need to get ACR credentials manually:"
        echo "az acr credential show --name $ACR_NAME"
        exit 1
    fi
fi

print_status "Logged in to ACR: $ACR_NAME"

# Build backend image for AMD64 (AKS nodes architecture)
echo -e "${BLUE}🏗️  Building backend Docker image for AMD64...${NC}"
docker buildx build \
    --platform linux/amd64 \
    -f docker/backend.Dockerfile \
    -t "$ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG" \
    --load \
    .

print_status "Backend image built: $ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG"

# Build frontend image for AMD64 (AKS nodes architecture)
echo -e "${BLUE}🎨 Building frontend Docker image for AMD64...${NC}"
docker buildx build \
    --platform linux/amd64 \
    -f docker/frontend.Dockerfile \
    -t "$ACR_NAME.azurecr.io/$PROJECT_NAME-frontend:$IMAGE_TAG" \
    --load \
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