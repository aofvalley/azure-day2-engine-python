# Azure Day 2 Engine - Troubleshooting Guide

## Common Issues and Solutions

### 1. ImagePullBackOff Error

**Symptoms:**
- Pods stuck in `ImagePullBackOff` status
- Error: `failed to pull and unpack image`
- Error: `no match for platform in manifest`

**Cause:**
Images were built for ARM64 (Apple Silicon Mac) but AKS nodes require AMD64.

**Solution:**
```bash
./scripts/troubleshoot-deployment.sh
# Choose option 5: "Rebuild images for AMD64"
```

Or manually:
```bash
# Rebuild for correct architecture
docker buildx build --platform linux/amd64 -f docker/backend.Dockerfile -t advconreg.azurecr.io/azure-day2-engine-backend:latest --load .
docker push advconreg.azurecr.io/azure-day2-engine-backend:latest
kubectl delete pods -l component=backend
```

### 2. CrashLoopBackOff - Missing Dependencies

**Symptoms:**
- Pods restart continuously
- Error: `ModuleNotFoundError: No module named 'pydantic_settings'`

**Cause:**
Missing Python dependencies in requirements.txt

**Solution:**
Dependencies have been fixed in requirements.txt:
- `pydantic-settings>=2.0.0,<3.0.0`
- `azure-mgmt-containerservice>=29.0.0`
- `azure-mgmt-rdbms>=10.1.0`

### 3. Azure CLI Authentication Issues

**Symptoms:**
- Error: `Can't get attribute 'NormalizedResponse'`
- ACR login failures

**Cause:**
Corrupted Azure CLI cache (common with Azure CLI 2.71.0+)

**Solution:**
```bash
# Clear Azure CLI cache
rm -rf ~/.azure/msal_http_cache ~/.azure/msal_token_cache.bin
az login
```

### 4. Pod Health Check Failures

**Symptoms:**
- Pods in `Running` state but not `Ready`
- Health check endpoints failing

**Solution:**
```bash
# Check pod logs
kubectl logs -l component=backend
# Port forward to test locally
kubectl port-forward svc/azure-day2-engine-backend 8000:8000
curl http://localhost:8000/health
```

## Quick Diagnostic Commands

```bash
# Check overall status
kubectl get pods -o wide

# Check detailed pod information
kubectl describe pod <pod-name>

# View logs
kubectl logs -f -l component=backend

# Check services
kubectl get services

# Run full troubleshooting
./scripts/troubleshoot-deployment.sh
```

## Architecture Verification

To verify images are built for correct architecture:
```bash
az acr repository show-manifests --name advconreg --repository azure-day2-engine-backend --detail | grep architecture
```

Should show `"architecture": "amd64"` for AKS compatibility.

## Prevention Tips

1. **Always build for AMD64 when targeting AKS:**
   ```bash
   docker buildx build --platform linux/amd64 ...
   ```

2. **Test locally with the same architecture:**
   ```bash
   docker run --platform linux/amd64 <image>
   ```

3. **Keep requirements.txt updated** with all necessary dependencies

4. **Use the updated build-and-push.sh script** which includes all fixes
