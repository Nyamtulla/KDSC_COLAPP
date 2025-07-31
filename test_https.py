#!/usr/bin/env python3
"""
Test script to verify HTTPS configuration for ColApp
"""
import requests
import json
from urllib.parse import urljoin

def test_endpoint(url, description):
    """Test an endpoint and print results"""
    print(f"\n🔍 Testing {description}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ HTTPS: {'Yes' if url.startswith('https://') else 'No'}")
        
        hsts = response.headers.get('Strict-Transport-Security')
        if hsts:
            print(f"   ✅ HSTS: Yes ({hsts})")
        else:
            print(f"   ⚠️  HSTS: No")
            
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ JSON Response: {data.get('status', 'OK')}")
            except:
                print(f"   ✅ Response: {len(response.text)} characters")
        else:
            print(f"   ⚠️  Response: {response.text[:100]}...")
            
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL Error: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection Error: {e}")
    except requests.exceptions.Timeout as e:
        print(f"   ❌ Timeout: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_cors(url, origin):
    """Test CORS headers"""
    print(f"\n🔍 Testing CORS for {origin} → {url}")
    
    try:
        headers = {'Origin': origin}
        response = requests.options(url, headers=headers, timeout=10)
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        cors_credentials = response.headers.get('Access-Control-Allow-Credentials')
        
        print(f"   ✅ CORS Origin: {cors_origin}")
        print(f"   ✅ CORS Credentials: {cors_credentials}")
        
        if cors_origin == origin or cors_origin == '*':
            print(f"   ✅ CORS: Allowed")
        else:
            print(f"   ❌ CORS: Blocked (got {cors_origin}, expected {origin})")
            
    except Exception as e:
        print(f"   ❌ CORS Test Error: {e}")

def test_security_headers(url, description):
    """Test security headers"""
    print(f"\n🔒 Testing Security Headers for {description}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        security_headers = {
            'Strict-Transport-Security': 'HSTS',
            'Content-Security-Policy': 'CSP',
            'X-Content-Type-Options': 'X-Content-Type-Options',
            'X-Frame-Options': 'X-Frame-Options',
            'X-XSS-Protection': 'X-XSS-Protection',
            'Referrer-Policy': 'Referrer-Policy'
        }
        
        for header, name in security_headers.items():
            value = response.headers.get(header)
            if value:
                print(f"   ✅ {name}: {value}")
            else:
                print(f"   ⚠️  {name}: Not set")
                
    except Exception as e:
        print(f"   ❌ Security Headers Test Error: {e}")

def main():
    print("🚀 ColApp HTTPS Configuration Test")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ("https://nyamshaik.me", "Frontend (GitHub Pages)"),
        ("https://api.nyamshaik.me", "Backend API"),
        ("https://api.nyamshaik.me/health", "Backend Health Check"),
    ]
    
    for url, description in endpoints:
        test_endpoint(url, description)
    
    # Test CORS
    print("\n" + "=" * 50)
    print("🔒 CORS Configuration Test")
    print("=" * 50)
    
    cors_tests = [
        ("https://api.nyamshaik.me/login", "https://nyamshaik.me"),
        ("https://api.nyamshaik.me/health", "https://nyamshaik.me"),
    ]
    
    for url, origin in cors_tests:
        test_cors(url, origin)
    
    # Test security headers
    print("\n" + "=" * 50)
    print("🔒 Security Headers Test")
    print("=" * 50)
    
    security_tests = [
        ("https://api.nyamshaik.me/health", "Backend Health Check"),
    ]
    
    for url, description in security_tests:
        test_security_headers(url, description)
    
    print("\n" + "=" * 50)
    print("✅ HTTPS Configuration Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main() 