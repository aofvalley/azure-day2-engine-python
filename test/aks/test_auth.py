import os
from app.core.azure_auth import azure_auth

def test_aks_auth():
    try:
        client = azure_auth.get_aks_client()
        clusters = list(client.managed_clusters.list())
        print(f"AKS Auth OK. Found {len(clusters)} clusters.")
        for cluster in clusters:
            print(f"- {cluster.name}")
    except Exception as e:
        print(f"AKS Auth FAILED: {e}")

if __name__ == "__main__":
    test_aks_auth()
