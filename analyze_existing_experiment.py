#!/usr/bin/env python3
"""
Analyze Existing Experiment - Debug Dataset Export

This script opens an existing experiment file and tries to extract
dataset information without running new data collection.
"""

import os
import uuid
from datetime import datetime
from astra_admin import AstraAdmin

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    """
    Open existing experiment and debug dataset export
    """
    log("🔍 Analyzing Existing Experiment for Dataset Export")
    
    # Setup
    results_dir = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
    
    # Find existing experiment files
    experiment_files = []
    if os.path.exists(results_dir):
        for file in os.listdir(results_dir):
            if file.endswith('.afe8'):
                full_path = os.path.join(results_dir, file)
                experiment_files.append((file, full_path, os.path.getmtime(full_path)))
    
    if not experiment_files:
        log("❌ No experiment files (.afe8) found in results directory")
        return False
    
    # Sort by modification time, newest first
    experiment_files.sort(key=lambda x: x[2], reverse=True)
    
    log(f"📁 Found {len(experiment_files)} experiment files:")
    for i, (filename, _, mtime) in enumerate(experiment_files):
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        log(f"  {i+1}. {filename} (modified: {mod_time})")
    
    # Use the most recent file (the collected experiment should be largest)
    target_file = experiment_files[0][1]
    target_filename = experiment_files[0][0]
    
    log(f"🎯 Using most recent file: {target_filename}")
    log(f"📍 Full path: {target_file}")
    
    # Step 1: Set automation identity (required for API access)
    log("=== Step 1: Setting Automation Identity ===")
    client_id = uuid.uuid4().hex
    
    try:
        AstraAdmin().set_automation_identity(
            "Dataset Debug App", 
            "1.0.0.0",
            os.getpid(),
            client_id,
            1
        )
        log("✓ Automation identity set")
    except Exception as e:
        log(f"✗ Error setting identity: {e}")
        return False
    
    # Step 2: Wait for instruments (required by API)
    log("=== Step 2: Waiting for Instruments ===")
    try:
        AstraAdmin().wait_for_instruments()
        log("✓ Instruments detected")
    except Exception as e:
        log(f"✗ Error waiting for instruments: {e}")
        return False
    
    # Step 3: Open the existing experiment
    log("=== Step 3: Opening Existing Experiment ===")
    log(f"Opening: {target_file}")
    log("About to call AstraAdmin().open_experiment()...")
    
    try:
        experiment_id = AstraAdmin().open_experiment(target_file)
        log(f"✓ Experiment opened successfully - ID: {experiment_id}")
        
        # Get experiment name
        try:
            exp_name = AstraAdmin().get_experiment_name(experiment_id)
            log(f"✓ Experiment name: {exp_name}")
        except Exception as e:
            log(f"⚠ Could not get experiment name: {e}")
            exp_name = f"Experiment{experiment_id}"
            
    except Exception as e:
        log(f"✗ Error opening experiment: {e}")
        log("  → This might mean the file is corrupted or incompatible")
        return False
    
    # Step 4: Analyze available datasets
    log("=== Step 4: Analyzing Available Datasets ===")
    log("Testing various dataset definitions to see what data exists...")
    
    # Comprehensive list of possible dataset definitions
    dataset_definitions = [
        # Wyatt's official examples
        "mean square radius vs volume",
        
        # Molecular weight variations
        "molecular weight vs volume", 
        "molar mass vs volume",
        "Molecular Weight vs Volume",
        "Molar Mass vs Volume",
        "molecular weight vs. volume",
        "molar mass vs. volume",
        "molecular_weight_vs_volume",
        "molar_mass_vs_volume",
        
        # Other common data types
        "concentration vs volume",
        "Concentration vs Volume",
        "concentration vs. volume",
        "intensity vs volume",
        "Intensity vs Volume", 
        "light scattering vs volume",
        "refractive index vs volume",
        "differential refractive index vs volume",
        "viscometry vs volume",
        "UV vs volume",
        "viscometer vs volume",
        
        # Alternative formats
        "Mn vs Volume",
        "Mw vs Volume", 
        "mn vs volume",
        "mw vs volume",
        "polydispersity vs volume",
        "radius vs volume",
        "rms radius vs volume",
        
        # Try single words
        "molecular",
        "weight",
        "molar", 
        "mass",
        "concentration",
        "intensity",
        "radius",
        
        # Try empty (might give default dataset)
        "",
    ]
    
    available_datasets = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for i, dataset_definition in enumerate(dataset_definitions):
        try:
            log(f"  → Testing: '{dataset_definition}'")
            dataset_content = AstraAdmin().get_data_set(experiment_id, dataset_definition)
            
            if dataset_content and len(dataset_content.strip()) > 10:
                content_length = len(dataset_content)
                log(f"  ✓ FOUND DATA: '{dataset_definition}' - {content_length} characters")
                
                available_datasets.append((dataset_definition, dataset_content))
                
                # Show preview of the data
                preview_lines = dataset_content.split('\n')[:10]
                log("    Preview:")
                for j, line in enumerate(preview_lines):
                    if line.strip():
                        log(f"      {j+1}: {line.strip()[:120]}")
                        if j >= 4:  # Just show first few lines
                            break
                
                # Try to export this dataset to CSV
                test_filename = f"dataset_{i:02d}_{timestamp}.csv"
                test_path = os.path.join(results_dir, test_filename)
                
                try:
                    log(f"    → Attempting CSV export to: {test_filename}")
                    save_success = AstraAdmin().save_data_set(experiment_id, dataset_definition, test_path)
                    
                    if save_success and os.path.exists(test_path):
                        file_size = os.path.getsize(test_path)
                        log(f"    ✓ CSV export SUCCESS: {file_size:,} bytes saved")
                    else:
                        log(f"    ✗ CSV export failed (save_data_set returned {save_success})")
                        
                except Exception as export_error:
                    log(f"    ✗ CSV export error: {export_error}")
                
                log("")  # Spacing for readability
                
            else:
                if dataset_content:
                    log(f"  → '{dataset_definition}' - data too short ({len(dataset_content)} chars)")
                else:
                    log(f"  → '{dataset_definition}' - no data")
                    
        except Exception as e:
            log(f"  → '{dataset_definition}' - error: {e}")
    
    # Step 5: Summary of findings
    log("=== Step 5: Dataset Analysis Summary ===")
    
    if available_datasets:
        log(f"🎉 SUCCESS: Found {len(available_datasets)} working dataset definitions:")
        for definition, content in available_datasets:
            lines = len(content.split('\n'))
            chars = len(content)
            log(f"  ✓ '{definition}' - {lines} lines, {chars} characters")
            
            # Try to identify what type of data this is
            header_line = content.split('\n')[0] if content.split('\n') else ""
            if header_line:
                log(f"    Headers: {header_line[:100]}...")
        
        log("")
        log("💡 Key Findings:")
        log("  → Your experiment DOES contain exportable data")
        log("  → The CSV export should work with the correct dataset definitions")
        log("  → Check the exported CSV files in the results folder")
        log(f"  → Files named: dataset_XX_{timestamp}.csv")
        
    else:
        log("❌ No working dataset definitions found")
        log("💡 This could mean:")
        log("  → The experiment file doesn't contain processed data")
        log("  → Different dataset definition syntax is needed")
        log("  → The experiment needs to be processed/analyzed first")
    
    # Step 6: Close experiment cleanly
    log("=== Step 6: Cleanup ===")
    try:
        AstraAdmin().close_experiment(experiment_id)
        log("✓ Experiment closed")
    except Exception as e:
        log(f"⚠ Warning - close error: {e}")
    
    try:
        AstraAdmin().dispose()
        log("✓ ASTRA connection disposed")
    except Exception as e:
        log(f"⚠ Warning - dispose error: {e}")
    
    return len(available_datasets) > 0

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 FOUND WORKING DATASETS!")
        print("Check the results folder for exported CSV files")
        print("These dataset definitions work with your experiment data")
    else:
        print("\n❌ No datasets found")
        print("This helps us understand why CSV export was failing")
    
    print("\nThis analysis shows:")
    print("• Which dataset definitions actually contain data")
    print("• What the data structure looks like")
    print("• Whether CSV export works for each definition")
    print("• Why your original automation script's CSV export failed")
