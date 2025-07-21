# Azure Day 2 Engine - Frontend Dashboard

Interactive web interface for demonstrating and testing the Azure Day 2 Engine API capabilities.

![Dashboard Preview](https://img.shields.io/badge/Framework-Streamlit-FF6B6B)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB)
![Status](https://img.shields.io/badge/Status-Ready-success)

## Features

### 🚀 **AKS Operations**
- **Cluster Management**: Start, stop, and get status of AKS clusters
- **Azure CLI Integration**: Execute predefined or custom Azure CLI commands
- **Real-time Results**: Visual display of operation results and execution times

### 🐘 **PostgreSQL Operations**
- **Server Management**: Get PostgreSQL Flexible Server status and information
- **SQL Script Execution**: Run health checks and custom SQL scripts with multi-query support
- **Data Visualization**: Structured display of query results in tables
- **Azure CLI Integration**: PostgreSQL-specific CLI commands with auto-authentication

### 🎨 **Visual Features**
- **Clean Interface**: Modern, responsive design with Azure-themed styling
- **Structured Responses**: Organized display of API responses with success/error indicators
- **Real-time Feedback**: Loading spinners and progress indicators
- **Raw Data Access**: Expandable raw response viewers for debugging

## Quick Start

### Prerequisites
- Azure Day 2 Engine backend running on `http://localhost:8000`
- Python 3.11+
- Virtual environment (recommended)

### Installation & Launch

**Option 1: Quick Start Script**
```bash
cd frontend
./run_frontend.sh
```

**Option 2: Manual Setup**
```bash
cd frontend

# Install dependencies
pip install -r requirements.txt

# Launch dashboard
streamlit run app.py --server.port 8501
```

The dashboard will be available at: **http://localhost:8501**

## Usage Guide

### 1. **API Health Check**
- Use the sidebar "Check API Health" button to verify backend connectivity
- Green indicator shows the API is ready for operations

### 2. **AKS Operations Tab**
- Configure your resource group and cluster name
- Use the three main buttons for cluster management:
  - **Get Cluster Status**: Retrieve current cluster information
  - **Start Cluster**: Initiate cluster startup (shows current status due to SDK limitations)
  - **Stop Cluster**: Initiate cluster shutdown (shows current status due to SDK limitations)
- Execute Azure CLI commands using predefined options or custom commands

### 3. **PostgreSQL Operations Tab**
- Configure connection details (resource group, server name, database, credentials)
- **Get Server Status**: Retrieve comprehensive server information
- **Execute SQL Scripts**: Run health checks or custom scripts
  - Select from available scripts: `sample_health_check.sql`, `sample_backup_check.sql`
  - View structured results with query metadata and execution statistics
- **Azure CLI Commands**: Execute PostgreSQL-specific Azure CLI operations

### 4. **Response Visualization**
- **Success Responses**: Green indicators with structured data display
- **Error Responses**: Red indicators with detailed error information
- **Query Results**: Tabular display of SQL query results with pandas DataFrames
- **Raw Response**: Expandable JSON viewer for complete API response inspection

## Available SQL Scripts

### `sample_health_check.sql`
Comprehensive database health monitoring including:
- PostgreSQL version and current timestamp
- Database size information
- Active connections statistics  
- Table count by schema

### `sample_backup_check.sql`
Backup verification and monitoring queries for database maintenance.

## Configuration

### Default Settings
- **Backend API**: `http://localhost:8000`
- **Frontend Port**: `8501`
- **Default Resource Group**: `adv_data_rg`
- **Default PostgreSQL Server**: `advpsqlfxuk`
- **Default Database**: `adventureworks`

### Customization
Edit the following in `app.py`:
```python
API_BASE_URL = "http://localhost:8000"  # Change if backend runs elsewhere
```

## Architecture

```
Frontend (Streamlit) → API Client → Azure Day 2 Engine API
     ↓                      ↓              ↓
Web Interface          HTTP Requests   Azure Resources
```

### Key Components
- **`APIClient`**: Handles all HTTP requests to the backend API
- **`display_response()`**: Formats and visualizes API responses
- **Tab-based UI**: Separate interfaces for AKS and PostgreSQL operations
- **Configuration Sidebar**: API health monitoring and settings

## Troubleshooting

### Common Issues

**1. "API not reachable"**
- Ensure the backend is running: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Check firewall settings
- Verify the API_BASE_URL in the frontend configuration

**2. Authentication Errors**
- Ensure Azure credentials are properly configured in the backend `.env` file
- Check that the service principal has proper permissions

**3. PostgreSQL Connection Issues**
- Verify database credentials in the frontend form
- Ensure the PostgreSQL server allows connections from your IP
- Check that the server name format is correct (short name vs FQDN)

**4. Frontend Dependencies**
```bash
# If packages are missing
pip install -r frontend/requirements.txt
```

## Development

### Adding New Features
1. **New API Endpoints**: Add methods to `APIClient` class
2. **UI Components**: Extend the tab-based interface
3. **Visualization**: Enhance `display_response()` for new data types
4. **Styling**: Modify CSS in the `st.markdown()` sections

### Testing
- Use the "Raw Response" expanders to debug API responses
- Monitor browser console for JavaScript errors
- Check Streamlit logs in the terminal for backend issues

## Demo Flow

**For Client Presentations:**

1. **Start with Health Check** - Show API connectivity
2. **AKS Demonstration**:
   - Get cluster status to show current state
   - Execute CLI commands to list resources
   - Demonstrate real-time execution and results
3. **PostgreSQL Demonstration**:
   - Show server status and configuration
   - Execute health check script to display comprehensive results
   - Demonstrate CLI backup listing
4. **Highlight Key Features**:
   - Real-time execution times
   - Structured data visualization  
   - Error handling and logging
   - Multi-query SQL result display

This dashboard provides a professional, visually appealing interface for demonstrating the full capabilities of the Azure Day 2 Engine to clients and stakeholders.