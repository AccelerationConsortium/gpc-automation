#!/usr/bin/env python3
"""
Add Missing GetDataSetNames Method - Direct COM Call

This script adds the missing GetDataSetNames functionality 
by calling the COM method directly.
"""

import os
import uuid
from datetime import datetime
from astra_admin import AstraAdmin

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def get_data_set_names_direct(admin, experiment_id):
    """
    Call GetDataSetNames directly on the COM object
    This method is missing from the Python wrapper
    """
    try:
        # Access the underlying COM object directly
        com_object = admin.astra_com
        dataset_names = com_object.GetDataSetNames(experiment_id)
        return dataset_names
    except Exception as e:
        log(f"Error calling GetDataSetNames: {e}")
        return None

def main():
    """
    Use the missing GetDataSetNames method to discover all available datasets
    """
    log("🔍 Using Missing GetDataSetNames Method")
    
    # Setup
    results_dir = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
    target_file = os.path.join(results_dir, "collected_experiment_20260113_114325.aex.afe8")
    
    if not os.path.exists(target_file):
        log(f"❌ Experiment file not found: {target_file}")
        return False
    
    log(f"📁 Using experiment: {os.path.basename(target_file)}")
    
    # Setup ASTRA connection
    log("=== Setting up ASTRA Connection ===")
    client_id = uuid.uuid4().hex
    
    try:
        admin = AstraAdmin()
        admin.set_automation_identity("DataSet Names Finder", "1.0.0.0", os.getpid(), client_id, 1)
        admin.wait_for_instruments()
        experiment_id = admin.open_experiment(target_file)
        log(f"✓ Experiment opened - ID: {experiment_id}")
    except Exception as e:
        log(f"✗ Error setting up ASTRA: {e}")
        return False
    
    # Try to get all dataset names using the missing method
    log("=== Calling GetDataSetNames (Missing Method) ===")
    dataset_names = get_data_set_names_direct(admin, experiment_id)
    
    if dataset_names:
        log(f"🎉 SUCCESS: Found {len(dataset_names)} dataset definitions:")
        for i, name in enumerate(dataset_names):
            log(f"  {i+1}. '{name}'")
        
        log("")
        log("=== Testing Each Dataset Definition ===")
        
        # Now test each discovered dataset definition
        working_datasets = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for i, definition_name in enumerate(dataset_names):
            try:
                log(f"Testing: '{definition_name}'")
                dataset_content = admin.get_data_set(experiment_id, definition_name)
                
                if dataset_content and hasattr(dataset_content, 'strip') and len(dataset_content.strip()) > 10:
                    content_length = len(dataset_content)
                    lines = len(dataset_content.split('\n'))
                    
                    log(f"  ✓ VALID: {content_length} chars, {lines} lines")
                    working_datasets.append((definition_name, dataset_content))
                    
                    # Export this dataset
                    safe_name = "".join(c for c in definition_name if c.isalnum() or c in " -_").replace(" ", "_")
                    filename = f"discovered_dataset_{i:02d}_{safe_name}_{timestamp}.csv"
                    filepath = os.path.join(results_dir, filename)
                    
                    try:
                        success = admin.save_data_set(experiment_id, definition_name, filepath)
                        if success and os.path.exists(filepath):
                            size = os.path.getsize(filepath)
                            log(f"    → Exported: {filename} ({size:,} bytes)")
                        else:
                            log(f"    → Export failed")
                    except Exception as exp_error:
                        log(f"    → Export error: {exp_error}")
                        
                else:
                    log(f"  → Empty or invalid data")
                    
            except Exception as e:
                if "'_empty' object" not in str(e):
                    log(f"  → Error: {e}")
                else:
                    log(f"  → Empty dataset")
        
        log("=== Final Results ===")
        log(f"🎯 Discovered {len(dataset_names)} total dataset definitions")
        log(f"✅ Found {len(working_datasets)} with valid data")
        
        if working_datasets:
            log("\nWorking dataset definitions:")
            for name, _ in working_datasets:
                log(f"  ✓ '{name}'")
                
    else:
        log("❌ GetDataSetNames failed - method may not be available in this ASTRA version")
        log("💡 This explains why we had to guess dataset definition names")
    
    # Cleanup
    try:
        admin.close_experiment(experiment_id)
        admin.dispose()
        log("✓ Cleanup complete")
    except Exception as e:
        log(f"⚠ Cleanup warning: {e}")
    
    return dataset_names is not None and len(dataset_names) > 0

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 DATASET DISCOVERY COMPLETE!")
        print("📋 Now we know ALL available dataset definitions")
        print("💾 Check results folder for exported CSV files")
        print("🔬 These are the exact names ASTRA recognizes")
    else:
        print("\n❌ Dataset discovery failed")
        print("💡 The GetDataSetNames method may not be available")
        
    print("\nKey findings:")
    print("• Python wrapper is missing GetDataSetNames method")
    print("• C# version has this method but Python doesn't")
    print("• This explains why we had to guess dataset definition names") 
    print("• Now we can discover the exact names ASTRA uses")
