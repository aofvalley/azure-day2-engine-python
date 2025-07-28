#!/bin/bash

# Azure Day 2 Engine - Environment Variables Loader
# =================================================
# This script loads environment variables from .env file
# Usage: source scripts/load-env.sh

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

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"

print_info "Loading environment variables from .env file..."

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env file not found at: $ENV_FILE"
    print_info "Please copy .env.example to .env and configure your values:"
    echo "  cp .env.example .env"
    echo "  # Edit .env with your actual values"
    return 1 2>/dev/null || exit 1
fi

# Source the .env file
set -a  # automatically export all variables
source "$ENV_FILE"
set +a  # stop automatically exporting

print_status ".env file loaded successfully"

# Validate critical Azure variables
MISSING_VARS=()

if [ -z "$AZURE_CLIENT_ID" ] || [ "$AZURE_CLIENT_ID" = "your-client-id-here" ]; then
    MISSING_VARS+=("AZURE_CLIENT_ID")
fi

if [ -z "$AZURE_TENANT_ID" ] || [ "$AZURE_TENANT_ID" = "your-tenant-id-here" ]; then
    MISSING_VARS+=("AZURE_TENANT_ID")
fi

if [ -z "$AZURE_CLIENT_SECRET" ] || [ "$AZURE_CLIENT_SECRET" = "your-client-secret-here" ]; then
    MISSING_VARS+=("AZURE_CLIENT_SECRET")
fi

if [ -z "$AZURE_SUBSCRIPTION_ID" ] || [ "$AZURE_SUBSCRIPTION_ID" = "your-subscription-id-here" ]; then
    MISSING_VARS+=("AZURE_SUBSCRIPTION_ID")
fi

if [ -z "$AKS_RESOURCE_GROUP" ] || [ "$AKS_RESOURCE_GROUP" = "your-resource-group-here" ]; then
    MISSING_VARS+=("AKS_RESOURCE_GROUP")
fi

# Report validation results
if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    print_status "All critical environment variables are configured"
else
    print_warning "The following variables need to be configured in .env:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    print_info "Please edit $ENV_FILE and set the actual values"
fi

# Display current configuration (safe values only)
echo ""
print_info "Current configuration:"
echo "  ACR_NAME=$ACR_NAME"
echo "  AKS_CLUSTER=$AKS_CLUSTER"
echo "  AKS_RESOURCE_GROUP=$AKS_RESOURCE_GROUP"
echo "  IMAGE_TAG=$IMAGE_TAG"
echo "  NAMESPACE=$NAMESPACE"
echo "  HELM_RELEASE_NAME=$HELM_RELEASE_NAME"
echo "  AZURE_TENANT_ID=${AZURE_TENANT_ID:0:8}... (${#AZURE_TENANT_ID} chars)"
echo "  AZURE_CLIENT_ID=${AZURE_CLIENT_ID:0:8}... (${#AZURE_CLIENT_ID} chars)"
echo "  AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID:0:8}... (${#AZURE_SUBSCRIPTION_ID} chars)"
echo "  AZURE_CLIENT_SECRET=****** (${#AZURE_CLIENT_SECRET} chars)"

# Export validation function for use in other scripts
validate_env() {
    if [ ${#MISSING_VARS[@]} -ne 0 ]; then
        print_error "Environment validation failed. Please configure missing variables."
        return 1
    fi
    return 0
}

export -f validate_env

print_status "Environment loaded and ready for use"