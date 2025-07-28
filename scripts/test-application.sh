#!/bin/bash

# Azure Day 2 Engine - Application Testing Script
# ===============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Azure Day 2 Engine - Application Testing${NC}"
echo "==========================================="

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

# Get service information
echo -e "${BLUE}🔍 Getting service information...${NC}"
FRONTEND_IP=$(kubectl get svc azure-day2-engine-frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
BACKEND_CLUSTER_IP=$(kubectl get svc azure-day2-engine-backend-service -o jsonpath='{.spec.clusterIP}')

if [ -z "$FRONTEND_IP" ]; then
    print_warning "Frontend external IP not yet assigned"
    FRONTEND_IP="<pending>"
fi

print_info "Frontend External IP: $FRONTEND_IP"
print_info "Backend Cluster IP: $BACKEND_CLUSTER_IP"

# Test 1: Check pods status
echo -e "\n${BLUE}📊 Test 1: Pod Status${NC}"
PODS_STATUS=$(kubectl get pods --no-headers | grep azure-day2-engine)
echo "$PODS_STATUS"

RUNNING_PODS=$(echo "$PODS_STATUS" | grep "Running" | wc -l | tr -d ' ')
if [ "$RUNNING_PODS" -eq 2 ]; then
    print_status "All pods are running ($RUNNING_PODS/2)"
else
    print_error "Not all pods are running ($RUNNING_PODS/2)"
fi

# Test 2: Backend Health Check
echo -e "\n${BLUE}🏥 Test 2: Backend Health Check${NC}"
BACKEND_POD=$(kubectl get pods -l component=backend -o jsonpath='{.items[0].metadata.name}')
HEALTH_RESPONSE=$(kubectl exec $BACKEND_POD -- curl -s http://localhost:8000/health)

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    print_status "Backend health check passed"
    echo "Response: $HEALTH_RESPONSE"
else
    print_error "Backend health check failed"
    echo "Response: $HEALTH_RESPONSE"
fi

# Test 3: Backend API Documentation
echo -e "\n${BLUE}📚 Test 3: API Documentation Endpoints${NC}"
DOCS_RESPONSE=$(kubectl exec $BACKEND_POD -- curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
REDOC_RESPONSE=$(kubectl exec $BACKEND_POD -- curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/redoc)

if [ "$DOCS_RESPONSE" = "200" ]; then
    print_status "Swagger UI (/docs) is accessible"
else
    print_error "Swagger UI (/docs) returned: $DOCS_RESPONSE"
fi

if [ "$REDOC_RESPONSE" = "200" ]; then
    print_status "ReDoc (/redoc) is accessible"
else
    print_error "ReDoc (/redoc) returned: $REDOC_RESPONSE"
fi

# Test 4: Frontend Status
echo -e "\n${BLUE}🎨 Test 4: Frontend Status${NC}"
FRONTEND_POD=$(kubectl get pods -l component=frontend -o jsonpath='{.items[0].metadata.name}')
FRONTEND_LOGS=$(kubectl logs $FRONTEND_POD --tail=5)

if echo "$FRONTEND_LOGS" | grep -q "Streamlit" || echo "$FRONTEND_LOGS" | grep -q "You can now view"; then
    print_status "Frontend (Streamlit) is running"
else
    print_warning "Frontend status unclear, check logs manually"
fi

# Test 5: Service Connectivity
echo -e "\n${BLUE}🔗 Test 5: Service Connectivity${NC}"
BACKEND_SERVICE_TEST=$(kubectl exec $FRONTEND_POD -- curl -s -o /dev/null -w "%{http_code}" http://azure-day2-engine-backend-service/health)

if [ "$BACKEND_SERVICE_TEST" = "200" ]; then
    print_status "Frontend can reach backend service"
else
    print_warning "Frontend-to-backend connectivity issue (code: $BACKEND_SERVICE_TEST)"
fi

# Summary and Access Information
echo -e "\n${GREEN}🎉 Testing Summary${NC}"
echo "=================="

if [ "$FRONTEND_IP" != "<pending>" ]; then
    echo -e "${GREEN}🌐 Frontend Access:${NC}"
    echo "   Direct Access: http://$FRONTEND_IP"
    echo "   Local Access:  kubectl port-forward svc/azure-day2-engine-frontend-service 8501:80"
    echo "                  Then visit: http://localhost:8501"
else
    echo -e "${YELLOW}🌐 Frontend Access (IP pending):${NC}"
    echo "   Local Access: kubectl port-forward svc/azure-day2-engine-frontend-service 8501:80"
    echo "                 Then visit: http://localhost:8501"
fi

echo ""
echo -e "${GREEN}🔧 Backend API Access:${NC}"
echo "   Local Access: kubectl port-forward svc/azure-day2-engine-backend-service 8000:80"
echo "   Then visit:"
echo "     - API Docs: http://localhost:8000/docs"
echo "     - ReDoc:    http://localhost:8000/redoc"
echo "     - Health:   http://localhost:8000/health"

echo ""
echo -e "${BLUE}📊 Quick Commands:${NC}"
echo "   Check logs:   kubectl logs -f -l component=backend"
echo "   Check pods:   kubectl get pods"
echo "   Check services: kubectl get services"

echo ""
print_status "Application testing completed!"
