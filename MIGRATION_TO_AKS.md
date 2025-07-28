# Azure Day 2 Engine - Migración a AKS con Helm

Guía completa paso a paso para migrar Azure Day 2 Engine a Azure Kubernetes Service (AKS) usando Helm Charts con servicios separados para backend y frontend.

## 📋 Arquitectura de la Migración

La migración separa el proyecto en dos componentes independientes:

### Backend (API)
- **Puerto**: 8000
- **Imagen**: `${ACR_NAME}.azurecr.io/azure-day2-engine-backend:${TAG}`
- **Réplicas**: 1 (optimizado para recursos)
- **Servicio**: ClusterIP (interno)
- **Recursos**: 256Mi RAM, 250m CPU (request) / 512Mi RAM, 500m CPU (limit)

### Frontend (Dashboard)
- **Puerto**: 8501
- **Imagen**: `${ACR_NAME}.azurecr.io/azure-day2-engine-frontend:${TAG}`
- **Réplicas**: 1 (demo/presentación)
- **Servicio**: LoadBalancer (acceso externo)
- **Recursos**: 128Mi RAM, 100m CPU (request) / 256Mi RAM, 200m CPU (limit)

## 🎯 Prerequisitos

### 1. Azure Resources
- **AKS Cluster**: `adv_aks` en el resource group especificado
- **Azure Container Registry**: `advaks` (o configurar ACR_NAME)
- **Azure CLI**: Instalado y configurado (`az --version`)
- **kubectl**: Instalado y configurado (`kubectl version`)

### 2. Helm Installation
Instalar Helm v3:
```bash
# Para macOS
brew install helm

# Para Linux
curl https://get.helm.sh/helm-v3.12.3-linux-amd64.tar.gz | tar xz
sudo mv linux-amd64/helm /usr/local/bin/helm

# Verificar instalación
helm version
```

### 3. Credenciales Azure
Configurar las siguientes variables de entorno:
```bash
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
```

### 4. Configuración AKS y Helm
```bash
export ACR_NAME="advaks"                         # Nombre de tu ACR
export AKS_CLUSTER="adv_aks"                    # Nombre de tu cluster AKS
export AKS_RESOURCE_GROUP="your-rg-name"        # Resource group de AKS
export IMAGE_TAG="latest"                        # Tag de las imágenes
export NAMESPACE="default"                       # Kubernetes namespace
export HELM_RELEASE_NAME="azure-day2-engine"    # Nombre del release de Helm
```

## 🚀 Proceso de Migración

### Paso 1: Preparar el Entorno

```bash
# 1. Clonar o actualizar el repositorio
cd ~/Desarrollo/azure-day2-engine-python

# 2. Verificar estructura del proyecto
ls -la
# Deberías ver: docker/, kubernetes/, helm-chart/, scripts/, app/, frontend/

# 3. Configurar variables de entorno
export ACR_NAME="advaks"
export AKS_CLUSTER="adv_aks"
export AKS_RESOURCE_GROUP="tu-resource-group"
export IMAGE_TAG="v1.0.0"

# 4. Verificar conectividad Azure
az account show
az acr list --query "[].{Name:name,LoginServer:loginServer}" -o table
```

### Paso 2: Construir y Subir Imágenes Docker

```bash
# 1. Ejecutar el script de build y push
./scripts/build-and-push.sh

# El script ejecutará:
# - Verificación de prerequisitos
# - Login a ACR
# - Build de imagen backend
# - Build de imagen frontend  
# - Push de ambas imágenes
# - Verificación en registry
```

**Salida esperada:**
```
🏗️ Azure Day 2 Engine - Docker Build and Push
==================================================
✅ Prerequisites verified
✅ Logged in to ACR: advaks
✅ Backend image built: advaks.azurecr.io/azure-day2-engine-backend:latest
✅ Frontend image built: advaks.azurecr.io/azure-day2-engine-frontend:latest
✅ Backend image pushed to registry
✅ Frontend image pushed to registry
✅ Build and push completed successfully!
```

### Paso 3: Desplegar a AKS con Helm

```bash
# 1. Ejecutar el script de deployment con Helm
./scripts/deploy-to-aks.sh

# El script ejecutará:
# - Verificación de prerequisitos (kubectl, Helm, Azure CLI)
# - Configuración de kubectl con AKS
# - Creación/verificación del namespace
# - Preparación de valores de Helm
# - Instalación/actualización del Helm chart
# - Verificación de deployments
```

