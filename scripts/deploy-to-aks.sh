#!/bin/bash

# Azure Day 2 Engine - Deploy to AKS using Helm
# ==============================================

set -e

# Configuration
ACR_NAME="${ACR_NAME:-advaks}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
AKS_CLUSTER="${AKS_CLUSTER:-adv_aks}"
AKS_RESOURCE_GROUP="${AKS_RESOURCE_GROUP}"
NAMESPACE="${NAMESPACE:-default}"
HELM_RELEASE_NAME="${HELM_RELEASE_NAME:-azure-day2-engine}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Azure Day 2 Engine - AKS Deployment (Helm)${NC}"
echo "=============================================="

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

# Check required environment variables
if [ -z "$ACR_NAME" ]; then
    print_error "ACR_NAME environment variable is not set"
    echo "Please set ACR_NAME to your Azure Container Registry name"
    exit 1
fi

if [ -z "$AKS_RESOURCE_GROUP" ]; then
    print_error "AKS_RESOURCE_GROUP environment variable is not set"
    echo "Please set AKS_RESOURCE_GROUP to your AKS resource group name"
    exit 1
fi

# Check Azure credentials environment variables
if [ -z "$AZURE_CLIENT_ID" ] || [ -z "$AZURE_TENANT_ID" ] || [ -z "$AZURE_CLIENT_SECRET" ] || [ -z "$AZURE_SUBSCRIPTION_ID" ]; then
    print_warning "Azure credential environment variables are not all set"
    echo "Required variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, AZURE_SUBSCRIPTION_ID"
    echo "You can set them now or the deployment will use placeholder values"
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
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

# Get AKS credentials
echo -e "${BLUE}🔑 Getting AKS credentials...${NC}"
az aks get-credentials --resource-group "$AKS_RESOURCE_GROUP" --name "$AKS_CLUSTER" --overwrite-existing
print_status "AKS credentials configured"

# Verify kubectl connection
echo -e "${BLUE}🔗 Verifying AKS connection...${NC}"
kubectl cluster-info
print_status "Connected to AKS cluster: $AKS_CLUSTER"

# Create namespace if it doesn't exist
echo -e "${BLUE}📦 Ensuring namespace exists...${NC}"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
print_status "Namespace '$NAMESPACE' ready"

# Prepare Helm values
echo -e "${BLUE}🔧 Preparing Helm deployment...${NC}"

# Create temporary values file for this deployment
TEMP_VALUES_FILE=$(mktemp)
cat > "$TEMP_VALUES_FILE" << EOF
global:
  registry: "$ACR_NAME.azurecr.io"
  imageTag: "$IMAGE_TAG"
  azure:
    clientId: "${AZURE_CLIENT_ID:-placeholder-client-id}"
    tenantId: "${AZURE_TENANT_ID:-placeholder-tenant-id}"
    clientSecret: "${AZURE_CLIENT_SECRET:-placeholder-client-secret}"
    subscriptionId: "${AZURE_SUBSCRIPTION_ID:-placeholder-subscription-id}"
EOF

if [ -n "$AZURE_CLIENT_ID" ] && [ -n "$AZURE_TENANT_ID" ] && [ -n "$AZURE_CLIENT_SECRET" ] && [ -n "$AZURE_SUBSCRIPTION_ID" ]; then
    print_status "Azure credentials configured for Helm deployment"
else
    print_warning "Using placeholder Azure credentials - update values after deployment"
fi

# Deploy using Helm
echo -e "${BLUE}🚀 Deploying with Helm...${NC}"

# Check if release exists
if helm list -n "$NAMESPACE" | grep -q "$HELM_RELEASE_NAME"; then
    echo "Upgrading existing Helm release..."
    helm upgrade "$HELM_RELEASE_NAME" ./helm-chart \
        --namespace "$NAMESPACE" \
        --values "$TEMP_VALUES_FILE" \
        --wait \
        --timeout=10m
    print_status "Helm release upgraded successfully"
else
    echo "Installing new Helm release..."
    helm install "$HELM_RELEASE_NAME" ./helm-chart \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --values "$TEMP_VALUES_FILE" \
        --wait \
        --timeout=10m
    print_status "Helm release installed successfully"
fi

# Clean up temporary file
rm -f "$TEMP_VALUES_FILE"

print_status "All deployments are ready!"

# Get service information
echo -e "${BLUE}📋 Deployment information:${NC}"
echo ""
echo "Pods:"
kubectl get pods -n "$NAMESPACE" -l app=azure-day2-engine

echo ""
echo "Services:"
kubectl get services -n "$NAMESPACE" -l app=azure-day2-engine

echo ""
echo "Deployments:"
kubectl get deployments -n "$NAMESPACE" -l app=azure-day2-engine

# Get external IP for frontend
echo ""
echo -e "${BLUE}🌐 Getting external access information...${NC}"
FRONTEND_EXTERNAL_IP=$(kubectl get service azure-day2-engine-frontend-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -n "$FRONTEND_EXTERNAL_IP" ]; then
    print_status "Frontend is accessible at: http://$FRONTEND_EXTERNAL_IP"
else
    print_warning "Frontend external IP is pending. Run the following command to check:"
    echo "kubectl get service azure-day2-engine-frontend-service -n $NAMESPACE"
fi

# Get backend service information
BACKEND_CLUSTER_IP=$(kubectl get service azure-day2-engine-backend-service -n "$NAMESPACE" -o jsonpath='{.spec.clusterIP}')
print_status "Backend service cluster IP: $BACKEND_CLUSTER_IP"

echo ""
print_status "Deployment completed successfully!"

echo ""
echo -e "${GREEN}🎉 Azure Day 2 Engine is now running in your AKS cluster!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "   1. Wait for external IP assignment (may take a few minutes)"
echo "   2. Test the backend API health: kubectl port-forward service/azure-day2-engine-backend-service -n $NAMESPACE 8080:80"
echo "   3. Access health check: http://localhost:8080/health"
echo "   4. Update Azure credentials if using placeholders:"
echo "      helm upgrade $HELM_RELEASE_NAME ./helm-chart -n $NAMESPACE \\"
echo "        --set global.azure.clientId=your-client-id \\"
echo "        --set global.azure.tenantId=your-tenant-id \\"
echo "        --set global.azure.clientSecret=your-client-secret \\"
echo "        --set global.azure.subscriptionId=your-subscription-id"
echo "   5. Use Helm commands to manage the deployment:"
echo "      helm list -n $NAMESPACE"
echo "      helm status $HELM_RELEASE_NAME -n $NAMESPACE"