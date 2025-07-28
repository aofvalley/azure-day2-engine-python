#!/bin/bash

# Azure Day 2 Engine - AKS Operations Helper (Helm)
# =================================================

# Load environment variables from .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/load-env.sh"

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

# Show usage
show_usage() {
    echo -e "${BLUE}Azure Day 2 Engine - AKS Operations Helper (Helm)${NC}"
    echo "=================================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Available commands:"
    echo "  status      - Show deployment status"
    echo "  logs        - Show application logs"
    echo "  scale       - Scale deployments"
    echo "  restart     - Restart deployments"
    echo "  port-forward - Set up port forwarding"
    echo "  update-secrets - Update Azure credentials"
    echo "  health      - Check application health"
    echo "  helm-status - Show Helm release status"
    echo "  cleanup     - Clean up deployment"
    echo ""
    echo "Environment variables:"
    echo "  ACR_NAME=$ACR_NAME"
    echo "  AKS_CLUSTER=$AKS_CLUSTER"
    echo "  AKS_RESOURCE_GROUP=$AKS_RESOURCE_GROUP"
    echo "  NAMESPACE=$NAMESPACE"
    echo "  HELM_RELEASE_NAME=$HELM_RELEASE_NAME"
}

# Show deployment status
show_status() {
    echo -e "${BLUE}📊 Deployment Status${NC}"
    echo "==================="
    
    echo ""
    echo "Helm Release:"
    helm status "$HELM_RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || echo "No Helm release found"
    
    echo ""
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine -o wide
    
    echo ""
    echo "Services:"
    kubectl get services -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine
    
    echo ""
    echo "Deployments:"
    kubectl get deployments -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine
    
    echo ""
    echo "HPA (if configured):"
    kubectl get hpa -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine 2>/dev/null || echo "No HPA configured"
}

# Show logs
show_logs() {
    echo -e "${BLUE}📝 Application Logs${NC}"
    echo "=================="
    
    echo ""
    echo "Backend logs (last 50 lines):"
    kubectl logs -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine,component=backend --tail=50
    
    echo ""
    echo "Frontend logs (last 50 lines):"
    kubectl logs -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine,component=frontend --tail=50
}

# Scale deployments
scale_deployments() {
    echo -e "${BLUE}⚖️  Scale Deployments${NC}"
    echo "==================="
    
    read -p "Backend replicas (current: $(kubectl get deployment azure-day2-engine-backend -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')): " backend_replicas
    read -p "Frontend replicas (current: $(kubectl get deployment azure-day2-engine-frontend -n "$NAMESPACE" -o jsonpath='{.spec.replicas}')): " frontend_replicas
    
    # Create values for Helm upgrade
    if [ -n "$backend_replicas" ] || [ -n "$frontend_replicas" ]; then
        TEMP_VALUES_FILE=$(mktemp)
        echo "backend:" > "$TEMP_VALUES_FILE"
        if [ -n "$backend_replicas" ]; then
            echo "  replicaCount: $backend_replicas" >> "$TEMP_VALUES_FILE"
        fi
        echo "frontend:" >> "$TEMP_VALUES_FILE"
        if [ -n "$frontend_replicas" ]; then
            echo "  replicaCount: $frontend_replicas" >> "$TEMP_VALUES_FILE"
        fi
        
        # Upgrade Helm release with new replica counts
        helm upgrade "$HELM_RELEASE_NAME" ./helm-chart -n "$NAMESPACE" -f "$TEMP_VALUES_FILE"
        rm -f "$TEMP_VALUES_FILE"
        
        print_status "Deployments scaled via Helm upgrade"
    fi
}

# Restart deployments
restart_deployments() {
    echo -e "${BLUE}🔄 Restart Deployments${NC}"
    echo "====================="
    
    echo "Restarting backend deployment..."
    kubectl rollout restart deployment/azure-day2-engine-backend -n "$NAMESPACE"
    
    echo "Restarting frontend deployment..."
    kubectl rollout restart deployment/azure-day2-engine-frontend -n "$NAMESPACE"
    
    echo "Waiting for rollout to complete..."
    kubectl rollout status deployment/azure-day2-engine-backend -n "$NAMESPACE"
    kubectl rollout status deployment/azure-day2-engine-frontend -n "$NAMESPACE"
    
    print_status "Deployments restarted successfully"
}

