#!/usr/bin/env python3
"""
Enhanced GPC Automation - Complete Data Collection & Analysis

This script:
1. Creates a timestamped results folder for each run
2. Executes the full GPC automation workflow 
3. Exports XML results and CSV datasets
4. Extracts and displays molecular weight values
5. Saves a summary text file with all results
"""

import os
import uuid
import re
import shutil
from datetime import datetime
from astra_admin import AstraAdmin

# =============================================================================
# CONFIGURATION PARAMETERS
# =============================================================================

# ASTRA Method Settings
ASTRA_METHOD_PATH = r"//dbf/Method Builder/Owen/test_method_3"
APP_NAME = "Enhanced GPC Test"
APP_VERSION = "1.0.0.0"

# File Paths and Directories
BASE_RESULTS_DIR = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
FOLDER_PREFIX = "gpc_run"  # Creates folders like "gpc_run_20260113_151025"

# Data Export Settings
EXPORT_XML_RESULTS = True
EXPORT_CSV_DATASETS = True
EXPORT_EXPERIMENT_FILE = True
CREATE_SUMMARY_FILE = True

# Dataset Definitions to Export (must match ASTRA dataset names exactly)
DATASET_EXPORTS = [
    ("masses vs volume", "Mass chromatogram data"),
    ("rms radius vs volume", "RMS radius chromatogram data")
]

# Display Settings
SHOW_MOLECULAR_WEIGHTS_IN_TERMINAL = True
PDI_DECIMAL_PLACES = 3  # Extra precision for polydispersity
MW_DECIMAL_PLACES = 1   # Standard precision for molecular weights

# Timeout Settings (if needed in future)
INSTRUMENT_WAIT_TIMEOUT = 300  # seconds
COLLECTION_TIMEOUT = 1800      # 30 minutes max collection time

# =============================================================================

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def extract_peak_results(xml_content):
    """Extract peak molecular weight results from ASTRA XML"""
    try:
        lines = xml_content.split('\n')
        peak_data = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for molar mass results
            if '<result type="molar mass">' in line:
                if i + 1 < len(lines) and i + 2 < len(lines):
                    name_line = lines[i + 1].strip()
                    scalar_line = lines[i + 2].strip()
                    
                    # Extract name
                    name_match = re.search(r'<name>(.+?)</name>', name_line)
                    if name_match:
                        name = name_match.group(1)
                        
                        # Handle different XML attribute orders
                        scalar_match = re.search(r'<scalar.*?units="([^"]*)".*?uncertainty="([^"]*)".*?peak="(\d+)".*?>([^<]*)</scalar>', scalar_line)
                        
                        if not scalar_match:
                            scalar_match = re.search(r'<scalar.*?units="([^"]*)".*?peak="(\d+)".*?uncertainty="([^"]*)".*?>([^<]*)</scalar>', scalar_line)
                            if scalar_match:
                                units = scalar_match.group(1)
                                peak_num = int(scalar_match.group(2))
                                uncertainty = float(scalar_match.group(3))
                                value_str = scalar_match.group(4).strip()
                        else:
                            units = scalar_match.group(1)
                            uncertainty = float(scalar_match.group(2))
                            peak_num = int(scalar_match.group(3))
                            value_str = scalar_match.group(4).strip()
                        
                        if scalar_match and value_str != 'n/a':
                            value = float(value_str)
                            pct_uncertainty = (uncertainty / value) * 100
                            
                            if peak_num not in peak_data:
                                peak_data[peak_num] = {}
                            
                            peak_data[peak_num][name] = {
                                'value': value,
                                'units': units,
                                'uncertainty_pct': pct_uncertainty
                            }
            
            # Look for polydispersity (PDI)
            elif '<result type="polydispersity">' in line:
                if i + 1 < len(lines) and i + 2 < len(lines):
                    name_line = lines[i + 1].strip()
                    if '<name>Mw/Mn</name>' in name_line:
                        scalar_line = lines[i + 2].strip()
                        scalar_match = re.search(r'<scalar.*?uncertainty="([^"]*)".*?peak="(\d+)".*?>([^<]*)</scalar>', scalar_line)
                        
                        if not scalar_match:
                            scalar_match = re.search(r'<scalar.*?peak="(\d+)".*?uncertainty="([^"]*)".*?>([^<]*)</scalar>', scalar_line)
                            if scalar_match:
                                peak_num = int(scalar_match.group(1))
                                uncertainty = float(scalar_match.group(2))
                                value = float(scalar_match.group(3))
                        else:
                            uncertainty = float(scalar_match.group(1))
                            peak_num = int(scalar_match.group(2))
                            value = float(scalar_match.group(3))
                        
                        if scalar_match:
                            pct_uncertainty = (uncertainty / value) * 100
                            
                            if peak_num not in peak_data:
                                peak_data[peak_num] = {}
                            
                            peak_data[peak_num]['Mw/Mn'] = {
                                'value': value,
                                'units': '',
                                'uncertainty_pct': pct_uncertainty
                            }
            
            # Look for rms radius results  
            elif '<result type="rms radius">' in line:
                if i + 1 < len(lines) and i + 2 < len(lines):
                    name_line = lines[i + 1].strip()
                    scalar_line = lines[i + 2].strip()
                    
                    name_match = re.search(r'<name>(.+?)</name>', name_line)
                    if name_match and name_match.group(1) == 'rz':
                        scalar_match = re.search(r'<scalar.*?units="([^"]*)".*?uncertainty="([^"]*)".*?peak="(\d+)".*?>([^<]*)</scalar>', scalar_line)
                        
                        if not scalar_match:
                            scalar_match = re.search(r'<scalar.*?units="([^"]*)".*?peak="(\d+)".*?uncertainty="([^"]*)".*?>([^<]*)</scalar>', scalar_line)
                            if scalar_match:
                                units = scalar_match.group(1)
                                peak_num = int(scalar_match.group(2))
                                uncertainty = float(scalar_match.group(3))
                                value_str = scalar_match.group(4).strip()
                        else:
                            units = scalar_match.group(1)
                            uncertainty = float(scalar_match.group(2))
                            peak_num = int(scalar_match.group(3))
                            value_str = scalar_match.group(4).strip()
                        
                        if scalar_match and value_str != 'n/a':
                            value = float(value_str)
                            pct_uncertainty = (uncertainty / value) * 100
                            
                            if peak_num not in peak_data:
                                peak_data[peak_num] = {}
                            
                            peak_data[peak_num]['rz'] = {
                                'value': value,
                                'units': units,
                                'uncertainty_pct': pct_uncertainty
                            }
        
        return peak_data
        
    except Exception as e:
        log(f"Error parsing XML: {e}")
        return {}

