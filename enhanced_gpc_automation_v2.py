#!/usr/bin/env python3
"""
Enhanced GPC Automation v2 - Using High-Level collect_data() Method

This script:
1. Creates a timestamped results folder for each run
2. Uses ASTRA's high-level collect_data() method (like official examples)
3. Exports XML results and CSV datasets
4. Extracts and displays molecular weight values
5. Saves a summary text file with all results

Based on the official ASTRA SDK command_line_app.py run_sequence() method.
"""

import os
import uuid
import re
import shutil
from datetime import datetime
from astra_admin import AstraAdmin, SampleInfo

# =============================================================================
# CONFIGURATION PARAMETERS
# =============================================================================

# ASTRA Method Settings
ASTRA_METHOD_PATH = r"//dbf/Method Builder/Owen/test_method_3"
APP_NAME = "Enhanced GPC Test v2"
APP_VERSION = "2.0.0.0"

# Sample Information (required for collect_data method)
SAMPLE_NAME = "GPC Test Sample"
SAMPLE_DESCRIPTION = "Automated GPC Test Run"
SAMPLE_DNDC = 0.185  # dn/dc (mL/g) - typical polymer value
SAMPLE_A2 = 0.0      # A2 (mol mL/g^2) - second virial coefficient
SAMPLE_UV_EXTINCTION = 0.0  # UV extinction (mL/(mg cm))
SAMPLE_CONCENTRATION = 2.0   # Concentration (mg/mL)

# Collection Parameters
COLLECTION_DURATION = 0.0    # Duration in minutes (0 = automatic from method)
INJECTION_VOLUME = 0.0       # Injection volume in microL (0 = from method)
FLOW_RATE = -1.0            # Flow rate mL/min (-1 = from method)

# File Paths and Directories
BASE_RESULTS_DIR = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
FOLDER_PREFIX = "gpc_run_v2"  # Creates folders like "gpc_run_v2_20260113_151025"

# Data Export Settings
EXPORT_XML_RESULTS = True
EXPORT_CSV_DATASETS = True
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

# =============================================================================

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def progress_callback(message: str):
    """Progress callback for collect_data method"""
    log(f"ASTRA: {message}")

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
                        
                        if scalar_match and value_str != 'n/a' and value_str != '~Invalid':
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
                                value_str = scalar_match.group(3).strip()
                        else:
                            uncertainty = float(scalar_match.group(1))
                            peak_num = int(scalar_match.group(2))
                            value_str = scalar_match.group(3).strip()
                        
                        if scalar_match and value_str != 'n/a' and value_str != '~Invalid':
                            value = float(value_str)
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
                        
                        if scalar_match and value_str != 'n/a' and value_str != '~Invalid':
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
    """Enhanced GPC automation using high-level collect_data method"""
    log("🚀 Enhanced GPC Automation v2 - Using High-Level collect_data()")
    log("Based on official ASTRA SDK command_line_app.py examples")
    
    # Display current configuration
    log(f"📋 ASTRA Method: {ASTRA_METHOD_PATH}")
    log(f"📁 Results Directory: {BASE_RESULTS_DIR}")
    log(f"🔬 App Identity: {APP_NAME} v{APP_VERSION}")
    log(f"🧪 Sample: {SAMPLE_NAME} ({SAMPLE_DESCRIPTION})")
    
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
        
        # Step 3: Create sample information
        log("=== Step 3: Preparing Sample Information ===")
        sample_info = SampleInfo(
            name=SAMPLE_NAME,
            description=SAMPLE_DESCRIPTION,
            dndc=SAMPLE_DNDC,
            a2=SAMPLE_A2,
            uvExtinction=SAMPLE_UV_EXTINCTION,
            concentration=SAMPLE_CONCENTRATION
        )
        log(f"✓ Sample configured: {SAMPLE_NAME}")
        log(f"  dn/dc: {SAMPLE_DNDC} mL/g")
        log(f"  Concentration: {SAMPLE_CONCENTRATION} mg/mL")
        
        # Step 4: Complete data collection using high-level method
        log("=== Step 4: Complete Data Collection (High-Level Method) ===")
        experiment_filename = f"experiment_{timestamp}.aex"
        experiment_path = os.path.join(run_results_folder, experiment_filename)
        
        log("Starting complete automated data collection...")
        log("This includes: experiment creation, data collection, processing, and saving")
        
        # This is the high-level method from the official examples
        admin.collect_data(
            ASTRA_METHOD_PATH,      # template/method path
            experiment_path,         # where to save the experiment
            sample_info,            # sample information
            COLLECTION_DURATION,    # duration (0 = automatic)
            INJECTION_VOLUME,       # injection volume (0 = from method) 
            FLOW_RATE,              # flow rate (-1 = from method)
            progress_callback       # progress callback function
        )
        
        log("✓ Complete data collection finished!")
        
        # Step 5: Verify experiment file was created
        if os.path.exists(experiment_path):
            exp_size = os.path.getsize(experiment_path)
            log(f"✓ Experiment file created: {exp_size:,} bytes")
        else:
            log("⚠ Warning: Experiment file not found")
            return False
        
        # Step 6: Open the completed experiment for analysis
        log("=== Step 5: Opening Completed Experiment for Analysis ===")
        experiment_id = admin.open_experiment(experiment_path)
        log(f"✓ Experiment opened - ID: {experiment_id}")
        
        # Step 7: Export XML results and extract molecular weights
        if EXPORT_XML_RESULTS:
            log("=== Step 6: Exporting and Analyzing Results ===")
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
        
        # Step 8: Export CSV datasets
        if EXPORT_CSV_DATASETS:
            log("=== Step 7: Exporting CSV Datasets ===")
            
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
        
        # Step 9: Final Summary
        log("=== Step 8: Complete! ===")
        log("📁 All data saved to timestamped results folder:")
        log(f"   📂 Folder: {os.path.basename(run_results_folder)}")
        log(f"   💾 Experiment: {experiment_filename}")
        
        if EXPORT_XML_RESULTS:
            log(f"   📄 XML Results: {results_filename}")
        if EXPORT_CSV_DATASETS:
            log(f"   📊 CSV Datasets: {exported_csv_count} files")
        if CREATE_SUMMARY_FILE and SHOW_MOLECULAR_WEIGHTS_IN_TERMINAL:
            log(f"   📝 Summary: molecular_weight_summary.txt")
        
        # Close the experiment
        admin.close_experiment(experiment_id)
        log("✓ Experiment closed")
        
        return True
        
    except Exception as main_error:
        log(f"❌ Main automation error: {main_error}")
        return False
    
    finally:
        # Always clean up properly
        log("=== Cleanup ===")
        
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
        print("🎉 ENHANCED GPC AUTOMATION v2 COMPLETE!")
        print("✅ Used high-level collect_data() method")
        print("💾 All data saved in timestamped results folder")
        print("📊 Molecular weight analysis completed and displayed")
        print("📁 Check the results folder for all exported files")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ AUTOMATION FAILED")
        print("Check the log messages above for details")
        print("="*60)
