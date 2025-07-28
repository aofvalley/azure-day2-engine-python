#!/bin/bash

# Azure Day 2 Engine - Deployment Troubleshooting Script
# ======================================================
# This script helps diagnose and fix common deployment issues

set -e

# Load environment variables from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/load-env.sh"

PROJECT_NAME="azure-day2-engine"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Azure Day 2 Engine - Deployment Troubleshooting${NC}"
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check pod status
check_pod_status() {
    echo -e "${BLUE}🔍 Checking pod status...${NC}"
    kubectl get pods -o wide
    echo ""
}

# Function to show recent pod logs
show_pod_logs() {
    local component=$1
    echo -e "${BLUE}📋 Recent logs for $component:${NC}"
    kubectl logs -l component=$component --tail=20 --prefix=true
    echo ""
}

# Function to describe failing pods
describe_failing_pods() {
    echo -e "${BLUE}🔍 Describing failing pods...${NC}"
    local failing_pods=$(kubectl get pods --no-headers | grep -v "Running\|Completed" | awk '{print $1}')
    
    if [ -z "$failing_pods" ]; then
        print_status "No failing pods found!"
        return
    fi
    
    for pod in $failing_pods; do
        echo -e "${YELLOW}Pod: $pod${NC}"
        kubectl describe pod $pod | grep -A 10 -B 5 "Events:"
        echo ""
    done
}

# Function to fix ImagePullBackOff issues
fix_image_pull_issues() {
    echo -e "${BLUE}🔧 Fixing ImagePullBackOff issues...${NC}"
    
    # Check if images exist in ACR
    print_info "Checking images in ACR..."
    az acr repository list --name "$ACR_NAME" --output table
    
    # Check image manifests
    print_info "Checking image architecture..."
    az acr repository show-manifests --name "$ACR_NAME" --repository "$PROJECT_NAME-backend" --detail | grep -E "architecture|digest" || print_warning "Backend image not found"
    az acr repository show-manifests --name "$ACR_NAME" --repository "$PROJECT_NAME-frontend" --detail | grep -E "architecture|digest" || print_warning "Frontend image not found"
    
    # Restart deployments to force image pull
    print_info "Restarting deployments..."
    kubectl rollout restart deployment azure-day2-engine-backend
    kubectl rollout restart deployment azure-day2-engine-frontend
}

# Function to rebuild images with correct architecture
rebuild_for_amd64() {
    echo -e "${BLUE}🏗️  Rebuilding images for AMD64 architecture...${NC}"
    
    # Enable Docker buildx
    if ! docker buildx version >/dev/null 2>&1; then
        print_warning "Enabling Docker buildx..."
        docker buildx create --use --name multiarch --driver docker-container 2>/dev/null || docker buildx use multiarch 2>/dev/null || true
    fi
    
    # Login to ACR
    print_info "Logging in to ACR..."
    az acr login --name "$ACR_NAME"
    
    # Build backend for AMD64
    print_info "Building backend for AMD64..."
    docker buildx build \
        --platform linux/amd64 \
        -f docker/backend.Dockerfile \
        -t "$ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG" \
        --load \
        .
    
    # Build frontend for AMD64
    print_info "Building frontend for AMD64..."
    docker buildx build \
        --platform linux/amd64 \
        -f docker/frontend.Dockerfile \
        -t "$ACR_NAME.azurecr.io/$PROJECT_NAME-frontend:$IMAGE_TAG" \
        --load \
        .
    
    # Push images
    print_info "Pushing images to ACR..."
    docker push "$ACR_NAME.azurecr.io/$PROJECT_NAME-backend:$IMAGE_TAG"
    docker push "$ACR_NAME.azurecr.io/$PROJECT_NAME-frontend:$IMAGE_TAG"
    
    print_status "Images rebuilt and pushed successfully!"
    
    # Force pod recreation
    print_info "Forcing pod recreation..."
    kubectl delete pods -l app.kubernetes.io/name=azure-day2-engine --ignore-not-found
}

# Main troubleshooting menu
show_menu() {
    echo ""
    echo -e "${BLUE}Select troubleshooting action:${NC}"
    echo "1) Check pod status"
    echo "2) Show pod logs"
    echo "3) Describe failing pods"
    echo "4) Fix ImagePullBackOff issues"
    echo "5) Rebuild images for AMD64"
    echo "6) Run full diagnostic"
    echo "7) Exit"
    echo ""
}

# Full diagnostic function
run_full_diagnostic() {
    echo -e "${BLUE}🔍 Running full diagnostic...${NC}"
    echo ""
    
    check_pod_status
    describe_failing_pods
    
    echo -e "${BLUE}📋 Backend logs:${NC}"
    show_pod_logs "backend"
    
    echo -e "${BLUE}📋 Frontend logs:${NC}"
    show_pod_logs "frontend"
    
    echo -e "${BLUE}🔍 Services status:${NC}"
    kubectl get services
    echo ""
    
    echo -e "${BLUE}🔍 Deployments status:${NC}"
    kubectl get deployments
    echo ""
}

# Check prerequisites
if [ -z "$ACR_NAME" ]; then
    print_error "ACR_NAME environment variable is not set"
    echo "Please set ACR_NAME in your .env file"
    exit 1
fi

# Main loop
while true; do
    show_menu
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            check_pod_status
            ;;
        2)
            echo "Which component? (backend/frontend/all)"
            read component
            if [ "$component" = "all" ]; then
                show_pod_logs "backend"
                show_pod_logs "frontend"
            else
                show_pod_logs "$component"
            fi
            ;;
        3)
            describe_failing_pods
            ;;
        4)
            fix_image_pull_issues
            ;;
        5)
            rebuild_for_amd64
            ;;
        6)
            run_full_diagnostic
            ;;
        7)
            echo -e "${GREEN}👋 Goodbye!${NC}"
            exit 0
            ;;
        *)
            print_error "Invalid option. Please choose 1-7."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