# Set up port forwarding
setup_port_forward() {
    echo -e "${BLUE}🌐 Port Forwarding Setup${NC}"
    echo "========================"
    
    echo "Setting up port forwarding..."
    echo "Backend API will be available at: http://localhost:8080"
    echo "Frontend will be available at: http://localhost:8501"
    echo ""
    echo "Press Ctrl+C to stop port forwarding"
    echo ""
    
    # Start port forwarding in background
    kubectl port-forward service/azure-day2-engine-backend-service -n "$NAMESPACE" 8080:80 &
    BACKEND_PID=$!
    
    kubectl port-forward service/azure-day2-engine-frontend-service -n "$NAMESPACE" 8501:80 &
    FRONTEND_PID=$!
    
    # Wait for user interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Port forwarding stopped'" SIGINT
    wait
}

# Update Azure credentials
update_secrets() {
    echo -e "${BLUE}🔐 Update Azure Credentials${NC}"
    echo "============================"
    
    if [ -z "$AZURE_CLIENT_ID" ] || [ -z "$AZURE_TENANT_ID" ] || [ -z "$AZURE_CLIENT_SECRET" ] || [ -z "$AZURE_SUBSCRIPTION_ID" ]; then
        print_error "Azure credential environment variables are not set"
        echo "Please set: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, AZURE_SUBSCRIPTION_ID"
        return 1
    fi
    
    # Update credentials via Helm upgrade
    helm upgrade "$HELM_RELEASE_NAME" ./helm-chart -n "$NAMESPACE" \
        --set global.azure.clientId="$AZURE_CLIENT_ID" \
        --set global.azure.tenantId="$AZURE_TENANT_ID" \
        --set global.azure.clientSecret="$AZURE_CLIENT_SECRET" \
        --set global.azure.subscriptionId="$AZURE_SUBSCRIPTION_ID"
    
    print_status "Azure credentials updated via Helm upgrade"
    print_status "Deployments will automatically restart with new credentials"
}

# Check application health
check_health() {
    echo -e "${BLUE}🏥 Health Check${NC}"
    echo "==============="
    
    # Check if pods are running
    echo "Pod status:"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=azure-day2-engine
    
    echo ""
    echo "Testing backend health endpoint..."
    
    # Try to access health endpoint via port-forward
    kubectl port-forward service/azure-day2-engine-backend-service -n "$NAMESPACE" 8080:80 &
    PF_PID=$!
    
    sleep 2
    
    if curl -s -f http://localhost:8080/health >/dev/null 2>&1; then
        print_status "Backend health check passed"
    else
        print_error "Backend health check failed"
    fi
    
    kill $PF_PID 2>/dev/null
    
    # Check external IP for frontend
    echo ""
    echo "Frontend external access:"
    EXTERNAL_IP=$(kubectl get service azure-day2-engine-frontend-service -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -n "$EXTERNAL_IP" ]; then
        print_status "Frontend accessible at: http://$EXTERNAL_IP"
    else
        print_warning "Frontend external IP is pending"
    fi
}

# Show Helm release status
show_helm_status() {
    echo -e "${BLUE}⚙️  Helm Release Status${NC}"
    echo "======================"
    
    echo "Helm releases in namespace $NAMESPACE:"
    helm list -n "$NAMESPACE"
    
    echo ""
    echo "Detailed status for $HELM_RELEASE_NAME:"
    helm status "$HELM_RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || echo "Release not found"
    
    echo ""
    echo "Release history:"
    helm history "$HELM_RELEASE_NAME" -n "$NAMESPACE" 2>/dev/null || echo "No history available"
}

# Main command handling
case "$1" in
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "scale")
        scale_deployments
        ;;
    "restart")
        restart_deployments
        ;;
    "port-forward")
        setup_port_forward
        ;;
    "update-secrets")
        update_secrets
        ;;
    "health")
        check_health
        ;;
    "helm-status")
        show_helm_status
        ;;
    "cleanup")
        exec ./scripts/cleanup-deployment.sh
        ;;
    *)
        show_usage
        ;;
esac