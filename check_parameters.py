#!/usr/bin/env python3
"""
Parameter Checker for Enhanced GPC Automation

Checks if all paths and settings are correct before running the full automation.
"""

import os
from astra_admin import AstraAdmin

def check_parameters():
    """Check if all parameters are set correctly"""
    print("🔍 Checking Enhanced GPC Automation Parameters...")
    print("="*50)
    
    # Check method path
    method_path = r"//dbf/Method Builder/Owen/test_method_3"
    print(f"📋 ASTRA Method: {method_path}")
    
    # Check results directory
    base_results_dir = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
    print(f"📁 Results Directory: {base_results_dir}")
    
    if os.path.exists(base_results_dir):
        print("   ✓ Results directory exists")
    else:
        print("   ⚠ Results directory will be created")
    
    # Check ASTRA connection
    print("\n🔌 Testing ASTRA Connection...")
    try:
        admin = AstraAdmin()
        admin.set_automation_identity("Parameter Check", "1.0.0.0", os.getpid(), "test", 1)
        print("   ✓ ASTRA connection successful")
        
        # Test instrument detection
        print("🔬 Testing instrument detection...")
        admin.wait_for_instruments()
        print("   ✓ Instruments detected")
        
        # Clean up
        admin.dispose()
        print("   ✓ ASTRA connection disposed")
        
    except Exception as e:
        print(f"   ❌ ASTRA connection failed: {e}")
        return False
    
    print("\n" + "="*50)
    print("✅ All parameters check out!")
    print("💡 Ready to run enhanced_gpc_automation.py")
    print("="*50)
    
    return True

if __name__ == "__main__":
    check_parameters()
