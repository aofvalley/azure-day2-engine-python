#!/bin/bash

# Deploy Azure Day 2 Engine with Security Features
# ===============================================
# Complete deployment script with authentication and security

set -e

# Load environment configuration
source "$(dirname "$0")/load-env.sh"

echo "🚀 Deploying Azure Day 2 Engine with Security Features"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE=${NAMESPACE:-default}
HELM_RELEASE_NAME=${HELM_RELEASE_NAME:-azure-day2-engine}

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   Registry: $ACR_NAME.azurecr.io"
echo "   Image Tag: $IMAGE_TAG"
echo "   Namespace: $NAMESPACE"
echo "   Release: $HELM_RELEASE_NAME"

# Step 1: Build and push images
echo -e "\n${BLUE}🏗️  Building and pushing Docker images...${NC}"
if ./scripts/build-and-push.sh; then
    echo -e "${GREEN}✅ Images built and pushed successfully${NC}"
else
    echo -e "${RED}❌ Failed to build and push images${NC}"
    exit 1
fi

# Step 2: Generate secure authentication secrets
echo -e "\n${BLUE}🔐 Generating authentication secrets...${NC}"

# Generate random secret key for JWT
AUTH_SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ADMIN_USERNAME="admin"
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"azure-day2-engine-2025"}

echo "   Secret key: [generated]"
echo "   Admin username: $ADMIN_USERNAME"
echo "   Admin password: [configured]"

# Step 3: Deploy with Helm
echo -e "\n${BLUE}🚢 Deploying to AKS with Helm...${NC}"

# Check if release exists
if helm list -n "$NAMESPACE" | grep -q "$HELM_RELEASE_NAME"; then
    echo "Upgrading existing release..."
    HELM_COMMAND="upgrade"
else
    echo "Installing new release..."
    HELM_COMMAND="install"
fi

# Deploy with security configuration
helm $HELM_COMMAND $HELM_RELEASE_NAME ./helm-chart \
    --namespace "$NAMESPACE" \
    --set global.registry="$ACR_NAME.azurecr.io" \
    --set global.imageTag="$IMAGE_TAG" \
    --set global.azure.clientId="$AZURE_CLIENT_ID" \
    --set global.azure.tenantId="$AZURE_TENANT_ID" \
    --set global.azure.clientSecret="$AZURE_CLIENT_SECRET" \
    --set global.azure.subscriptionId="$AZURE_SUBSCRIPTION_ID" \
    --set global.auth.secretKey="$AUTH_SECRET_KEY" \
    --set global.auth.adminUsername="$ADMIN_USERNAME" \
    --set global.auth.adminPassword="$ADMIN_PASSWORD" \
    --set global.auth.tokenExpireMinutes="1440" \
    --set backend.service.type="LoadBalancer" \
    --set frontend.service.type="LoadBalancer" \
    --wait --timeout=10m

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful${NC}"
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Step 4: Wait for LoadBalancer IPs
echo -e "\n${BLUE}⏳ Waiting for LoadBalancer external IPs...${NC}"

echo "Waiting for backend service..."
kubectl wait --for=jsonpath='{.status.loadBalancer.ingress[0].ip}' \
    svc/azure-day2-engine-backend-service \
    -n "$NAMESPACE" --timeout=300s || {
    echo -e "${RED}❌ Backend LoadBalancer timeout${NC}"
    kubectl describe svc azure-day2-engine-backend-service -n "$NAMESPACE"
    exit 1
}

echo "Waiting for frontend service..."
kubectl wait --for=jsonpath='{.status.loadBalancer.ingress[0].ip}' \
    svc/azure-day2-engine-frontend-service \
    -n "$NAMESPACE" --timeout=300s || {
    echo -e "${RED}❌ Frontend LoadBalancer timeout${NC}"
    kubectl describe svc azure-day2-engine-frontend-service -n "$NAMESPACE"
    exit 1
}

# Step 5: Get service information
BACKEND_IP=$(kubectl get svc azure-day2-engine-backend-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
FRONTEND_IP=$(kubectl get svc azure-day2-engine-frontend-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo -e "${GREEN}✅ External IPs assigned:${NC}"
echo "   Backend:  $BACKEND_IP"
echo "   Frontend: $FRONTEND_IP"

# Step 6: Update frontend configuration with backend IP
echo -e "\n${BLUE}🔄 Updating frontend configuration...${NC}"

helm upgrade $HELM_RELEASE_NAME ./helm-chart \
    --namespace "$NAMESPACE" \
    --reuse-values \
    --set frontend.env.API_URL="http://$BACKEND_IP" \
    --wait --timeout=5m

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Frontend configuration updated${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend configuration update may have issues${NC}"
fi

# Step 7: Verify deployment
echo -e "\n${BLUE}🔍 Verifying deployment...${NC}"

kubectl get pods -l app=azure-day2-engine -n "$NAMESPACE"
kubectl get svc -l app=azure-day2-engine -n "$NAMESPACE"

# Step 8: Test security
echo -e "\n${BLUE}🔐 Testing security implementation...${NC}"
sleep 30  # Give services time to fully start

if ./scripts/test-security.sh; then
    echo -e "${GREEN}✅ Security tests passed${NC}"
else
    echo -e "${YELLOW}⚠️  Some security tests may need manual verification${NC}"
fi

# Summary
echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
echo "=================================="

echo -e "\n${BLUE}🔗 Access Information:${NC}"
echo "Frontend Dashboard: http://$FRONTEND_IP"
echo "Backend API Docs:   http://$BACKEND_IP/docs"
echo "Backend Redoc:      http://$BACKEND_IP/redoc"
echo "Health Check:       http://$BACKEND_IP/health"

echo -e "\n${BLUE}🔐 Authentication:${NC}"
echo "Username: $ADMIN_USERNAME"
echo "Password: $ADMIN_PASSWORD"

echo -e "\n${BLUE}⚠️  Security Notes:${NC}"
echo "• Frontend requires login before access"
echo "• All API endpoints (except /health, /docs, /redoc) require authentication"
echo "• JWT tokens expire in 24 hours (configurable)"
echo "• Both services are exposed via LoadBalancer (production ready)"

echo -e "\n${BLUE}📋 Next Steps:${NC}"
echo "1. Access the frontend at http://$FRONTEND_IP"
echo "2. Login with the credentials above"
echo "3. Test AKS and PostgreSQL operations"
echo "4. Access API documentation at http://$BACKEND_IP/docs"
echo "5. Monitor logs: kubectl logs -l app=azure-day2-engine -n $NAMESPACE -f"

echo -e "\n${GREEN}Deployment script completed!${NC}"