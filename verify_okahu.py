#!/usr/bin/env python3
"""
Quick verification script for Okahu integration
Run this to test if Okahu is receiving traces
"""

import os
import sys

def check_okahu_setup():
    """Verify Okahu configuration"""
    
    print("🔍 Checking Okahu Setup...\n")
    
    # Check 1: API Key
    api_key = os.getenv('OKAHU_API_KEY')
    if api_key:
        print("✅ OKAHU_API_KEY is set")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ OKAHU_API_KEY not found")
        print("   Set it with: export OKAHU_API_KEY='your_key'")
        return False
    
    # Check 2: Monocle package
    try:
        import monocle
        print("✅ monocle-observability installed")
    except ImportError:
        print("❌ monocle-observability not installed")
        print("   Install with: pip install monocle-observability")
        return False
    
    # Check 3: Test trace
    print("\n📊 Sending test trace to Okahu...")
    try:
        from monocle import Monocle
        from monocle.exporters import OkahuExporter
        
        Monocle.init({
            'exporter': OkahuExporter(
                api_key=api_key,
                endpoint='https://api.okahu.ai/v1/traces'
            ),
            'service_name': 'qaops-test',
            'environment': 'test'
        })
        
        @Monocle.trace_agent
        def test_function():
            return "Test trace sent"
        
        result = test_function()
        print("✅ Test trace sent successfully")
        print(f"   Result: {result}")
        
    except Exception as e:
        print(f"❌ Failed to send trace: {e}")
        return False
    
    print("\n✅ Okahu setup complete!")
    print("\n📍 Next steps:")
    print("   1. Visit https://app.okahu.ai/traces")
    print("   2. Look for 'qaops-test' service")
    print("   3. Verify test trace appears")
    print("   4. Run: python integrated_orchestrator.py")
    
    return True

if __name__ == "__main__":
    success = check_okahu_setup()
    sys.exit(0 if success else 1)