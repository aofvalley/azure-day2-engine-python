# Pruebas de Autenticación Azure

Este directorio contiene scripts para validar la autenticación y acceso a recursos AKS y PostgreSQL usando la App Registration configurada en Azure.

## Requisitos previos
- Python 3.8+
- Entorno virtual activado (opcional pero recomendado)
- Variables de entorno configuradas:
  - `AZURE_CLIENT_ID`
  - `AZURE_TENANT_ID`
  - `AZURE_CLIENT_SECRET`
  - `AZURE_SUBSCRIPTION_ID` (si tu código lo requiere)
- Dependencias instaladas:
  - `pip install -r ../requirements.txt`

## Ejecución de pruebas

### 1. Prueba de autenticación AKS
```bash
python test/aks/test_auth.py
```

### 2. Prueba de autenticación PostgreSQL
```bash
python test/postgresql/test_auth.py
```

## Resultados
- Si la autenticación es exitosa, se mostrará el número y nombre de los recursos encontrados.
- Si falla, se mostrará el error correspondiente.

## Notas
- Asegúrate de que tu App Registration tenga permisos OWNER sobre los recursos.
- Si usas un entorno virtual, actívalo antes de ejecutar los scripts:
  ```bash
  source ../venv/bin/activate
  ```
