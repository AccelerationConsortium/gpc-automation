#!/usr/bin/env python3
"""
Simple ASTRA Experiment Processor

This script does exactly what the official process_experiment() example does:
1. Opens an existing experiment file
2. Runs the experiment 
3. Saves XML results and CSV datasets
4. Extracts and displays molecular weight values

Use this on experiment files created by your data collection script.
"""

import os
import uuid
import re
from datetime import datetime
from astra_admin import AstraAdmin

# =============================================================================
# CONFIGURATION PARAMETERS
# =============================================================================

APP_NAME = "Simple ASTRA Processor"
APP_VERSION = "1.0.0.0"

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

def display_results(peak_data):
    """Display results in terminal"""
    print("\n" + "="*50)
    print("🎯 MOLECULAR WEIGHT ANALYSIS RESULTS")
    print("="*50)
    
    for peak_num in sorted(peak_data.keys()):
        data = peak_data[peak_num]
        
        peak_header = f"🔬 Peak {peak_num}"
        peak_divider = "-" * 30
        
        print(f"\n{peak_header}")
        print(peak_divider)
        
        # Molar mass moments
        if any(key in data for key in ['Mn', 'Mw', 'Mp', 'Mz']):
            mass_header = "📊 Molar mass moments (g/mol)"
            print(mass_header)
            print()
            
            if 'Mn' in data:
                mn = data['Mn']
                formatted = format_value_with_uncertainty(mn['value'], mn['units'], mn['uncertainty_pct'])
                line = f"  Mn: {formatted}"
                print(line)
            
            if 'Mw' in data:
                mw = data['Mw']
                formatted = format_value_with_uncertainty(mw['value'], mw['units'], mw['uncertainty_pct'])
                line = f"  Mw: {formatted}"
                print(line)
                
            if 'Mp' in data:
                mp = data['Mp'] 
                formatted = format_value_with_uncertainty(mp['value'], mp['units'], mp['uncertainty_pct'])
                line = f"  Mp: {formatted}"
                print(line)
            
            print()
        
        # Polydispersity with extra precision
        if 'Mw/Mn' in data:
            pdi_header = "📈 Polydispersity"
            print(pdi_header)
            print()
            
            pdi = data['Mw/Mn']
            formatted = format_value_with_uncertainty(pdi['value'], '', pdi['uncertainty_pct'], extra_precision=True)
            line = f"  Mw/Mn: {formatted}"
            print(line)
            print()
    
    print("="*50)
    print("✅ SUCCESS: Molecular weight analysis complete!")
    print("="*50)

def main():
    """Simple experiment processor - exactly like official process_experiment()"""
    log("🔬 Simple ASTRA Experiment Processor")
    log("Opens existing experiment, runs it, and exports results")
    
    # Get experiment file path
    experiment_path = input("\nEnter path to experiment file (.aex): ").strip().strip('"')
    
    if not os.path.exists(experiment_path):
        print(f"❌ Error: File not found: {experiment_path}")
        return False
    
    # Get output directory 
    output_dir = os.path.dirname(experiment_path)
    base_name = os.path.splitext(os.path.basename(experiment_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
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
        
        # Step 3: Open experiment (exactly like official example)
        log("=== Step 3: Opening Experiment ===")
        experiment_id = admin.open_experiment(experiment_path)
        log(f"✓ Experiment opened - ID: {experiment_id}")
        
        # Step 4: Run experiment (exactly like official example)
        log("=== Step 4: Running Experiment ===")
        log("Processing data and calculating molecular weights...")
        admin.run_experiment(experiment_id)
        log("✓ Experiment run completed")
        
        # Step 5: Save XML results
        log("=== Step 5: Saving Results ===")
        results_filename = f"{base_name}_results_{timestamp}.xml"
        results_path = os.path.join(output_dir, results_filename)
        
        admin.save_results(experiment_id, results_path)
        
        if os.path.exists(results_path):
            results_size = os.path.getsize(results_path)
            log(f"✓ XML results saved: {results_filename} ({results_size:,} bytes)")
            
            # Extract and display molecular weight data
            if SHOW_MOLECULAR_WEIGHTS_IN_TERMINAL:
                try:
                    with open(results_path, 'r', encoding='utf-8') as f:
                        xml_content = f.read()
                    
                    log("🔬 Extracting molecular weight data...")
                    peak_data = extract_peak_results(xml_content)
                    
                    if peak_data:
                        display_results(peak_data)
                    else:
                        log("⚠ No molecular weight data found in XML")
                        
                except Exception as extract_error:
                    log(f"⚠ Warning: Could not extract molecular weights: {extract_error}")
        else:
            log("❌ Error: Results file was not created")
            return False
        
        # Step 6: Export CSV datasets
        log("=== Step 6: Exporting CSV Datasets ===")
        exported_csv_count = 0
        
        for dataset_name, description in DATASET_EXPORTS:
            try:
                log(f"Exporting dataset: '{dataset_name}'")
                
                csv_filename = f"{base_name}_{dataset_name.replace(' ', '_')}_{timestamp}.csv"
                csv_path = os.path.join(output_dir, csv_filename)
                
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
        
        # Step 7: Summary
        log("=== Step 7: Complete! ===")
        log(f"📁 Output directory: {output_dir}")
        log(f"📄 XML Results: {results_filename}")
        log(f"📊 CSV Datasets: {exported_csv_count} files")
        
        return True
        
    except Exception as main_error:
        log(f"❌ Processing error: {main_error}")
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
        print("🎉 EXPERIMENT PROCESSING COMPLETE!")
        print("✅ Used official open/run/save approach")
        print("📊 Molecular weight analysis completed and displayed")
        print("📁 Check output directory for all files")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ PROCESSING FAILED")
        print("Check the log messages above for details")
        print("="*60)
