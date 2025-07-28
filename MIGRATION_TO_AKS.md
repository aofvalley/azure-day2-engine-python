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

### 3. Configuración de Variables de Entorno (Centralizada)

El proyecto ahora utiliza un sistema centralizado de configuración mediante archivos `.env`:

#### Opción 1: Configuración Interactiva (Recomendada)
```bash
# Ejecutar el asistente de configuración
./scripts/setup-env.sh
```

Este script te guiará paso a paso para configurar todas las variables necesarias.

#### Opción 2: Configuración Manual
```bash
# Copiar el template de configuración
cp .env.example .env

# Editar el archivo .env con tus valores reales
nano .env  # o usa tu editor preferido
```

**Variables requeridas en `.env`:**
```bash
# Azure Configuration
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here
AZURE_SUBSCRIPTION_ID=your-subscription-id-here

# AKS and Container Registry Configuration
ACR_NAME=advaks
AKS_CLUSTER=adv_aks
AKS_RESOURCE_GROUP=your-resource-group-here
IMAGE_TAG=latest
NAMESPACE=default
HELM_RELEASE_NAME=azure-day2-engine
```

#### Validación Automática
```bash
# Verificar configuración (opcional)
source scripts/load-env.sh
```

**Ventajas del sistema centralizado:**
- ✅ **Única fuente de verdad**: Todas las variables en un solo archivo
- ✅ **Validación automática**: Los scripts verifican automáticamente las configuraciones
- ✅ **Seguridad mejorada**: Las credenciales se muestran enmascaradas
- ✅ **Sin exports manuales**: No necesitas configurar variables de entorno manualmente
- ✅ **Consistencia**: Todos los scripts usan la misma configuración

## 🚀 Proceso de Migración

### Paso 1: Preparar el Entorno

```bash
# 1. Clonar o actualizar el repositorio
cd ~/Desarrollo/azure-day2-engine-python

# 2. Verificar estructura del proyecto
ls -la
# Deberías ver: docker/, helm-chart/, scripts/, app/, frontend/

# 3. Configurar variables de entorno (NUEVO - Sistema Centralizado)
# Opción A: Configuración interactiva (recomendada)
./scripts/setup-env.sh

# Opción B: Configuración manual
cp .env.example .env
# Editar .env con tus valores reales

# 4. Verificar configuración automáticamente
source scripts/load-env.sh

# 5. Verificar conectividad Azure
az account show
az acr list --query "[].{Name:name,LoginServer:loginServer}" -o table
```

### Paso 2: Construir y Subir Imágenes Docker

```bash
# 1. Ejecutar el script de build y push (carga automáticamente .env)
./scripts/build-and-push.sh

# El script ejecutará automáticamente:
# - Carga de variables desde .env
# - Validación de configuración
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
# 1. Ejecutar el script de deployment con Helm (carga automáticamente .env)
./scripts/deploy-to-aks.sh

# El script ejecutará automáticamente:
# - Carga y validación de variables desde .env
# - Verificación de prerequisitos (kubectl, Helm, Azure CLI)
# - Configuración de kubectl con AKS
# - Creación/verificación del namespace
# - Preparación automática de valores de Helm
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
# Verificar configuración actual
source scripts/load-env.sh

# Actualizar credenciales en .env
nano .env  # Editar las credenciales incorrectas

# Aplicar cambios usando el script de operaciones (carga automáticamente .env)
./scripts/aks-operations.sh update-secrets

# Alternativamente, usar Helm directamente después de actualizar .env
source scripts/load-env.sh
helm upgrade azure-day2-engine ./helm-chart -n $NAMESPACE \
  --set global.azure.clientId=$AZURE_CLIENT_ID \
  --set global.azure.tenantId=$AZURE_TENANT_ID \
  --set global.azure.clientSecret=$AZURE_CLIENT_SECRET \
  --set global.azure.subscriptionId=$AZURE_SUBSCRIPTION_ID
```

#### 5. Problemas de Configuración de Variables de Entorno
```bash
# Problema: Variables no configuradas o con valores por defecto
# Síntomas: "Environment validation failed" al ejecutar scripts

# Solución 1: Usar configuración interactiva
./scripts/setup-env.sh

# Solución 2: Verificar y corregir .env manualmente
cat .env  # Ver configuración actual
nano .env  # Editar valores incorrectos

# Verificar configuración después de los cambios
source scripts/load-env.sh

# Problema: .env no existe
# Síntomas: ".env file not found"

# Solución: Crear desde template
cp .env.example .env
./scripts/setup-env.sh

# Problema: Variables enmascaradas muestran valores incorrectos
# Síntomas: Credenciales tienen longitud incorrecta

# Verificar longitudes esperadas:
# - AZURE_TENANT_ID: ~36 caracteres (UUID)
# - AZURE_CLIENT_ID: ~36 caracteres (UUID) 
# - AZURE_SUBSCRIPTION_ID: ~36 caracteres (UUID)
# - AZURE_CLIENT_SECRET: variable (generalmente 40+ caracteres)
```

#### 6. Problemas con Helm
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

## 🎉 ¡Migración Completada con Helm y Configuración Centralizada!

Tu Azure Day 2 Engine ahora está ejecutándose en AKS con Helm y gestión moderna de configuración:

### ✅ **Características Implementadas**
- ✅ **Backend API optimizado** (1 réplica configurable)
- ✅ **Frontend dashboard** accesible externamente
- ✅ **Gestión simplificada** con Helm Charts
- ✅ **Configuración centralizada** mediante archivos `.env`
- ✅ **Validación automática** de variables de entorno
- ✅ **Scripts inteligentes** con carga automática de configuración
- ✅ **Seguridad mejorada** con enmascaramiento de credenciales
- ✅ **Actualizaciones y rollbacks** sencillos
- ✅ **Servicios separados** y escalables independientemente
- ✅ **Monitoreo y logging** configurado

### 🚀 **Ventajas del Nuevo Sistema**

**Helm Benefits:**
- Gestión de configuración centralizada
- Versionado de deployments
- Rollbacks automáticos
- Plantillas reutilizables
- Actualizaciones incrementales

**Sistema de Variables de Entorno:**
- 🎯 **Única fuente de verdad**: Archivo `.env` centralizado
- 🔒 **Seguridad mejorada**: Credenciales enmascaradas en logs
- ⚡ **Automatización completa**: Sin exports manuales necesarios
- 🛡️ **Validación robusta**: Verificación automática de configuraciones
- 📋 **Experiencia mejorada**: Scripts más intuitivos y fáciles de usar

### 🔄 **Flujo de Trabajo Simplificado**
```bash
# 1. Configuración una sola vez
./scripts/setup-env.sh

# 2. Build y deploy sin configuración adicional
./scripts/build-and-push.sh
./scripts/deploy-to-aks.sh

# 3. Operaciones sin exports manuales
./scripts/aks-operations.sh status
```

El backend es el componente de valor con las APIs, mientras que el frontend sirve como herramienta de demostración y pruebas.