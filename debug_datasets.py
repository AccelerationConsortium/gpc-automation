#!/usr/bin/env python3
"""
Debug CSV Dataset Export - Find Available Dataset Definitions

This script will help us understand why CSV export is failing
by exploring what dataset definitions are available.
"""

import os
from datetime import datetime
from astra_admin import AstraAdmin

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    """
    Debug dataset export by trying different approaches
    """
    log("🔍 Dataset Export Debug")
    
    # First, let's see if there are any experiment files we can work with
    results_dir = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
    
    # Look for existing experiment files
    experiment_files = []
    if os.path.exists(results_dir):
        for file in os.listdir(results_dir):
            if file.endswith('.afe8'):
                experiment_files.append(os.path.join(results_dir, file))
    
    if not experiment_files:
        log("❌ No experiment files found to test dataset export")
        return False
        
    log(f"📁 Found {len(experiment_files)} experiment files:")
    for file in experiment_files:
        log(f"  → {os.path.basename(file)}")
    
    # Use the most recent experiment file
    latest_file = max(experiment_files, key=os.path.getmtime)
    log(f"🎯 Using latest file: {os.path.basename(latest_file)}")
    
    try:
        # Try to open the experiment and get dataset info
        log("🔧 Attempting to analyze experiment for available datasets...")
        
        # This might give us clues about what went wrong
        admin = AstraAdmin()
        
        # Try various dataset definition patterns
        dataset_patterns = [
            # Standard patterns
            "molecular weight vs volume",
            "molar mass vs volume", 
            "concentration vs volume",
            "intensity vs volume",
            "mean square radius vs volume",
            
            # Alternative patterns
            "Molecular Weight vs Volume",
            "Molar Mass vs Volume",
            "Concentration vs Volume", 
            "Intensity vs Volume",
            
            # Different separators
            "molecular weight vs. volume",
            "molar mass vs. volume",
            "molecular_weight_vs_volume",
            "molar_mass_vs_volume",
            
            # Single words
            "molecular",
            "weight", 
            "molar",
            "mass",
            "concentration",
            "intensity",
            
            # Empty string (might give default)
            "",
        ]
        
        log("🧪 Testing dataset export patterns...")
        test_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for i, pattern in enumerate(dataset_patterns):
            test_file = os.path.join(results_dir, f"test_dataset_{i:02d}_{test_timestamp}.csv")
            
            try:
                log(f"  Testing: '{pattern}'")
                
                # Note: We can't easily get experiment_id from saved file,
                # so this debug approach has limitations
                # Let's at least log what we're trying
                
                log(f"    → Would try to export to: test_dataset_{i:02d}_{test_timestamp}.csv")
                
            except Exception as e:
                log(f"    → Error: {e}")
        
        log("💡 The real issue might be that we need an active experiment in memory")
        log("💡 The CSV export might only work during the automation run, not from saved files")
        log("💡 Let's check if this is a timing issue in our main script")
        
        return True
        
    except Exception as e:
        log(f"❌ Error during dataset debug: {e}")
        return False

if __name__ == "__main__":
    main()