def format_value_with_uncertainty(value, units, uncertainty_pct, extra_precision=False):
    """Format value with uncertainty like ASTRA GUI"""
    if value >= 1000:
        formatted_value = f"{value:.3e}"
    else:
        formatted_value = f"{value:.1f}"
    
    # Use configurable precision
    precision = f".{PDI_DECIMAL_PLACES}f" if extra_precision else f".{MW_DECIMAL_PLACES}f"
    return f"{formatted_value} (±{uncertainty_pct:{precision}}%)"

def display_and_save_results(peak_data, results_folder):
    """Display results in terminal and save summary to file"""
    summary_lines = []
    
    print("\n" + "="*50)
    print("🎯 MOLECULAR WEIGHT ANALYSIS RESULTS")
    print("="*50)
    
    summary_lines.append("="*50)
    summary_lines.append("🎯 MOLECULAR WEIGHT ANALYSIS RESULTS")
    summary_lines.append("="*50)
    
    for peak_num in sorted(peak_data.keys()):
        data = peak_data[peak_num]
        
        peak_header = f"🔬 Peak {peak_num}"
        peak_divider = "-" * 30
        
        print(f"\n{peak_header}")
        print(peak_divider)
        
        summary_lines.append(f"\n{peak_header}")
        summary_lines.append(peak_divider)
        
        # Molar mass moments
        if any(key in data for key in ['Mn', 'Mw', 'Mp', 'Mz']):
            mass_header = "📊 Molar mass moments (g/mol)"
            print(mass_header)
            print()
            
            summary_lines.append(mass_header)
            summary_lines.append("")
            
            if 'Mn' in data:
                mn = data['Mn']
                formatted = format_value_with_uncertainty(mn['value'], mn['units'], mn['uncertainty_pct'])
                line = f"  Mn: {formatted}"
                print(line)
                summary_lines.append(line)
            
            if 'Mw' in data:
                mw = data['Mw']
                formatted = format_value_with_uncertainty(mw['value'], mw['units'], mw['uncertainty_pct'])
                line = f"  Mw: {formatted}"
                print(line)
                summary_lines.append(line)
                
            if 'Mp' in data:
                mp = data['Mp'] 
                formatted = format_value_with_uncertainty(mp['value'], mp['units'], mp['uncertainty_pct'])
                line = f"  Mp: {formatted}"
                print(line)
                summary_lines.append(line)
            
            print()
            summary_lines.append("")
        
        # Polydispersity with extra precision
        if 'Mw/Mn' in data:
            pdi_header = "📈 Polydispersity"
            print(pdi_header)
            print()
            
            summary_lines.append(pdi_header)
            summary_lines.append("")
            
            pdi = data['Mw/Mn']
            formatted = format_value_with_uncertainty(pdi['value'], '', pdi['uncertainty_pct'], extra_precision=True)
            line = f"  Mw/Mn: {formatted}"
            print(line)
            print()
            
            summary_lines.append(line)
            summary_lines.append("")
        
        # RMS radius
        if 'rz' in data:
            radius_header = "🔵 RMS radius moments (nm)"
            print(radius_header)
            print()
            
            summary_lines.append(radius_header)
            summary_lines.append("")
            
            rz = data['rz']
            formatted = format_value_with_uncertainty(rz['value'], rz['units'], rz['uncertainty_pct'])
            line = f"  rz: {formatted}"
            print(line)
            print()
            
            summary_lines.append(line)
            summary_lines.append("")
    
    # Save summary to file
    summary_file = os.path.join(results_folder, "molecular_weight_summary.txt")
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        log(f"✓ Molecular weight summary saved to: {os.path.basename(summary_file)}")
    except Exception as e:
        log(f"⚠ Warning: Could not save summary file: {e}")
    
    print("="*50)
    print("✅ SUCCESS: Complete molecular weight analysis!")
    print("💾 All data saved to timestamped results folder")
    print("="*50)

