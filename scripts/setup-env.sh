#!/bin/bash

# Azure Day 2 Engine - Environment Setup Helper
# ==============================================
# This script helps you set up your .env file interactively

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}🔧 Azure Day 2 Engine - Environment Setup${NC}"
echo "========================================="
echo ""

# Get the project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"
ENV_FILE="$PROJECT_DIR/.env"

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    print_warning ".env file already exists"
    echo ""
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Keeping existing .env file"
        print_info "You can edit it manually: $ENV_FILE"
        exit 0
    fi
fi

# Copy from example
if [ ! -f "$ENV_EXAMPLE" ]; then
    print_error ".env.example not found at: $ENV_EXAMPLE"
    exit 1
fi

cp "$ENV_EXAMPLE" "$ENV_FILE"
print_status ".env file created from template"

echo ""
print_info "Please provide the following configuration values:"
echo ""

# Collect Azure credentials
echo -e "${BLUE}Azure Configuration:${NC}"
read -p "Azure Tenant ID: " AZURE_TENANT_ID
read -p "Azure Client ID: " AZURE_CLIENT_ID
read -s -p "Azure Client Secret: " AZURE_CLIENT_SECRET
echo ""
read -p "Azure Subscription ID: " AZURE_SUBSCRIPTION_ID

echo ""
echo -e "${BLUE}AKS Configuration:${NC}"
read -p "AKS Resource Group: " AKS_RESOURCE_GROUP
read -p "ACR Name (default: advaks): " ACR_NAME_INPUT
read -p "AKS Cluster Name (default: adv_aks): " AKS_CLUSTER_INPUT
read -p "Image Tag (default: latest): " IMAGE_TAG_INPUT

# Set defaults
ACR_NAME=${ACR_NAME_INPUT:-advaks}
AKS_CLUSTER=${AKS_CLUSTER_INPUT:-adv_aks}
IMAGE_TAG=${IMAGE_TAG_INPUT:-latest}

echo ""
print_info "Updating .env file with your values..."

# Update the .env file
sed -i.bak "s/AZURE_TENANT_ID=.*/AZURE_TENANT_ID=$AZURE_TENANT_ID/" "$ENV_FILE"
sed -i.bak "s/AZURE_CLIENT_ID=.*/AZURE_CLIENT_ID=$AZURE_CLIENT_ID/" "$ENV_FILE"
sed -i.bak "s/AZURE_CLIENT_SECRET=.*/AZURE_CLIENT_SECRET=$AZURE_CLIENT_SECRET/" "$ENV_FILE"
sed -i.bak "s/AZURE_SUBSCRIPTION_ID=.*/AZURE_SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID/" "$ENV_FILE"
sed -i.bak "s/AKS_RESOURCE_GROUP=.*/AKS_RESOURCE_GROUP=$AKS_RESOURCE_GROUP/" "$ENV_FILE"
sed -i.bak "s/ACR_NAME=.*/ACR_NAME=$ACR_NAME/" "$ENV_FILE"
sed -i.bak "s/AKS_CLUSTER=.*/AKS_CLUSTER=$AKS_CLUSTER/" "$ENV_FILE"
sed -i.bak "s/IMAGE_TAG=.*/IMAGE_TAG=$IMAGE_TAG/" "$ENV_FILE"

# Remove backup file
rm -f "$ENV_FILE.bak"

print_status ".env file configured successfully!"

echo ""
print_info "Testing configuration..."

# Test the configuration
source "$SCRIPT_DIR/load-env.sh"

echo ""
print_status "Environment setup completed!"
echo ""
print_info "Next steps:"
echo "  1. Review your .env file: $ENV_FILE"
echo "  2. Build and push images: ./scripts/build-and-push.sh"
echo "  3. Deploy to AKS: ./scripts/deploy-to-aks.sh"
echo "  4. Check status: ./scripts/aks-operations.sh status"