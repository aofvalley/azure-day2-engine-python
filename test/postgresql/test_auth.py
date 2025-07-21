import os
from app.core.azure_auth import azure_auth

def test_postgresql_auth():
    try:
        client = azure_auth.get_postgres_client()
        servers = list(client.servers.list())
        print(f"PostgreSQL Auth OK. Found {len(servers)} servers.")
        for server in servers:
            print(f"- {server.name}")
    except Exception as e:
        print(f"PostgreSQL Auth FAILED: {e}")

if __name__ == "__main__":
    test_postgresql_auth()