def main():
    """Enhanced GPC automation with organized data saving"""
    log("🚀 Enhanced GPC Automation with Complete Data Organization")
    log("Creates timestamped folders and extracts molecular weight data")
    
    # Display current configuration
    log(f"📋 ASTRA Method: {ASTRA_METHOD_PATH}")
    log(f"📁 Results Directory: {BASE_RESULTS_DIR}")
    log(f"🔬 App Identity: {APP_NAME} v{APP_VERSION}")
    
    # Create timestamped results folder for this run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_results_folder = os.path.join(BASE_RESULTS_DIR, f"{FOLDER_PREFIX}_{timestamp}")
    
    try:
        os.makedirs(run_results_folder, exist_ok=True)
        log(f"📁 Created results folder: {os.path.basename(run_results_folder)}")
    except Exception as e:
        log(f"❌ Could not create results folder: {e}")
        return False
    
    admin = None
    experiment_id = None
    
    try:
        # Step 1: Set automation identity
        log("=== Step 1: Setting Automation Identity ===")
        client_id = uuid.uuid4().hex
        
        admin = AstraAdmin()
        admin.set_automation_identity(
            APP_NAME, 
            APP_VERSION,
            os.getpid(),
            client_id,
            1
        )
        log("✓ Automation identity set")
        
        # Step 2: Wait for instruments
        log("=== Step 2: Waiting for Instruments ===")
        admin.wait_for_instruments()
        log("✓ Instruments detected")
        
        # Step 3: Create experiment
        log("=== Step 3: Creating Experiment ===")
        experiment_id = admin.new_experiment_from_template(ASTRA_METHOD_PATH)
        log(f"✓ Experiment created - ID: {experiment_id}")
        
        # Step 4: Start data collection
        log("=== Step 4: Starting Data Collection ===")
        admin.start_collection(experiment_id)
        log("✓ Collection started")
        
        # Step 5: Wait for GPC signal
        log("=== Step 5: Waiting for GPC Auto-Inject Signal ===")
        admin.wait_waiting_for_auto_inject()
        log("✓ GPC auto-inject signal received!")
        
        # Step 6: Wait for collection to start
        log("=== Step 6: Waiting for Collection to Start ===")
        admin.wait_collection_started()
        log("✓ Data collection started")
        
        # Step 7: Wait for collection to finish
        log("=== Step 7: Waiting for Collection to Finish ===")
        collection_start_time = datetime.now()
        admin.wait_collection_finished()
        collection_end_time = datetime.now()
        collection_duration = (collection_end_time - collection_start_time).total_seconds() / 60
        log(f"✓ Data collection completed ({collection_duration:.2f} minutes)")
        
        # Step 8: Wait for data processing
        log("=== Step 8: Waiting for Data Processing ===")
        admin.wait_experiment_run()
        log("✓ Data processing completed")
        
        # Step 9: Save experiment with data
        if EXPORT_EXPERIMENT_FILE:
            log("=== Step 9: Saving Complete Experiment ===")
            experiment_filename = f"experiment_{timestamp}.aex"
            experiment_path = os.path.join(run_results_folder, experiment_filename)
            admin.save_experiment(experiment_id, experiment_path)
            
            if os.path.exists(experiment_path):
                exp_size = os.path.getsize(experiment_path)
                log(f"✓ Experiment saved: {exp_size:,} bytes")
        
        # Step 10: Export XML results and extract molecular weights
        if EXPORT_XML_RESULTS:
            log("=== Step 10: Exporting and Analyzing Results ===")
            results_filename = f"results_{timestamp}.xml"
            results_path = os.path.join(run_results_folder, results_filename)
            
            admin.save_results(experiment_id, results_path)
            
            if os.path.exists(results_path):
                results_size = os.path.getsize(results_path)
                log(f"✓ XML results exported: {results_size:,} bytes")
                
                # Extract and display molecular weight data
                if SHOW_MOLECULAR_WEIGHTS_IN_TERMINAL:
                    try:
                        with open(results_path, 'r', encoding='utf-8') as f:
                            xml_content = f.read()
                        
                        log("🔬 Extracting molecular weight data...")
                        peak_data = extract_peak_results(xml_content)
                        
                        if peak_data:
                            # Display results in terminal and save summary
                            display_and_save_results(peak_data, run_results_folder)
                        else:
                            log("⚠ No molecular weight data found in XML")
                            
                    except Exception as extract_error:
                        log(f"⚠ Warning: Could not extract molecular weights: {extract_error}")
        
        # Step 11: Export CSV datasets
        if EXPORT_CSV_DATASETS:
            log("=== Step 11: Exporting CSV Datasets ===")
            
            exported_csv_count = 0
            
            for dataset_name, description in DATASET_EXPORTS:
                try:
                    log(f"Exporting dataset: '{dataset_name}'")
                    
                    csv_filename = f"chromatogram_{dataset_name.replace(' ', '_')}_{timestamp}.csv"
                    csv_path = os.path.join(run_results_folder, csv_filename)
                    
                    success = admin.save_data_set(experiment_id, dataset_name, csv_path)
                    
                    if success and os.path.exists(csv_path):
                        csv_size = os.path.getsize(csv_path)
                        log(f"  ✓ {description}: {csv_size:,} bytes")
                        exported_csv_count += 1
                    else:
                        log(f"  ⚠ Failed to export '{dataset_name}'")
                        
                except Exception as csv_error:
                    log(f"  ✗ Error exporting '{dataset_name}': {csv_error}")
            
            log(f"✓ Exported {exported_csv_count} CSV dataset files")
        
        # Step 12: Final Summary
        log("=== Step 12: Complete! ===")
        log("📁 All data saved to timestamped results folder:")
        log(f"   📂 Folder: {os.path.basename(run_results_folder)}")
        
        if EXPORT_XML_RESULTS:
            log(f"   📄 XML Results: {results_filename}")
        if EXPORT_CSV_DATASETS:
            log(f"   📊 CSV Datasets: {exported_csv_count} files")
        if CREATE_SUMMARY_FILE and SHOW_MOLECULAR_WEIGHTS_IN_TERMINAL:
            log(f"   📝 Summary: molecular_weight_summary.txt")
        if EXPORT_EXPERIMENT_FILE:
            log(f"   💾 Experiment: {experiment_filename}")
        
        return True
        
    except Exception as main_error:
        log(f"❌ Main automation error: {main_error}")
        return False
    
    finally:
        # Always clean up properly
        log("=== Cleanup ===")
        
        if experiment_id is not None and admin is not None:
            try:
                admin.close_experiment(experiment_id)
                log("✓ Experiment closed")
            except Exception as e:
                log(f"⚠ Warning closing experiment: {e}")
        
        if admin is not None:
            try:
                admin.dispose()
                log("✓ ASTRA connection disposed")
            except Exception as e:
                log(f"⚠ Warning disposing ASTRA: {e}")

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "="*60)
        print("🎉 ENHANCED GPC AUTOMATION COMPLETE!")
        print("✅ Full workflow executed successfully")
        print("💾 All data saved in timestamped results folder")
        print("📊 Molecular weight analysis completed and displayed")
        print("📁 Check the results folder for all exported files")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ AUTOMATION FAILED")
        print("Check the log messages above for details")
        print("="*60)
