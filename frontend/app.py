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
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd
from auth import require_authentication, make_authenticated_request, get_api_base_url

# Try to import plotly, fallback gracefully if not available
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly not installed. Performance charts will be disabled. Run: pip install plotly")

# Page configuration
st.set_page_config(
    page_title="Azure Day 2 Engine | Internal Developer Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS - only for IDP header and cards, using Streamlit defaults for everything else
st.markdown("""
<style>
    /* Only essential IDP styling - let Streamlit handle the rest */
    
    /* IDP Header */
    .idp-header {
        background: linear-gradient(90deg, #0066cc 0%, #004080 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .idp-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .idp-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Dashboard cards - minimal styling */
    .dashboard-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    
    .dashboard-card h4 {
        color: #0066cc;
        margin: 0 0 1rem 0;
        font-weight: 600;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        border-left: 4px solid #0066cc;
        margin: 0.5rem 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0066cc;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #6c757d;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-change {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive {
        color: #28a745;
    }
    
    .metric-change.negative {
        color: #dc3545;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .status-healthy {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .status-loading {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #212529;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #0066cc;
        position: relative;
    }
    
    .section-header::before {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 50px;
        height: 3px;
        background: #28a745;
    }
    
    /* Resource cards */
    .resource-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 4px solid #0066cc;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .resource-card h4 {
        color: #0066cc;
        margin: 0 0 1rem 0;
        font-weight: 600;
    }
    
    /* Activity timeline */
    .activity-item {
        background: white;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .activity-item strong {
        color: #0066cc;
    }
    
    .activity-item small {
        color: #6c757d;
    }
    
    /* Keep ALL Streamlit controls visible, only hide footer */
    footer {visibility: hidden;}
    
    /* Hide the "Made with Streamlit" link if present */
    a[href*="streamlit.io"] {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .idp-header h1 {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
        
        .dashboard-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
import os

# API Configuration - use environment variable for Kubernetes deployment
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

class APIClient:
    """Client for Azure Day 2 Engine API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to API with authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication headers if user is authenticated
        if st.session_state.get("authenticated", False):
            token = st.session_state.get("access_token")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle authentication errors
            if response.status_code == 401:
                st.error("🔒 Authentication failed. Please login again.")
                # Clear authentication and force re-login
                if "authenticated" in st.session_state:
                    del st.session_state["authenticated"]
                st.rerun()
            
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
    
    def postgres_list_servers(self, resource_group: Optional[str] = None) -> Dict[str, Any]:
        """List PostgreSQL servers"""
        data = {}
        if resource_group:
            data["resource_group"] = resource_group
        return self._make_request("POST", "/PSSQL/v1/servers/list", data)
    
    def postgres_start_server(self, resource_group: str, server_name: str) -> Dict[str, Any]:
        """Start PostgreSQL server"""
        data = {"resource_group": resource_group, "server_name": server_name}
        return self._make_request("POST", "/PSSQL/v1/servers/start", data)
    
    def postgres_stop_server(self, resource_group: str, server_name: str) -> Dict[str, Any]:
        """Stop PostgreSQL server"""
        data = {"resource_group": resource_group, "server_name": server_name}
        return self._make_request("POST", "/PSSQL/v1/servers/stop", data)
    
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

def create_dashboard_overview():
    """Create IDP dashboard overview with metrics and monitoring"""
    st.markdown('<div class="section-header">📊 Platform Overview</div>', unsafe_allow_html=True)
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2</div>
            <div class="metric-label">Active Services</div>
            <div class="metric-change positive">↑ 100% Uptime</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">156</div>
            <div class="metric-label">Operations Today</div>
            <div class="metric-change positive">↑ 23%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">0.85s</div>
            <div class="metric-label">Avg Response Time</div>
            <div class="metric-change positive">↓ 12%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">99.9%</div>
            <div class="metric-label">Success Rate</div>
            <div class="metric-change positive">↑ 0.1%</div>
        </div>
        """, unsafe_allow_html=True)

def create_service_health_widget():
    """Create service health monitoring widget"""
    st.markdown('<div class="section-header">🛡️ Service Health Monitor</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="resource-card">
            <h4>🚀 Azure Kubernetes Service</h4>
            <div class="status-indicator status-healthy">
                ✓ Operational
            </div>
            <p style="margin-top: 1rem; color: #6c757d;">
                • API Response: <strong>245ms</strong><br>
                • Last Check: <strong>30s ago</strong><br>
                • Operations: <strong>89 today</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="resource-card">
            <h4>🐘 PostgreSQL Service</h4>
            <div class="status-indicator status-healthy">
                ✓ Operational  
            </div>
            <p style="margin-top: 1rem; color: #6c757d;">
                • API Response: <strong>189ms</strong><br>
                • Last Check: <strong>15s ago</strong><br>
                • Operations: <strong>67 today</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

def create_activity_timeline():
    """Create recent activity timeline"""
    st.markdown('<div class="section-header">🕰️ Recent Activity</div>', unsafe_allow_html=True)
    
    # Sample activity data
    activities = [
        {"time": "2 min ago", "action": "AKS Cluster Status Check", "user": "admin", "status": "success"},
        {"time": "5 min ago", "action": "PostgreSQL Health Check", "user": "developer", "status": "success"},
        {"time": "12 min ago", "action": "Database Backup Verification", "user": "admin", "status": "success"},
        {"time": "23 min ago", "action": "AKS Node Scale Operation", "user": "devops", "status": "warning"},
        {"time": "35 min ago", "action": "SQL Script Execution", "user": "developer", "status": "success"},
    ]
    
    for activity in activities:
        status_class = f"status-{activity['status']}"
        icon = "✓" if activity['status'] == 'success' else "⚠️" if activity['status'] == 'warning' else "❌"
        border_color = '#28a745' if activity['status'] == 'success' else '#ffc107' if activity['status'] == 'warning' else '#dc3545'
        
        st.markdown(f"""
        <div class="activity-item" style="border-left: 4px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #0066cc;">{activity['action']}</strong><br>
                    <small style="color: #6c757d;">by {activity['user']} • {activity['time']}</small>
                </div>
                <div class="status-indicator {status_class}">
                    {icon} {activity['status'].title()}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_performance_chart():
    """Create performance monitoring chart"""
    st.markdown('<div class="section-header">📈 Performance Metrics</div>', unsafe_allow_html=True)
    
    if not PLOTLY_AVAILABLE:
        # Fallback without plotly - using Streamlit native components
        st.markdown("""
        <div class="dashboard-card">
            <h4>📊 Performance Overview</h4>
            <p><strong>AKS Service:</strong> Avg 245ms response time</p>
            <p><strong>PostgreSQL Service:</strong> Avg 189ms response time</p>
            <p><em>Install plotly for interactive charts: <code>pip install plotly</code></em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create simple metrics using streamlit native components
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AKS Avg Response", "245ms", delta="-12ms")
        with col2:
            st.metric("PostgreSQL Avg Response", "189ms", delta="-8ms")
        return
    
    # Generate sample performance data
    import random
    from datetime import datetime, timedelta
    
    times = [datetime.now() - timedelta(minutes=x) for x in range(60, 0, -5)]
    aks_response_times = [random.uniform(200, 400) for _ in times]
    postgres_response_times = [random.uniform(150, 300) for _ in times]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=aks_response_times,
        mode='lines+markers',
        name='AKS Response Time',
        line=dict(color='#0066cc', width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=times,
        y=postgres_response_times,
        mode='lines+markers', 
        name='PostgreSQL Response Time',
        line=dict(color='#28a745', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=dict(
            text="API Response Times (Last Hour)",
            font=dict(size=16, color='#212529')
        ),
        xaxis_title="Time",
        yaxis_title="Response Time (ms)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            size=12,
            color='#212529'
        ),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(color='#212529')
        ),
        xaxis=dict(
            title_font=dict(color='#212529'),
            tickfont=dict(color='#212529')
        ),
        yaxis=dict(
            title_font=dict(color='#212529'),
            tickfont=dict(color='#212529')
        )
    )
    
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0,0,0,0.1)',
        title_font_color='#212529',
        tickfont_color='#212529'
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(0,0,0,0.1)',
        title_font_color='#212529',
        tickfont_color='#212529'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_response(response: Dict[str, Any], title: str = "Operation Result"):
    """Display API response using Streamlit native components"""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    
    if response["success"]:
        st.success("✅ Operation Successful")
        
        # Display response data using Streamlit native components
        if "data" in response and response["data"]:
            data = response["data"]
            
            # Handle different response structures
            if "result" in data and "details" in data.get("result", {}):
                result = data["result"]
                
                # Create metrics row for execution details using Streamlit native
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", result.get('status', 'Unknown'))
                with col2:
                    exec_time = result.get('execution_time', 0)
                    st.metric("Execution Time", f"{exec_time:.3f}s")
                with col3:
                    st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
                
                if result.get('message'):
                    st.info(f"📝 {result['message']}")
                
                # Display details using Streamlit native components
                details = result.get("details", {})
                if details:
                    st.subheader("📊 Operation Details")
                    
                    # Handle query results specially
                    if "query_results" in details and details["query_results"]:
                        st.subheader("🔍 Query Results")
                        for i, query in enumerate(details["query_results"]):
                            with st.expander(f"Query {query['query_number']}: {query['statement'][:80]}...", expanded=i==0):
                                if query["rows"]:
                                    df = pd.DataFrame(query["rows"])
                                    st.dataframe(df, use_container_width=True, height=300)
                                    st.caption(f"Returned {query['row_count']} rows")
                                else:
                                    st.info("No rows returned")
                    else:
                        # Display other details in organized way using Streamlit native
                        for key, value in details.items():
                            if key != "query_results":
                                if isinstance(value, dict):
                                    with st.expander(f"📄 {key.replace('_', ' ').title()}"):
                                        st.json(value)
                                else:
                                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            else:
                # Display raw data if structure is different
                with st.expander("📄 Response Data"):
                    st.json(data)
                
    else:
        st.error("❌ Operation Failed")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status Code", response['status_code'])
        with col2:
            st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
        
        if "error" in response:
            st.error(f"🚨 **Error Details:** {response['error']}")
        
        if response.get("data"):
            with st.expander("📄 Error Data"):
                st.json(response["data"])
    
    # Show raw response in expander using Streamlit native
    with st.expander("🔍 Raw API Response"):
        st.json(response)

def main():
    """Main IDP Application"""
    
    # Require authentication before showing main app
    require_authentication()
    
    # Professional IDP Header
    st.markdown("""
    <div class="idp-header">
        <h1>🏗️ Azure Day 2 Engine</h1>
        <p>Internal Developer Platform | Operations Management & Automation</p>
        <p><em>Secure Access ✓</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize API client
    api_client = APIClient(API_BASE_URL)
    
    # Enhanced Sidebar using Streamlit native components
    with st.sidebar:
        st.markdown("## 🛠️ Control Center")
        
        # Environment selector
        environment = st.selectbox(
            "🌍 Environment",
            ["Development", "Staging", "Production"],
            index=0
        )
        
        # API Health Check
        st.markdown("### 🛡️ System Health")
        
        if st.button("🔄 Health Check", use_container_width=True):
            with st.spinner("Checking system health..."):
                try:
                    health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                    if health_response.status_code == 200:
                        st.success("✓ All Systems Operational")
                    else:
                        st.error(f"❌ System Unhealthy ({health_response.status_code})")
                except:
                    st.error("❌ API Unreachable")
        
        # Quick stats in sidebar
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("API Endpoint", API_BASE_URL.split("//")[1])
        st.metric("Environment", environment)
        st.metric("Session Time", f"{int(time.time() % 3600 / 60)}min")
        
        # Resource shortcuts
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.markdown("""
        - [📄 API Documentation](http://localhost:8000/docs)
        - [🔍 Health Endpoint](http://localhost:8000/health)
        - [📈 Metrics Dashboard](http://localhost:8000/metrics)
        - [📝 ReDoc](http://localhost:8000/redoc)
        """)
    
    # Main navigation using Streamlit native radio buttons
    selected_tab = st.radio(
        "Navigate to:",
        ["🏠 Dashboard", "🚀 AKS Operations", "🐘 PostgreSQL Operations"],
        horizontal=True
    )
    
    if selected_tab == "🏠 Dashboard":
        dashboard_ui(api_client)
    elif selected_tab == "🚀 AKS Operations":
        aks_operations_ui(api_client)
    elif selected_tab == "🐘 PostgreSQL Operations":
        postgres_operations_ui(api_client)

def dashboard_ui(api_client: APIClient):
    """Main dashboard with IDP overview"""
    # Dashboard overview metrics
    create_dashboard_overview()
    
    # Two column layout for monitoring widgets
    col1, col2 = st.columns([2, 1])
    
    with col1:
        create_performance_chart()
    
    with col2:
        create_service_health_widget()
    
    # Activity timeline
    create_activity_timeline()

def aks_operations_ui(api_client: APIClient):
    """Enhanced AKS Operations UI with non-blocking operations"""
    st.markdown('<div class="section-header">🚀 Azure Kubernetes Service Operations</div>', unsafe_allow_html=True)
    
    # Quick status overview using Streamlit native
    st.markdown("""
    <div class="dashboard-card">
        <h4>📊 AKS Service Overview</h4>
        <p>Manage and monitor your Azure Kubernetes Service clusters with enterprise-grade operations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AKS Configuration using Streamlit native
    st.subheader("🔧 Cluster Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        aks_resource_group = st.text_input(
            "📁 Resource Group", 
            value="my_aks_rg", 
            key="aks_rg",
            help="Azure Resource Group containing the AKS cluster"
        )
    with col2:
        aks_cluster_name = st.text_input(
            "🏗️ Cluster Name", 
            value="my-aks-cluster", 
            key="aks_cluster",
            help="Name of the AKS cluster to manage"
        )
    
    # AKS Operations using Streamlit native
    st.subheader("🎮 Cluster Operations")
    st.write("Execute critical operations on your AKS cluster infrastructure.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Get Status", use_container_width=True, type="primary"):
            with st.spinner("🔍 Retrieving cluster status..."):
                start_time = time.time()
                response = api_client.aks_get_status(aks_resource_group, aks_cluster_name)
                execution_time = time.time() - start_time
                st.success(f"Status retrieved in {execution_time:.2f}s")
                display_response(response, f"📊 AKS Cluster Status - {aks_cluster_name}")
    
    with col2:
        if st.button("▶️ Start Cluster", use_container_width=True):
            if st.session_state.get('confirm_start', False):
                # Show immediate feedback and user guidance
                st.info("🚀 Sending start command to Azure...")
                
                # Execute the operation without blocking UI with spinner
                start_time = time.time()
                response = api_client.aks_start_cluster(aks_resource_group, aks_cluster_name)
                execution_time = time.time() - start_time
                
                if response["success"]:
                    st.success(f"✅ Start command sent successfully in {execution_time:.2f}s")
                    st.info("💡 **The cluster is now starting.** This process takes 5-10 minutes. Use 'Get Status' to monitor progress or check the Azure portal.")
                else:
                    st.error(f"❌ Start operation failed in {execution_time:.2f}s")
                
                display_response(response, f"▶️ Start AKS Cluster - {aks_cluster_name}")
                st.session_state['confirm_start'] = False
            else:
                st.warning("⚠️ Click again to confirm cluster start operation")
                st.session_state['confirm_start'] = True
    
    with col3:
        if st.button("⏹️ Stop Cluster", use_container_width=True):
            if st.session_state.get('confirm_stop', False):
                # Show immediate feedback and user guidance
                st.info("⏹️ Sending stop command to Azure...")
                
                # Execute the operation without blocking UI with spinner
                start_time = time.time()
                response = api_client.aks_stop_cluster(aks_resource_group, aks_cluster_name)
                execution_time = time.time() - start_time
                
                if response["success"]:
                    st.success(f"✅ Stop command sent successfully in {execution_time:.2f}s")
                    st.info("💡 **The cluster is now stopping.** This process takes 3-5 minutes. Use 'Get Status' to monitor progress or check the Azure portal.")
                else:
                    st.error(f"❌ Stop operation failed in {execution_time:.2f}s")
                
                display_response(response, f"⏹️ Stop AKS Cluster - {aks_cluster_name}")
                st.session_state['confirm_stop'] = False
            else:
                st.error("⚠️ Click again to confirm cluster stop operation")
                st.session_state['confirm_stop'] = True
    
    # AKS CLI Commands using Streamlit native
    st.subheader("⚡ Azure CLI Operations")
    st.write("Execute Azure CLI commands directly against your AKS infrastructure.")
    
    # Predefined commands with descriptions
    aks_commands = {
        "az aks list -o table": "📋 List all AKS clusters",
        f"az aks show -g {aks_resource_group} -n {aks_cluster_name}": "🔍 Show cluster details",
        f"az aks get-credentials -g {aks_resource_group} -n {aks_cluster_name}": "🔑 Get cluster credentials",
        "az aks get-versions --location eastus -o table": "📦 Available Kubernetes versions",
        f"az aks nodepool list -g {aks_resource_group} --cluster-name {aks_cluster_name}": "🖥️ List node pools"
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_command = st.selectbox(
            "Select CLI operation:", 
            ["Custom..."] + list(aks_commands.keys()),
            format_func=lambda x: aks_commands.get(x, "✏️ Custom Command") if x != "Custom..." else "✏️ Custom Command"
        )
        
        if selected_command == "Custom...":
            aks_cli_command = st.text_input("Enter Azure CLI command:", "az aks list", help="Enter any Azure CLI command")
        else:
            aks_cli_command = st.text_input("Command to execute:", value=selected_command, help="Review and modify if needed")
    
    with col2:
        st.markdown("#### ℹ️ Command Info")
        if selected_command != "Custom..." and selected_command in aks_commands:
            st.info(aks_commands[selected_command])
        else:
            st.info("Custom Azure CLI command")
    
    if st.button("⚡ Execute CLI Command", use_container_width=True, type="secondary"):
        with st.spinner(f"🔄 Executing: {aks_cli_command[:50]}..."):
            start_time = time.time()
            response = api_client.aks_cli_command(aks_cli_command)
            execution_time = time.time() - start_time
            st.success(f"CLI command executed in {execution_time:.2f}s")
            display_response(response, f"⚡ AKS CLI Result: {aks_cli_command[:30]}...")

def postgres_operations_ui(api_client: APIClient):
    """Enhanced PostgreSQL Operations UI using Streamlit native components"""
    st.markdown('<div class="section-header">🐘 PostgreSQL Operations</div>', unsafe_allow_html=True)
    
    # Quick status overview
    st.markdown("""
    <div class="dashboard-card">
        <h4>📊 PostgreSQL Service Overview</h4>
        <p>Manage and monitor your Azure PostgreSQL Flexible Server with advanced database operations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # PostgreSQL Configuration using Streamlit native
    st.subheader("🔧 Database Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        pg_resource_group = st.text_input(
            "📁 Resource Group", 
            value="adv_data_rg", 
            key="pg_rg",
            help="Azure Resource Group containing the PostgreSQL server"
        )
        pg_server_name = st.text_input(
            "🗄️ Server Name", 
            value="advpsqlfxuk", 
            key="pg_server",
            help="PostgreSQL Flexible Server name"
        )
    with col2:
        pg_database_name = st.text_input(
            "🎯 Database Name", 
            value="adventureworks", 
            key="pg_db",
            help="Target database for operations"
        )
        pg_username = st.text_input(
            "👤 Username", 
            value="alfonsod", 
            key="pg_user",
            help="Database username for connections"
        )
    
    # Server Management Section - Lista de servidores con controles
    st.subheader("🗄️ Server Management")
    st.write("List and control PostgreSQL servers in your subscription.")
    
    # Initialize servers in session state
    if 'postgres_servers' not in st.session_state:
        st.session_state.postgres_servers = []
    if 'servers_loaded' not in st.session_state:
        st.session_state.servers_loaded = False
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 List All Servers", use_container_width=True, type="primary"):
            with st.spinner("🔍 Loading PostgreSQL servers..."):
                start_time = time.time()
                response = api_client.postgres_list_servers()
                execution_time = time.time() - start_time
                
                if response["success"] and response["data"].get("result", {}).get("status") == "success":
                    st.success(f"Servers loaded in {execution_time:.2f}s")
                    st.session_state.postgres_servers = response["data"]["result"]["details"]["servers"]
                    st.session_state.servers_loaded = True
                else:
                    st.error("Failed to load servers")
                    st.session_state.servers_loaded = False
                    display_response(response, "List Servers Error")
    
    # Display servers if loaded
    if st.session_state.servers_loaded and st.session_state.postgres_servers:
        st.subheader(f"📊 Found {len(st.session_state.postgres_servers)} PostgreSQL servers:")
        
        # Display servers with controls
        for i, server in enumerate(st.session_state.postgres_servers):
            with st.container():
                st.markdown(f"""
                <div class="resource-card">
                    <h4>🗄️ {server['name']}</h4>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p><strong>Resource Group:</strong> {server['resource_group']}</p>
                            <p><strong>Location:</strong> {server['location']}</p>
                            <p><strong>State:</strong> <span class="status-indicator {'status-healthy' if server['state'] == 'Ready' else 'status-warning'}">{server['state']}</span></p>
                            <p><strong>Version:</strong> {server['version']}</p>
                            <p><strong>SKU:</strong> {server['sku']['name'] if server['sku'] else 'N/A'} ({server['sku']['tier'] if server['sku'] else 'N/A'})</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons for each server
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    # Start button with improved UX
                    start_disabled = server['state'] in ['Ready', 'Starting']
                    start_button_text = "▶️ Starting..." if server['state'] == 'Starting' else "▶️ Start"
                    
                    if st.button(start_button_text, key=f"start_{i}_{server['name']}", 
                               use_container_width=True, 
                               disabled=start_disabled):
                        
                        # Store operation result in session state
                        operation_key = f"start_result_{server['name']}"
                        
                        with st.spinner(f"🚀 Starting server {server['name']}..."):
                            start_response = api_client.postgres_start_server(
                                server['resource_group'], server['name']
                            )
                            st.session_state[operation_key] = start_response
                        
                        # Rerun to show the result
                        st.rerun()
                
                with col_b:
                    # Stop button with improved UX
                    stop_disabled = server['state'] in ['Stopped', 'Stopping']
                    stop_button_text = "⏹️ Stopping..." if server['state'] == 'Stopping' else "⏹️ Stop"
                    
                    if st.button(stop_button_text, key=f"stop_{i}_{server['name']}", 
                               use_container_width=True,
                               disabled=stop_disabled):
                        
                        # Store operation result in session state
                        operation_key = f"stop_result_{server['name']}"
                        
                        with st.spinner(f"⏹️ Stopping server {server['name']}..."):
                            stop_response = api_client.postgres_stop_server(
                                server['resource_group'], server['name']
                            )
                            st.session_state[operation_key] = stop_response
                        
                        # Rerun to show the result
                        st.rerun()
                
                with col_c:
                    if st.button(f"📊 Status", key=f"status_{i}_{server['name']}", 
                               use_container_width=True):
                        with st.spinner(f"🔍 Getting status for {server['name']}..."):
                            status_response = api_client.postgres_get_status(
                                server['resource_group'], server['name']
                            )
                        display_response(status_response, f"Status: {server['name']}")
                
                # Show operation results if available
                start_result_key = f"start_result_{server['name']}"
                stop_result_key = f"stop_result_{server['name']}"
                
                if start_result_key in st.session_state:
                    result = st.session_state[start_result_key]
                    if result["success"]:
                        st.success(f"✅ Start command sent for {server['name']}")
                        st.info("💡 Server is starting. Refresh the list to see updated status.")
                    else:
                        st.error(f"❌ Failed to start {server['name']}")
                        # Show detailed error information
                        if result.get("data", {}).get("result", {}).get("details"):
                            details = result["data"]["result"]["details"]
                            if "rest_api" in details and "cli_fallback" in details:
                                st.error("🔧 Both REST API and CLI methods failed:")
                                with st.expander("Error Details"):
                                    st.write("**REST API Error:**", details["rest_api"].get("error", "Unknown"))
                                    st.write("**CLI Error:**", details["cli_fallback"].get("error", "Unknown"))
                            elif "error" in details:
                                st.error(f"🔧 Error: {details['error']}")
                    
                    # Show full response in expandable section
                    with st.expander(f"🔍 Full Response - Start {server['name']}"):
                        st.json(result)
                    
                    # Clear the result after showing
                    if st.button(f"Clear Start Result", key=f"clear_start_{i}"):
                        del st.session_state[start_result_key]
                        st.rerun()
                
                if stop_result_key in st.session_state:
                    result = st.session_state[stop_result_key]
                    if result["success"]:
                        st.success(f"✅ Stop command sent for {server['name']}")
                        st.info("💡 Server is stopping. Refresh the list to see updated status.")
                    else:
                        st.error(f"❌ Failed to stop {server['name']}")
                        # Show detailed error information
                        if result.get("data", {}).get("result", {}).get("details"):
                            details = result["data"]["result"]["details"]
                            if "rest_api" in details and "cli_fallback" in details:
                                st.error("🔧 Both REST API and CLI methods failed:")
                                with st.expander("Error Details"):
                                    st.write("**REST API Error:**", details["rest_api"].get("error", "Unknown"))
                                    st.write("**CLI Error:**", details["cli_fallback"].get("error", "Unknown"))
                            elif "error" in details:
                                st.error(f"🔧 Error: {details['error']}")
                    
                    # Show full response in expandable section
                    with st.expander(f"🔍 Full Response - Stop {server['name']}"):
                        st.json(result)
                    
                    # Clear the result after showing
                    if st.button(f"Clear Stop Result", key=f"clear_stop_{i}"):
                        del st.session_state[stop_result_key]
                        st.rerun()
                
                st.markdown("---")
    elif st.session_state.servers_loaded and not st.session_state.postgres_servers:
        st.info("No PostgreSQL servers found in your subscription.")
    
    with col2:
        filter_rg = st.text_input("🔍 Filter by Resource Group", 
                                 placeholder="Optional - leave empty for all",
                                 help="Filter servers by specific resource group")
        
        if st.button("📋 List by Resource Group", use_container_width=True, 
                    disabled=not filter_rg):
            if filter_rg:
                with st.spinner(f"🔍 Loading servers from {filter_rg}..."):
                    start_time = time.time()
                    response = api_client.postgres_list_servers(filter_rg)
                    execution_time = time.time() - start_time
                    st.success(f"Servers loaded in {execution_time:.2f}s")
                    display_response(response, f"Servers in {filter_rg}")
    
    with col3:
        st.markdown("#### ℹ️ Server Controls")
        st.info("""
        **Server States:**
        • Ready - Server is running
        • Stopped - Server is stopped
        • Starting - Server is starting up
        • Stopping - Server is shutting down
        
        **Actions:**
        • Start - Powers on a stopped server
        • Stop - Powers off a running server  
        • Status - Get detailed server info
        """)
    
    # Individual Server Operations using Streamlit native
    st.subheader("🎮 Individual Server Operations")
    st.write("Monitor specific server status and execute targeted operations.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Get Server Status", use_container_width=True, type="primary"):
            with st.spinner("🔍 Retrieving server status..."):
                start_time = time.time()
                response = api_client.postgres_get_status(pg_resource_group, pg_server_name)
                execution_time = time.time() - start_time
                st.success(f"Status retrieved in {execution_time:.2f}s")
                display_response(response, f"📊 PostgreSQL Server Status - {pg_server_name}")
    
    with col2:
        st.markdown("#### 📈 Server Metrics")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Server Version", "17.4", delta="Latest")
        with col_b:
            st.metric("Status", "Running", delta="Healthy")
    
    # PostgreSQL CLI Commands using Streamlit native
    st.subheader("⚡ Azure CLI Operations")
    st.write("Execute Azure CLI commands for PostgreSQL management.")
    
    # Predefined commands with descriptions
    pg_commands = {
        f"az postgres flexible-server list -g {pg_resource_group}": "📋 List all PostgreSQL servers",
        f"az postgres flexible-server show -g {pg_resource_group} -n {pg_server_name}": "🔍 Show server details",
        f"az postgres flexible-server backup list -g {pg_resource_group} -n {pg_server_name}": "💾 List backups",
        "az postgres flexible-server list-versions --location eastus": "📦 Available versions",
        f"az postgres flexible-server parameter list -g {pg_resource_group} -s {pg_server_name}": "⚙️ Server parameters"
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_pg_command = st.selectbox(
            "Select CLI operation:", 
            ["Custom..."] + list(pg_commands.keys()),
            format_func=lambda x: pg_commands.get(x, "✏️ Custom Command") if x != "Custom..." else "✏️ Custom Command",
            key="pg_cli_select"
        )
        
        if selected_pg_command == "Custom...":
            pg_cli_command = st.text_input("Enter Azure CLI command:", "az postgres flexible-server list", key="pg_cli_custom")
        else:
            pg_cli_command = st.text_input("Command to execute:", value=selected_pg_command, key="pg_cli_command")
    
    with col2:
        st.markdown("#### ℹ️ Command Info")
        if selected_pg_command != "Custom..." and selected_pg_command in pg_commands:
            st.info(pg_commands[selected_pg_command])
        else:
            st.info("Custom Azure CLI command")
    
    if st.button("⚡ Execute CLI Command", use_container_width=True, type="secondary"):
        with st.spinner(f"🔄 Executing: {pg_cli_command[:50]}..."):
            start_time = time.time()
            response = api_client.postgres_cli_command(pg_cli_command)
            execution_time = time.time() - start_time
            st.success(f"CLI command executed in {execution_time:.2f}s")
            display_response(response, f"⚡ PostgreSQL CLI Result: {pg_cli_command[:30]}...")
    
    # SQL Script Execution using Streamlit native
    st.subheader("📜 SQL Script Execution")
    st.write("Execute predefined or custom SQL scripts with advanced result visualization.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Password input
        pg_password = st.text_input(
            "🔐 Database Password", 
            type="password", 
            key="pg_password",
            help="Password for database authentication"
        )
        
        # Script selection
        script_options = {
            "sample_health_check.sql": "🏥 Health Check",
            "sample_backup_check.sql": "💾 Backup Check", 
            "custom_script.sql": "✏️ Custom Script"
        }
        
        selected_script = st.selectbox(
            "📜 Select SQL script:", 
            list(script_options.keys()),
            format_func=lambda x: script_options[x]
        )
        
        # Parameters section
        with st.expander("⚙️ Script Parameters", expanded=False):
            st.info("💡 Add parameters for script substitution using ${parameter_name} syntax")
            param_key = st.text_input("Parameter name:", placeholder="table_name")
            param_value = st.text_input("Parameter value:", placeholder="users")
            parameters = {}
            if param_key and param_value:
                parameters[param_key] = param_value
                st.success(f"✅ Parameter added: {param_key} = {param_value}")
    
    with col2:
        # Script descriptions
        script_info = {
            "sample_health_check.sql": {
                "title": "🏥 Database Health Check",
                "description": "Comprehensive database monitoring",
                "features": [
                    "📊 Database version and timestamp",
                    "💽 Database size information",  
                    "🔗 Active connection statistics",
                    "📋 Table count by schema",
                    "⚡ Performance metrics"
                ]
            },
            "sample_backup_check.sql": {
                "title": "💾 Backup Verification",
                "description": "Backup monitoring and validation",
                "features": [
                    "🔍 Backup verification queries",
                    "📅 Backup schedule information",
                    "✅ Backup integrity checks",
                    "⏰ Last backup timestamp"
                ]
            },
            "custom_script.sql": {
                "title": "✏️ Custom SQL Script",
                "description": "Execute your own SQL operations",
                "features": [
                    "📝 Upload custom SQL script",
                    "🔧 Place in app/scripts/sql/",
                    "⚙️ Parameter substitution support",
                    "📊 Multi-query execution"
                ]
            }
        }
        
        if selected_script in script_info:
            info = script_info[selected_script]
            st.markdown(f"#### {info['title']}")
            st.markdown(f"*{info['description']}*")
            st.markdown("**Features:**")
            for feature in info['features']:
                st.markdown(f"- {feature}")
    
    # Execute button
    if st.button("🚀 Execute SQL Script", use_container_width=True, type="primary"):
        if not pg_password:
            st.error("🔐 Please enter the database password to proceed")
        else:
            with st.spinner(f"🔄 Executing script: {script_options[selected_script]}..."):
                start_time = time.time()
                response = api_client.postgres_execute_script(
                    pg_resource_group, pg_server_name, pg_database_name,
                    pg_username, pg_password, selected_script, parameters
                )
                execution_time = time.time() - start_time
                st.success(f"Script executed in {execution_time:.2f}s")
                display_response(response, f"📜 SQL Script Results: {script_options[selected_script]}")

if __name__ == "__main__":
    main()