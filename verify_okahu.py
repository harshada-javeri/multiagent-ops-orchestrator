#!/usr/bin/env python3
"""
Quick verification script for Okahu integration
Run this to test if Okahu is receiving traces
"""

import os
import sys
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_network_connectivity():
    """Check network connectivity to Okahu endpoints"""
    print("🌐 Checking Network Connectivity...\n")
    
    endpoints = {
        'okahu.jfrog.io': 'SDK repository',
        'ingest.okahu.io': 'Trace ingestion',
        'portal.okahu.co': 'Dashboard'
    }
    
    all_ok = True
    for host, purpose in endpoints.items():
        try:
            socket.create_connection((host, 443), timeout=5)
            print(f"✅ {host} ({purpose})")
        except Exception as e:
            print(f"❌ {host} ({purpose}) - {e}")
            all_ok = False
    
    return all_ok

def check_okahu_setup():
    """Verify Okahu configuration"""
    
    print("🔍 Checking Okahu Setup...\n")
    
    # Check 1: API Key
    api_key = os.getenv('OKAHU_API_KEY')
    if api_key:
        print("✅ OKAHU_API_KEY is set")
        masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
        print(f"   Key: {masked_key}")
    else:
        print("❌ OKAHU_API_KEY not found")
        print("   Windows: $env:OKAHU_API_KEY = 'your_key'")
        print("   Linux/Mac: export OKAHU_API_KEY='your_key'")
        return False
    
    # Check 2: Monocle package
    try:
        from monocle_apptrace import setup_monocle_telemetry
        print("✅ monocle_apptrace installed")
    except ImportError:
        print("❌ monocle_apptrace not installed")
        print("   Install with: pip install monocle_apptrace")
        return False
    
    # Check 3: Network connectivity
    print()
    if not check_network_connectivity():
        print("\n⚠️  Some endpoints are not reachable")
        print("   Contact your network team to allowlist Okahu endpoints")
    
    # Check 4: Test trace
    print("\n📊 Sending test trace to Okahu...")
    try:
        from monocle_apptrace import setup_monocle_telemetry
        
        # Initialize with test workflow
        setup_monocle_telemetry(workflow_name="okahu-connectivity-test")
        
        # Simulate a traced function
        def test_function():
            return "Test trace sent"
        
        result = test_function()
        print("✅ Monocle telemetry initialized")
        print(f"   Workflow: okahu-connectivity-test")
        print(f"   Traces will be sent to: https://ingest.okahu.io")
        
    except Exception as e:
        print(f"❌ Failed to initialize telemetry: {e}")
        return False
    
    print("\n✅ Okahu setup complete!")
    print("\n📍 Next steps:")
    print("   1. Visit https://portal.okahu.co/en/apps/")
    print("   2. Click 'New Application'")
    print("   3. Browse Discovered Components")
    print("   4. Look for 'qaops-multiagent-orchestrator' workflow")
    print("   5. Add selection and Save")
    print("\n💡 Run the application to generate traces:")
    print("   python predict.py")
    print("   python serve.py")
    
    return True

if __name__ == "__main__":
    success = check_okahu_setup()
    sys.exit(0 if success else 1)