**Salida esperada:**
```
🚀 Azure Day 2 Engine - AKS Deployment (Helm)
==============================================
✅ Prerequisites verified
✅ AKS credentials configured
✅ Connected to AKS cluster: adv_aks
✅ Namespace 'default' ready
✅ Azure credentials configured for Helm deployment
✅ Helm release installed successfully
✅ All deployments are ready!
```

### Paso 4: Verificar el Despliegue

```bash
# 1. Verificar el release de Helm
helm list -n default

# 2. Ver status detallado del release
helm status azure-day2-engine -n default

# 3. Verificar pods
kubectl get pods -l app.kubernetes.io/name=azure-day2-engine

# 4. Verificar servicios
kubectl get services -l app.kubernetes.io/name=azure-day2-engine

# 5. Verificar deployments
kubectl get deployments -l app.kubernetes.io/name=azure-day2-engine

# 6. Obtener IP externa del frontend
kubectl get service azure-day2-engine-frontend-service

# 7. Ver logs del backend
kubectl logs -l app.kubernetes.io/name=azure-day2-engine,component=backend

# 8. Ver logs del frontend
kubectl logs -l app.kubernetes.io/name=azure-day2-engine,component=frontend
```

### Paso 5: Probar la Aplicación

```bash
# 1. Test de salud del backend (port-forward temporal)
kubectl port-forward service/azure-day2-engine-backend-service 8080:80 &
curl http://localhost:8080/health

# 2. Acceder al frontend via IP externa
# Esperar a que se asigne la IP externa (puede tomar 2-5 minutos)
kubectl get service azure-day2-engine-frontend-service -w

# 3. Una vez asignada, acceder via navegador
# http://<EXTERNAL-IP>/
```

## 🛠️ Configuración Avanzada con Helm

### Personalizar Valores de Helm

Crear un archivo `custom-values.yaml` para personalización:

```yaml
# custom-values.yaml
backend:
  replicaCount: 2  # Cambiar a más réplicas si es necesario
  resources:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

frontend:
  replicaCount: 1
  service:
    type: LoadBalancer  # o NodePort, ClusterIP

global:
  registry: "your-acr.azurecr.io"
  imageTag: "v1.0.0"
  azure:
    clientId: "your-real-client-id"
    tenantId: "your-real-tenant-id"
    clientSecret: "your-real-secret"
    subscriptionId: "your-real-subscription"
```

Aplicar la configuración personalizada:
```bash
helm upgrade azure-day2-engine ./helm-chart -n default -f custom-values.yaml
```

### Scaling con Helm

```bash
# Escalar backend usando Helm
helm upgrade azure-day2-engine ./helm-chart -n default \
  --set backend.replicaCount=3

# Actualizar recursos usando Helm
helm upgrade azure-day2-engine ./helm-chart -n default \
  --set backend.resources.requests.cpu=500m \
  --set backend.resources.limits.memory=1Gi

# Configurar auto-scaling (después del deployment)
kubectl autoscale deployment azure-day2-engine-backend --cpu-percent=70 --min=1 --max=5
```

### Monitoreo y Logging con Helm

```bash
# Ver status del Helm release
helm status azure-day2-engine -n default

# Ver historial de releases
helm history azure-day2-engine -n default

# Ver logs en tiempo real
kubectl logs -f deployment/azure-day2-engine-backend

# Describir pod para troubleshooting
kubectl describe pod <pod-name>

# Verificar events del namespace
kubectl events --sort-by=.metadata.creationTimestamp

# Usar el script de operaciones
./scripts/aks-operations.sh status
./scripts/aks-operations.sh logs
./scripts/aks-operations.sh helm-status
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. ImagePullBackOff
```bash
# Verificar que las imágenes existen en ACR
az acr repository list --name $ACR_NAME

# Verificar permisos de AKS en ACR
az aks check-acr --resource-group $AKS_RESOURCE_GROUP --name $AKS_CLUSTER --acr $ACR_NAME.azurecr.io
```

#### 2. Backend no responde
```bash
# Verificar configuración de secrets
kubectl get secret azure-credentials -o yaml

# Verificar variables de entorno en pods
kubectl exec deployment/azure-day2-engine-backend -- env | grep AZURE

# Verificar logs detallados
kubectl logs deployment/azure-day2-engine-backend --previous
```

#### 3. Frontend no accesible
```bash
# Verificar estado del LoadBalancer
kubectl describe service azure-day2-engine-frontend-service

