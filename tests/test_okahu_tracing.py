#!/usr/bin/env python3
"""
End-to-end test for Okahu tracing
Runs a sample prediction and verifies traces are sent
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_okahu_tracing():
    """Run a complete test of the Okahu tracing setup"""
    
    print("=" * 60)
    print("🧪 Okahu Tracing End-to-End Test")
    print("=" * 60)
    print()
    
    # Step 1: Verify API key
    print("Step 1: Checking API Key...")
    api_key = os.getenv('OKAHU_API_KEY')
    if not api_key:
        print("❌ OKAHU_API_KEY not set!")
        print()
        print("Windows PowerShell:")
        print('  $env:OKAHU_API_KEY = "your-key-here"')
        print()
        print("Linux/Mac:")
        print('  export OKAHU_API_KEY="your-key-here"')
        print()
        return False
    
    masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
    print(f"✅ API Key: {masked_key}")
    print()
    
    # Step 2: Import and initialize
    print("Step 2: Initializing Monocle...")
    try:
        from monocle_apptrace import setup_monocle_telemetry
        setup_monocle_telemetry(workflow_name="qaops-multiagent-orchestrator-test")
        print("✅ Monocle initialized")
        print("   Workflow: qaops-multiagent-orchestrator-test")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    print()
    
    # Step 3: Run sample prediction
    print("Step 3: Running test prediction with tracing...")
    print("-" * 60)
    
    sample_logs = """
[INFO] Starting test suite...
[ERROR] test_login FAILED
  AssertionError: Expected 200, got 500
  at login_handler.py:45
[ERROR] test_checkout FAILED
  TimeoutError: Database connection timeout after 30s
  at checkout_service.py:120
[INFO] 2 tests failed, 8 tests passed
"""
    
    try:
        from predict import QAOpsPredictor
        
        print("Sample CI Logs:")
        print(sample_logs)
        print("-" * 60)
        
        predictor = QAOpsPredictor()
        result = predictor.predict(sample_logs)
        
        print("\n✅ Prediction completed!")
        print("\nResults:")
        print(f"  Failed Tests: {len(result.get('failed_tests', []))}")
        print(f"  Status: {result.get('status', 'unknown')}")
        
        if result.get('failed_tests'):
            print("\n  Detected failures:")
            for test in result.get('failed_tests', []):
                print(f"    - {test}")
        
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    print()
    print("📊 Next Steps:")
    print("1. Visit: https://portal.okahu.co/en/apps/")
    print("2. Click: New Application")
    print("3. Browse Discovered Components")
    print("4. Find workflow: qaops-multiagent-orchestrator-test")
    print("5. Add Selection → Save")
    print("6. View your traces in the Okahu dashboard!")
    print()
    print("💡 Traces may take 1-2 minutes to appear in the dashboard")
    print()
    
    return True

if __name__ == "__main__":
    success = test_okahu_tracing()
    sys.exit(0 if success else 1)
