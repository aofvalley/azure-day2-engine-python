"""
Azure Day 2 Engine - Frontend Dashboard
======================================

Interactive frontend for demonstrating Azure Day 2 Engine capabilities.
Built with Streamlit for easy API testing and result visualization.
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Azure Day 2 Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #0066cc;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #004080;
        border-bottom: 2px solid #0066cc;
        padding-bottom: 0.5rem;
        margin: 1rem 0;
    }
    
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        color: #155724;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        color: #721c24;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #0066cc;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"

class APIClient:
    """Client for Azure Day 2 Engine API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "raw_response": response.text
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "status_code": 0,
                "data": {},
                "error": str(e),
                "raw_response": ""
            }
    
    # AKS Operations
    def aks_get_status(self, resource_group: str, cluster_name: str) -> Dict[str, Any]:
        """Get AKS cluster status"""
        return self._make_request("GET", f"/AKS/v1/status/{resource_group}/{cluster_name}")
    
    def aks_start_cluster(self, resource_group: str, cluster_name: str) -> Dict[str, Any]:
        """Start AKS cluster"""
        data = {"resource_group": resource_group, "cluster_name": cluster_name}
        return self._make_request("POST", "/AKS/v1/start", data)
    
    def aks_stop_cluster(self, resource_group: str, cluster_name: str) -> Dict[str, Any]:
        """Stop AKS cluster"""
        data = {"resource_group": resource_group, "cluster_name": cluster_name}
        return self._make_request("POST", "/AKS/v1/stop", data)
    
    def aks_cli_command(self, command: str) -> Dict[str, Any]:
        """Execute AKS CLI command"""
        data = {"command": command}
        return self._make_request("POST", "/AKS/v1/cli", data)
    
    # PostgreSQL Operations
    def postgres_get_status(self, resource_group: str, server_name: str) -> Dict[str, Any]:
        """Get PostgreSQL server status"""
        return self._make_request("GET", f"/PSSQL/v1/status/{resource_group}/{server_name}")
    
    def postgres_execute_script(self, resource_group: str, server_name: str, 
                               database_name: str, username: str, password: str, 
                               script_name: str, parameters: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute PostgreSQL script"""
        data = {
            "resource_group": resource_group,
            "server_name": server_name,
            "database_name": database_name,
            "username": username,
            "password": password,
            "script_name": script_name
        }
        if parameters:
            data["parameters"] = parameters
        return self._make_request("POST", "/PSSQL/v1/execute-script", data)
    
    def postgres_cli_command(self, command: str) -> Dict[str, Any]:
        """Execute PostgreSQL CLI command"""
        data = {"command": command}
        return self._make_request("POST", "/PSSQL/v1/cli", data)

def display_response(response: Dict[str, Any], title: str = "API Response"):
    """Display API response in formatted way"""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    
    if response["success"]:
        st.markdown('<div class="success-box">✅ Request Successful</div>', unsafe_allow_html=True)
        
        # Display response data
        if "data" in response and response["data"]:
            data = response["data"]
            
            # Handle different response structures
            if "result" in data and "details" in data.get("result", {}):
                result = data["result"]
                st.write(f"**Status:** {result.get('status', 'Unknown')}")
                st.write(f"**Message:** {result.get('message', 'No message')}")
                st.write(f"**Execution Time:** {result.get('execution_time', 0):.3f} seconds")
                
                # Display details
                details = result.get("details", {})
                if details:
                    st.subheader("Details")
                    
                    # Handle query results specially
                    if "query_results" in details and details["query_results"]:
                        st.subheader("🔍 Query Results")
                        for query in details["query_results"]:
                            st.write(f"**Query {query['query_number']}:** {query['statement'][:100]}...")
                            if query["rows"]:
                                df = pd.DataFrame(query["rows"])
                                st.dataframe(df, use_container_width=True)
                            st.write(f"Row count: {query['row_count']}")
                            st.write("---")
                    else:
                        # Display other details
                        for key, value in details.items():
                            if key != "query_results":
                                if isinstance(value, dict):
                                    st.json(value)
                                else:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                # Display raw data if structure is different
                st.json(data)
                
    else:
        st.markdown('<div class="error-box">❌ Request Failed</div>', unsafe_allow_html=True)
        st.write(f"**Status Code:** {response['status_code']}")
        if "error" in response:
            st.write(f"**Error:** {response['error']}")
        if response.get("data"):
            st.json(response["data"])
    
    # Show raw response in expander
    with st.expander("🔍 Raw Response"):
        st.code(json.dumps(response, indent=2))

def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">⚡ Azure Day 2 Engine</div>', unsafe_allow_html=True)
    st.markdown("**Interactive Dashboard for Azure Operations Management**")
    
    # Initialize API client
    api_client = APIClient(API_BASE_URL)
    
    # Sidebar configuration
    st.sidebar.title("🛠️ Configuration")
    
    # API Health Check
    with st.sidebar:
        st.subheader("API Health")
        if st.button("🔄 Check API Health"):
            try:
                health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if health_response.status_code == 200:
                    st.success("✅ API is healthy")
                else:
                    st.error(f"❌ API unhealthy: {health_response.status_code}")
            except:
                st.error("❌ API not reachable")
    
    # Main tabs
    tab1, tab2 = st.tabs(["🚀 AKS Operations", "🐘 PostgreSQL Operations"])
    
    with tab1:
        aks_operations_ui(api_client)
    
    with tab2:
        postgres_operations_ui(api_client)

def aks_operations_ui(api_client: APIClient):
    """AKS Operations UI"""
    st.markdown('<div class="section-header">🚀 Azure Kubernetes Service Operations</div>', unsafe_allow_html=True)
    
    # AKS Configuration
    col1, col2 = st.columns(2)
    with col1:
        aks_resource_group = st.text_input("Resource Group", value="adv_data_rg", key="aks_rg")
    with col2:
        aks_cluster_name = st.text_input("Cluster Name", value="my-aks-cluster", key="aks_cluster")
    
    # AKS Operations
    st.subheader("Cluster Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Get Cluster Status", use_container_width=True):
            with st.spinner("Getting cluster status..."):
                response = api_client.aks_get_status(aks_resource_group, aks_cluster_name)
                display_response(response, "AKS Cluster Status")
    
    with col2:
        if st.button("▶️ Start Cluster", use_container_width=True):
            with st.spinner("Starting cluster..."):
                response = api_client.aks_start_cluster(aks_resource_group, aks_cluster_name)
                display_response(response, "Start AKS Cluster")
    
    with col3:
        if st.button("⏹️ Stop Cluster", use_container_width=True):
            with st.spinner("Stopping cluster..."):
                response = api_client.aks_stop_cluster(aks_resource_group, aks_cluster_name)
                display_response(response, "Stop AKS Cluster")
    
    # AKS CLI Commands
    st.subheader("Azure CLI Commands")
    
    # Predefined commands
    aks_commands = [
        "az aks list -o table",
        f"az aks show -g {aks_resource_group} -n {aks_cluster_name}",
        f"az aks get-credentials -g {aks_resource_group} -n {aks_cluster_name}",
        "az aks get-versions --location eastus -o table"
    ]
    
    selected_command = st.selectbox("Select predefined command:", ["Custom..."] + aks_commands)
    
    if selected_command == "Custom...":
        aks_cli_command = st.text_input("Enter Azure CLI command:", "az aks list")
    else:
        aks_cli_command = st.text_input("Azure CLI command:", value=selected_command)
    
    if st.button("🔧 Execute AKS CLI Command", use_container_width=True):
        with st.spinner(f"Executing: {aks_cli_command}"):
            response = api_client.aks_cli_command(aks_cli_command)
            display_response(response, "AKS CLI Command Result")

def postgres_operations_ui(api_client: APIClient):
    """PostgreSQL Operations UI"""
    st.markdown('<div class="section-header">🐘 PostgreSQL Operations</div>', unsafe_allow_html=True)
    
    # PostgreSQL Configuration
    col1, col2 = st.columns(2)
    with col1:
        pg_resource_group = st.text_input("Resource Group", value="adv_data_rg", key="pg_rg")
        pg_server_name = st.text_input("Server Name", value="advpsqlfxuk", key="pg_server")
    with col2:
        pg_database_name = st.text_input("Database Name", value="adventureworks", key="pg_db")
        pg_username = st.text_input("Username", value="alfonsod", key="pg_user")
    
    # Server Management
    st.subheader("Server Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Get Server Status", use_container_width=True):
            with st.spinner("Getting server status..."):
                response = api_client.postgres_get_status(pg_resource_group, pg_server_name)
                display_response(response, "PostgreSQL Server Status")
    
    with col2:
        # PostgreSQL CLI Commands section
        st.subheader("Azure CLI Commands")
        
        pg_commands = [
            f"az postgres flexible-server list -g {pg_resource_group}",
            f"az postgres flexible-server show -g {pg_resource_group} -n {pg_server_name}",
            f"az postgres flexible-server backup list -g {pg_resource_group} -n {pg_server_name}",
            "az postgres flexible-server list-versions --location eastus"
        ]
        
        selected_pg_command = st.selectbox("Select predefined command:", ["Custom..."] + pg_commands, key="pg_cli_select")
        
        if selected_pg_command == "Custom...":
            pg_cli_command = st.text_input("Enter Azure CLI command:", "az postgres flexible-server list", key="pg_cli_custom")
        else:
            pg_cli_command = st.text_input("Azure CLI command:", value=selected_pg_command, key="pg_cli_command")
        
        if st.button("🔧 Execute PostgreSQL CLI Command", use_container_width=True):
            with st.spinner(f"Executing: {pg_cli_command}"):
                response = api_client.postgres_cli_command(pg_cli_command)
                display_response(response, "PostgreSQL CLI Command Result")
    
    # SQL Script Execution
    st.subheader("SQL Script Execution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Password input
        pg_password = st.text_input("Password", type="password", key="pg_password")
        
        # Script selection
        available_scripts = ["sample_health_check.sql", "sample_backup_check.sql", "custom_script.sql"]
        selected_script = st.selectbox("Select SQL script:", available_scripts)
        
        # Parameters (optional)
        with st.expander("Script Parameters (Optional)"):
            st.info("Add parameters for script substitution using ${parameter_name} syntax")
            param_key = st.text_input("Parameter name:")
            param_value = st.text_input("Parameter value:")
            parameters = {}
            if param_key and param_value:
                parameters[param_key] = param_value
    
    with col2:
        # Script description based on selection
        script_descriptions = {
            "sample_health_check.sql": """
            **Health Check Script**
            - Database version and current time
            - Database size information  
            - Active connections statistics
            - Table count by schema
            """,
            "sample_backup_check.sql": """
            **Backup Check Script**
            - Backup verification queries
            - Backup monitoring information
            """,
            "custom_script.sql": """
            **Custom Script**
            - Upload your own SQL script to the server
            - Ensure it's placed in app/scripts/sql/
            """
        }
        
        st.markdown(script_descriptions.get(selected_script, "No description available"))
    
    if st.button("🔍 Execute SQL Script", use_container_width=True):
        if not pg_password:
            st.error("Please enter the database password")
        else:
            with st.spinner(f"Executing script: {selected_script}"):
                response = api_client.postgres_execute_script(
                    pg_resource_group, pg_server_name, pg_database_name,
                    pg_username, pg_password, selected_script, parameters
                )
                display_response(response, f"SQL Script Results: {selected_script}")

if __name__ == "__main__":
    main()