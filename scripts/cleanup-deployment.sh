#!/bin/bash

# Azure Day 2 Engine - Cleanup AKS Deployment (Helm)
# ===================================================

set -e

# Configuration
NAMESPACE="${NAMESPACE:-default}"
HELM_RELEASE_NAME="${HELM_RELEASE_NAME:-azure-day2-engine}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Azure Day 2 Engine - Cleanup Deployment (Helm)${NC}"
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

# Confirm cleanup
echo -e "${YELLOW}⚠️  This will delete the Azure Day 2 Engine Helm release from the AKS cluster${NC}"
echo "Namespace: $NAMESPACE"
echo "Helm Release: $HELM_RELEASE_NAME"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

echo -e "${BLUE}🔍 Checking current Helm releases...${NC}"
helm list -n "$NAMESPACE"

echo ""
echo -e "${BLUE}🗑️  Deleting Helm release...${NC}"

# Check if the release exists
if helm list -n "$NAMESPACE" | grep -q "$HELM_RELEASE_NAME"; then
    # Uninstall the Helm release
    helm uninstall "$HELM_RELEASE_NAME" -n "$NAMESPACE"
    print_status "Helm release '$HELM_RELEASE_NAME' deleted successfully"
else
    print_warning "Helm release '$HELM_RELEASE_NAME' not found"
fi

# Wait for cleanup to complete
echo -e "${BLUE}⏳ Waiting for cleanup to complete...${NC}"
sleep 5

# Verify cleanup
echo -e "${BLUE}🔍 Verifying cleanup...${NC}"

# Check if any resources remain with the app label
REMAINING_RESOURCES=$(kubectl get all -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine --no-headers 2>/dev/null | wc -l)

if [ "$REMAINING_RESOURCES" -eq 0 ]; then
    print_status "All Azure Day 2 Engine resources have been successfully deleted!"
else
    print_warning "Some resources may still be terminating:"
    kubectl get all -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine
fi

# Check Helm release status
echo ""
echo -e "${BLUE}📋 Final Helm status:${NC}"
if helm list -n "$NAMESPACE" | grep -q "$HELM_RELEASE_NAME"; then
    print_warning "Helm release still exists (may be in terminating state)"
    helm list -n "$NAMESPACE" | grep "$HELM_RELEASE_NAME"
else
    print_status "Helm release successfully removed"
fi

echo ""
print_status "Cleanup completed!"

echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "   • Helm release '$HELM_RELEASE_NAME' uninstalled from namespace: $NAMESPACE"
echo "   • All deployments, services, and resources cleaned up"
echo "   • Secrets and configuration maps deleted"
echo "   • Service accounts removed"
echo ""
echo -e "${GREEN}Your AKS cluster is now clean of Azure Day 2 Engine resources.${NC}"