# Verificar si el frontend puede conectar al backend
kubectl exec deployment/azure-day2-engine-frontend -- curl -I azure-day2-engine-backend-service
```

#### 4. Problemas de Azure Credentials
```bash
# Actualizar credenciales usando Helm upgrade
helm upgrade azure-day2-engine ./helm-chart -n default \
  --set global.azure.clientId=$AZURE_CLIENT_ID \
  --set global.azure.tenantId=$AZURE_TENANT_ID \
  --set global.azure.clientSecret=$AZURE_CLIENT_SECRET \
  --set global.azure.subscriptionId=$AZURE_SUBSCRIPTION_ID

# O usar el script de operaciones
export AZURE_CLIENT_ID="new-client-id"
export AZURE_TENANT_ID="new-tenant-id" 
export AZURE_CLIENT_SECRET="new-client-secret"
export AZURE_SUBSCRIPTION_ID="new-subscription-id"
./scripts/aks-operations.sh update-secrets
```

#### 5. Problemas con Helm
```bash
# Ver releases de Helm
helm list -n default

# Ver status detallado
helm status azure-day2-engine -n default

# Ver historial de cambios
helm history azure-day2-engine -n default

# Rollback a una versión anterior
helm rollback azure-day2-engine 1 -n default

# Verificar sintaxis del chart
helm lint ./helm-chart

# Debug del template
helm template azure-day2-engine ./helm-chart --debug
```

## 🧹 Limpieza y Rollback con Helm

### Limpiar Deployment Completo
```bash
# Ejecutar script de limpieza (usa Helm uninstall)
./scripts/cleanup-deployment.sh

# O manualmente con Helm
helm uninstall azure-day2-engine -n default

# Verificar que se eliminó todo
kubectl get all -l app.kubernetes.io/name=azure-day2-engine
```

### Rollback a Versión Anterior con Helm
```bash
# Ver historial de releases de Helm
helm history azure-day2-engine -n default

# Rollback a la versión anterior
helm rollback azure-day2-engine -n default

# Rollback a una versión específica
helm rollback azure-day2-engine 2 -n default

# Verificar el rollback
helm status azure-day2-engine -n default
```

## 📊 Configuración de Producción

### Recursos Recomendados para Producción

```yaml
# Backend - Producción
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

# Frontend - Producción
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "400m"
```

### Configuración de Auto-scaling
```bash
# HPA para backend
kubectl autoscale deployment azure-day2-engine-backend \
  --cpu-percent=70 --min=2 --max=10

# Verificar HPA
kubectl get hpa
```

### Backup de Configuración
```bash
# Exportar configuración actual
kubectl get all,secrets,configmaps -l app=azure-day2-engine -o yaml > azure-day2-engine-backup.yaml
```

## 🔐 Seguridad

### Network Policies (Opcional)
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: azure-day2-engine-netpol
spec:
  podSelector:
    matchLabels:
      app: azure-day2-engine
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: azure-day2-engine
  egress:
  - to: []
```

### Pod Security Context
Los Dockerfiles ya incluyen usuarios no-root. Para mayor seguridad:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
```

## 📈 Resultados Esperados

### URLs de Acceso
- **Frontend Dashboard**: `http://<EXTERNAL-IP>/`
- **Backend API Docs**: Port-forward a `http://localhost:8080/docs`
- **Health Check**: Port-forward a `http://localhost:8080/health`

### Estructura Final en AKS con Helm
```
azure-day2-engine/ (Helm Release)
├── Backend Deployment (1 replica - optimizado)
│   └── Pod 1: backend-xxx-aaa
├── Frontend Deployment (1 replica)
│   └── Pod 1: frontend-xxx-ccc
├── Services
│   ├── backend-service (ClusterIP)
│   └── frontend-service (LoadBalancer)
├── Helm Management
│   ├── Release: azure-day2-engine
│   ├── Chart Version: 1.0.0
│   └── Values: Configurables via upgrade
└── Resources
    ├── ServiceAccount
    ├── Secret (Azure credentials)
    └── ConfigMap (SQL scripts)
```

## 🎉 ¡Migración Completada con Helm!

Tu Azure Day 2 Engine ahora está ejecutándose en AKS con Helm:
- ✅ Backend API optimizado (1 réplica configurable)
- ✅ Frontend dashboard accesible externamente
- ✅ Gestión simplificada con Helm Charts
- ✅ Configuración versionada y reproducible
- ✅ Actualizaciones y rollbacks sencillos
- ✅ Servicios separados y escalables independientemente
- ✅ Scripts de mantenimiento actualizados para Helm
- ✅ Monitoreo y logging configurado

**Ventajas de usar Helm:**
- Gestión de configuración centralizada
- Versionado de deployments
- Rollbacks automáticos
- Plantillas reutilizables
- Actualizaciones incrementales

El backend es el componente de valor con las APIs, mientras que el frontend sirve como herramienta de demostración y pruebas.