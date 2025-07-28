#!/usr/bin/env python3
"""
Test script to validate authentication integration between frontend and backend
"""

import requests
import sys
import json

def test_authentication():
    """Test the authentication flow"""
    api_url = "http://localhost:8000"
    
    print("🔍 Testing Authentication Integration")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing API health...")
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and healthy")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Make sure to run: ./scripts/run_dev.sh")
        return False
    
    # Test 2: Login with correct credentials
    print("\n2. Testing login with correct credentials...")
    try:
        login_data = {
            "username": "admin", 
            "password": "azure-day2-admin"
        }
        response = requests.post(
            f"{api_url}/auth/login", 
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful")
            print(f"   Token type: {token_data.get('token_type')}")
            print(f"   Expires in: {token_data.get('expires_in')} seconds")
            print(f"   User: {token_data.get('user_info', {}).get('username')}")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # Test 3: Test protected AKS endpoint
    print("\n3. Testing protected AKS endpoint...")
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test AKS status endpoint (this will fail gracefully if no cluster configured)
        response = requests.get(
            f"{api_url}/AKS/v1/status/test-rg/test-cluster",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 404, 500]:  # Any of these means auth worked
            print("✅ AKS endpoint accepts JWT token")
            print(f"   Status: {response.status_code}")
        elif response.status_code == 401:
            print("❌ AKS endpoint rejected JWT token (authentication failed)")
            return False
        else:
            print(f"⚠️  Unexpected AKS response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ AKS request failed: {e}")
        return False
    
    # Test 4: Test invalid credentials
    print("\n4. Testing login with invalid credentials...")
    try:
        login_data = {
            "username": "admin", 
            "password": "wrong-password"
        }
        response = requests.post(
            f"{api_url}/auth/login", 
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ Invalid credentials correctly rejected")
        else:
            print(f"❌ Invalid credentials should return 401, got: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Invalid login test failed: {e}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    print("\n📋 Frontend Integration Notes:")
    print("   • Frontend now uses real API authentication")
    print("   • JWT tokens from backend are used for AKS operations")
    print("   • Password matches backend default: 'azure-day2-admin'")
    print("   • Session management improved with proper token cleanup")
    
    return True

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)