"""
Authentication module for Azure Day 2 Engine Frontend
==================================================

Simple authentication system for securing the frontend dashboard.
Uses session state to maintain authentication across page interactions.
"""

import streamlit as st
import hashlib
import os
import time
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# Configuration
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "azure-day2-admin")  # Default password - matches backend
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

def get_api_base_url() -> str:
    """Get the API base URL"""
    return API_BASE_URL

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username: str, password: str) -> bool:
    """Verify user credentials"""
    expected_username = AUTH_USERNAME
    expected_password_hash = hash_password(AUTH_PASSWORD)
    provided_password_hash = hash_password(password)
    
    return (username == expected_username and 
            provided_password_hash == expected_password_hash)

def login_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user with the real API backend
    
    Returns:
        Dict with login response or error information
    """
    try:
        api_url = get_api_base_url()
        response = requests.post(
            f"{api_url}/auth/login", 
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            return {
                "success": True, 
                "data": {
                    "access_token": token_data.get("access_token"),
                    "user_info": {"username": username, "role": "admin"},
                    "expires_in": 7200  # 2 hours (backend default: 24h, but using shorter for frontend)
                }
            }
        elif response.status_code == 401:
            return {"success": False, "error": "Invalid username or password"}
        else:
            return {"success": False, "error": f"Authentication failed: HTTP {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to authentication server. Please check if the backend API is running."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Authentication request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def logout_user():
    """Logout user and clear session"""
    # Clear all auth-related session state
    keys_to_clear = ["authenticated", "access_token", "user_info", "token_expires"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.success("Logged out successfully")
    st.rerun()

def is_token_expired() -> bool:
    """Check if the current token is expired"""
    if "token_expires" not in st.session_state:
        return True
    
    try:
        expires_at = datetime.fromisoformat(st.session_state.token_expires)
        return datetime.now() >= expires_at
    except:
        return True

def is_authenticated() -> bool:
    """Check if user is authenticated and token is valid"""
    if not st.session_state.get("authenticated", False):
        return False
    
    if not st.session_state.get("access_token"):
        return False
    
    if is_token_expired():
        # Token expired, clear session
        logout_user()
        return False
    
    return True

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers for API requests"""
    if not is_authenticated():
        return {}
    
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def make_authenticated_request(method: str, url: str, **kwargs) -> requests.Response:
    """Make an authenticated request to the API"""
    if not is_authenticated():
        raise Exception("Not authenticated")
    
    headers = kwargs.get("headers", {})
    headers.update(get_auth_headers())
    kwargs["headers"] = headers
    
    return requests.request(method, url, **kwargs)

def show_login_form():
    """Display the login form"""
    st.markdown("""
        <div style="
            background: linear-gradient(90deg, #0066cc 0%, #004080 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h1>🔐 Azure Day 2 Engine</h1>
            <p>Secure Internal Developer Platform</p>
            <p><em>Please authenticate to access the dashboard</em></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔑 Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
            
            if submit_button:
                if username and password:
                    with st.spinner("Authenticating..."):
                        result = login_user(username, password)
                    
                    if result["success"]:
                        # Store authentication data
                        token_data = result["data"]
                        st.session_state.authenticated = True
                        st.session_state.access_token = token_data["access_token"]
                        st.session_state.user_info = token_data["user_info"]
                        
                        # Calculate token expiration
                        expires_in_seconds = token_data["expires_in"]
                        expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)
                        st.session_state.token_expires = expires_at.isoformat()
                        
                        st.success(f"Welcome, {token_data['user_info']['username']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {result['error']}")
                else:
                    st.error("Please enter both username and password")
        
        # API connection status
        st.markdown("---")
        st.markdown("### 🌐 Connection Status")
        api_url = get_api_base_url()
        
        try:
            import requests
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success(f"✅ Connected to API: {api_url}")
            else:
                st.error(f"❌ API error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection failed: {str(e)}")
            st.warning("Make sure the backend API is running and accessible")
        except ImportError:
            st.warning("⚠️ Requests library not available for connection test")

def show_user_info():
    """Display current user information in sidebar"""
    if not is_authenticated():
        return
    
    user_info = st.session_state.get("user_info", {})
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 User Information")
    st.sidebar.write(f"**Username:** {user_info.get('username', 'Unknown')}")
    st.sidebar.write(f"**Role:** {user_info.get('role', 'Unknown')}")
    
    # Token expiration info
    if "token_expires" in st.session_state:
        try:
            expires_at = datetime.fromisoformat(st.session_state.token_expires)
            time_left = expires_at - datetime.now()
            if time_left.total_seconds() > 0:
                hours_left = int(time_left.total_seconds() // 3600)
                minutes_left = int((time_left.total_seconds() % 3600) // 60)
                st.sidebar.write(f"**Session expires in:** {hours_left}h {minutes_left}m")
            else:
                st.sidebar.error("Session expired")
        except:
            pass
    
    # Logout button
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout_user()

def require_authentication():
    """Decorator function to require authentication for pages"""
    if not is_authenticated():
        show_login_form()
        st.stop()
    else:
        show_user_info()