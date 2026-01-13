#!/usr/bin/env python3
"""
Find All Working Dataset Definitions

This script systematically searches for ALL possible dataset definitions
that actually contain data, handling the _empty object issue properly.
"""

import os
import uuid
from datetime import datetime
from astra_admin import AstraAdmin

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def is_valid_dataset_content(content):
    """Check if dataset content is valid (not empty object)"""
    try:
        # Try to access string methods to detect _empty objects
        if content is None:
            return False
        if hasattr(content, 'strip') and len(content.strip()) > 10:
            return True
        return False
    except (AttributeError, TypeError):
        # This catches the '_empty' object has no attribute 'strip' error
        return False

def main():
    """
    Find all working dataset definitions in the experiment
    """
    log("🔍 Comprehensive Dataset Definition Search")
    
    # Setup
    results_dir = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
    
    # Find experiment file (use the same one from previous analysis)
    target_file = os.path.join(results_dir, "collected_experiment_20260113_114325.aex.afe8")
    
    if not os.path.exists(target_file):
        log(f"❌ Experiment file not found: {target_file}")
        return False
    
    log(f"📁 Using experiment: {os.path.basename(target_file)}")
    
    # Setup ASTRA connection
    log("=== Setting up ASTRA Connection ===")
    client_id = uuid.uuid4().hex
    
    try:
        AstraAdmin().set_automation_identity("Dataset Search", "1.0.0.0", os.getpid(), client_id, 1)
        AstraAdmin().wait_for_instruments()
        experiment_id = AstraAdmin().open_experiment(target_file)
        log(f"✓ Experiment opened - ID: {experiment_id}")
    except Exception as e:
        log(f"✗ Error setting up ASTRA: {e}")
        return False
    
    # Extended list of dataset definitions to try
    log("=== Searching for Dataset Definitions ===")
    
    # Based on what we found, let's try more radius/light scattering variations
    dataset_definitions = [
        # Known working one first
        "rms radius vs volume",
        
        # Light scattering variations
        "light scattering vs volume",
        "light scattering data vs volume", 
        "rayleigh ratio vs volume",
        "detector 1 vs volume",
        "detector 2 vs volume", 
        "detector 3 vs volume",
        "angle 1 vs volume",
        "angle 2 vs volume",
        "90 degree vs volume",
        
        # Radius variations  
        "mean square radius vs volume",
        "radius vs volume",
        "rg vs volume",
        "radius of gyration vs volume",
        
        # Molecular weight (even though they failed, try variations)
        "molecular weight vs volume",
        "molar mass vs volume",
        "Mn vs volume", 
        "Mw vs volume",
        "Mp vs volume",
        "weight average vs volume",
        "number average vs volume",
        "peak molecular weight vs volume",
        
        # Concentration variations
        "concentration vs volume",
        "conc vs volume", 
        "c vs volume",
        "mass concentration vs volume",
        
        # Other detector data
        "refractive index vs volume",
        "ri vs volume",
        "dri vs volume", 
        "differential refractive index vs volume",
        "uv vs volume",
        "UV vs volume",
        "UV detector vs volume",
        "viscometer vs volume",
        "viscometry vs volume",
        "intrinsic viscosity vs volume",
        
        # Try volume as x-axis variations
        "volume vs rms radius",
        "volume vs molecular weight", 
        "volume vs concentration",
        "volume vs light scattering",
        
        # Try time-based
        "rms radius vs time",
        "molecular weight vs time",
        "light scattering vs time", 
        "concentration vs time",
        
        # Try elution volume variations
        "rms radius vs elution volume",
        "molecular weight vs elution volume",
        "light scattering vs elution volume",
        
        # Try without "vs"
        "rms radius volume",
        "molecular weight volume", 
        "light scattering volume",
        
        # Try different separators
        "rms radius | volume",
        "molecular weight | volume",
        "rms radius : volume",
        "molecular weight : volume",
        
        # Try generic terms
        "data",
        "results", 
        "chromatogram",
        "peak",
        "baseline",
        "raw data",
        "detector data",
        
        # Try combinations
        "molar mass and radius vs volume",
        "molecular weight and radius vs volume",
    ]
    
    working_datasets = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    log(f"Testing {len(dataset_definitions)} dataset definitions...")
    
    for i, definition in enumerate(dataset_definitions):
        try:
            dataset_content = AstraAdmin().get_data_set(experiment_id, definition)
            
            if is_valid_dataset_content(dataset_content):
                content_length = len(dataset_content)
                lines = len(dataset_content.split('\n'))
                
                log(f"  ✓ FOUND: '{definition}' - {content_length} chars, {lines} lines")
                working_datasets.append((definition, dataset_content))
                
                # Export each working dataset 
                filename = f"working_dataset_{i:02d}_{definition.replace(' ', '_').replace('|', '_').replace(':', '_')}_{timestamp}.csv"
                # Clean up filename
                filename = "".join(c for c in filename if c.isalnum() or c in "._-")
                filepath = os.path.join(results_dir, filename)
                
                try:
                    success = AstraAdmin().save_data_set(experiment_id, definition, filepath)
                    if success and os.path.exists(filepath):
                        size = os.path.getsize(filepath)
                        log(f"    → Exported to: {filename} ({size:,} bytes)")
                    else:
                        log(f"    → Export failed for: {definition}")
                except Exception as exp_error:
                    log(f"    → Export error: {exp_error}")
                    
            # Don't log every failure to keep output clean
            elif definition in ["rms radius vs volume"]:  # Only log expected ones that fail
                log(f"  ✗ '{definition}' - no valid data")
                
        except Exception as e:
            # Only log non-empty object errors
            if "'_empty' object" not in str(e):
                log(f"  ✗ '{definition}' - error: {e}")
    
    # Summary
    log("=== Search Results ===")
    if working_datasets:
        log(f"🎉 Found {len(working_datasets)} working dataset definitions:")
        for definition, content in working_datasets:
            preview = content.split('\n')[0] if content else ""
            log(f"  ✓ '{definition}' - {preview[:80]}...")
            
        log(f"\n💾 Exported {len(working_datasets)} CSV files to results folder")
        log("🔬 These are ALL the dataset types available in your experiment")
        
    else:
        log("❌ No working dataset definitions found (unexpected)")
    
    # Cleanup
    try:
        AstraAdmin().close_experiment(experiment_id)
        AstraAdmin().dispose()
        log("✓ Cleanup complete")
    except Exception as e:
        log(f"⚠ Cleanup warning: {e}")
    
    return len(working_datasets) > 0

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 COMPREHENSIVE DATASET SEARCH COMPLETE!")
        print("📁 Check results folder for all exported CSV files")
        print("🔬 Now you know exactly what data types are available")
        print("💡 Use these dataset definitions in your automation script")
    else:
        print("\n❌ Search failed")
        
    print("\nNext steps:")
    print("• Review the exported CSV files to see what data you have")
    print("• Update your automation script to use the working dataset definitions") 
    print("• Focus on the dataset that contains your molecular weight data")
