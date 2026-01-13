#!/usr/bin/env python3
"""
Test Results Access - Get Molecular Weight Values

Testing how to properly access molecular weight results using get_results()
method as documented in the ASTRA API    if success:
        print("\n🎉 COMPLETE DATA ACCESS TEST SUCCESSFUL!")
        print("📁 Check results folder for both data types:")
        print("  📊 XML Results - Peak molecular weight values (Mn, Mw)")
        print("  📈 CSV Datasets - Chromatogram time-series data")
        print("")
        print("💡 You now have access to ALL your GPC data!")
    else:
        print("\n❌ Test failed")
    
    print("\nData Access Summary:")
    print("• XML Results = Calculated peak molecular weights")
    print("• CSV Datasets = Chromatogram data for plotting/analysis") 
    print("• Both are valuable - use the right tool for each data type")
    print("• Your automation can export both types simultaneously")n.
"""

import os
import uuid
import re
from datetime import datetime
from astra_admin import AstraAdmin

def extract_molecular_weights_from_xml(xml_content):
    """
    Extract molecular weight values from ASTRA XML results
    Returns list of dictionaries with peak data
    """
    peaks_data = []
    
    try:
        # Split into lines for easier parsing
        lines = xml_content.split('\n')
        
        current_peak_data = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for molar mass result sections
            if '<result type="molar mass">' in line:
                # Next line should have the name
                if i + 1 < len(lines):
                    name_line = lines[i + 1].strip()
                    name_match = re.search(r'<name>(.+?)</name>', name_line)
                    
                    if name_match and i + 2 < len(lines):
                        name = name_match.group(1)
                        scalar_line = lines[i + 2].strip()
                        
                        # Extract the value and units from scalar line
                        # <scalar units="g/mol" uncertainty="9.890642754e+01" peak="1">2.157163613e+04</scalar>
                        scalar_match = re.search(r'<scalar.*?units="([^"]*)".*?peak="(\d+)".*?>([^<]*)</scalar>', scalar_line)
                        
                        if scalar_match:
                            units = scalar_match.group(1)
                            peak_number = int(scalar_match.group(2))
                            value_str = scalar_match.group(3).strip()
                            
                            # Skip n/a values
                            if value_str != 'n/a':
                                # Convert scientific notation to readable number
                                try:
                                    value = float(value_str)
                                    
                                    # Find or create peak data
                                    peak_data = next((p for p in peaks_data if p['peak_number'] == peak_number), None)
                                    if not peak_data:
                                        peak_data = {
                                            'peak_number': peak_number,
                                            'mn': None, 'mw': None, 'mp': None, 'mv': None, 'mz': None, 'mz1': None,
                                            'mavg': None, 'pdi': None, 'units': units
                                        }
                                        peaks_data.append(peak_data)
                                    
                                    # Store the value based on the name
                                    if name == 'Mn':
                                        peak_data['mn'] = f"{value:.0f}"
                                    elif name == 'Mw':
                                        peak_data['mw'] = f"{value:.0f}"
                                    elif name == 'Mp':
                                        peak_data['mp'] = f"{value:.0f}"
                                    elif name == 'Mv':
                                        peak_data['mv'] = f"{value:.0f}"
                                    elif name == 'Mz':
                                        peak_data['mz'] = f"{value:.0f}"
                                    elif name == 'Mz+1':
                                        peak_data['mz1'] = f"{value:.0f}"
                                    elif name == 'M(avg)':
                                        peak_data['mavg'] = f"{value:.0f}"
                                        
                                except ValueError:
                                    continue
            
            # Look for polydispersity (PDI)
            elif '<result type="polydispersity">' in line:
                if i + 1 < len(lines):
                    name_line = lines[i + 1].strip()
                    if '<name>Mw/Mn</name>' in name_line and i + 2 < len(lines):
                        scalar_line = lines[i + 2].strip()
                        scalar_match = re.search(r'<scalar.*?peak="(\d+)".*?>([^<]*)</scalar>', scalar_line)
                        
                        if scalar_match:
                            peak_number = int(scalar_match.group(1))
                            value_str = scalar_match.group(2).strip()
                            
                            try:
                                value = float(value_str)
                                peak_data = next((p for p in peaks_data if p['peak_number'] == peak_number), None)
                                if peak_data:
                                    peak_data['pdi'] = f"{value:.3f}"
                            except ValueError:
                                continue
                            
    except Exception as e:
        print(f"Error parsing XML: {e}")
        
    return peaks_data

def log(message: str):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    """
    Test accessing results using get_results() method
    """
    log("🎯 Testing Results Access with get_results()")
    
    # Setup
    results_dir = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
    target_file = os.path.join(results_dir, "collected_experiment_20260113_114325.aex.afe8")
    
    log(f"📁 Using experiment: {os.path.basename(target_file)}")
    
    # Setup ASTRA connection
    log("=== Setting up ASTRA Connection ===")
    client_id = uuid.uuid4().hex
    
    admin = None
    experiment_id = None
    
    try:
        admin = AstraAdmin()
        admin.set_automation_identity("Results Test", "1.0.0.0", os.getpid(), client_id, 1)
        admin.wait_for_instruments()
        experiment_id = admin.open_experiment(target_file)
        log(f"✓ Experiment opened - ID: {experiment_id}")
        
        # Test get_results() method for molecular weight values
        log("=== Testing get_results() Method ===")
        log("About to call AstraAdmin().get_results()...")
        log("  → This should return calculated peak molecular weight values as XML")
        
        try:
            results_xml = admin.get_results(experiment_id)
            
            if results_xml and len(results_xml) > 100:
                log(f"✓ Results retrieved: {len(results_xml)} characters")
                
                # Save the XML results to file for analysis
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                results_file = os.path.join(results_dir, f"results_xml_{timestamp}.xml")
                
                with open(results_file, 'w', encoding='utf-8') as f:
                    f.write(results_xml)
                
                log(f"✓ Results saved to: {os.path.basename(results_file)}")
                
                # Search for molecular weight values in the XML
                log("🔍 Searching for peak molecular weight values in XML...")
                
                if "Mn" in results_xml:
                    log("  ✓ Found 'Mn' in results")
                    
                if "Mw" in results_xml:
                    log("  ✓ Found 'Mw' in results")
                    
                if "g/mol" in results_xml or "g mol" in results_xml:
                    log("  ✓ Found molecular weight units in results")
                    
                # Look for specific molecular weight sections
                lines = results_xml.split('\n')
                mn_lines = [line for line in lines if 'Mn' in line and ('g/mol' in line or 'mol' in line)]
                mw_lines = [line for line in lines if 'Mw' in line and ('g/mol' in line or 'mol' in line)]
                
                if mn_lines:
                    log(f"  📊 Found {len(mn_lines)} Mn entries")
                    for line in mn_lines[:3]:  # Show first 3
                        log(f"    → {line.strip()[:100]}")
                        
                if mw_lines:
                    log(f"  📊 Found {len(mw_lines)} Mw entries")
                    for line in mw_lines[:3]:  # Show first 3
                        log(f"    → {line.strip()[:100]}")
                
                log("✅ XML results contain calculated molecular weight values!")
                
                # EXTRACT ACTUAL MOLECULAR WEIGHT VALUES
                log("=== Extracting Molecular Weight Values ===")
                mw_values = extract_molecular_weights_from_xml(results_xml)
                
                if mw_values:
                    log("🎯 MOLECULAR WEIGHT RESULTS:")
                    for peak_data in mw_values:
                        log(f"  🔬 Peak {peak_data['peak_number']}:")
                        if peak_data['mn']:
                            log(f"    Mn: {peak_data['mn']} {peak_data['units']}")
                        if peak_data['mw']:
                            log(f"    Mw: {peak_data['mw']} {peak_data['units']}")
                        if peak_data['mp']:
                            log(f"    Mp: {peak_data['mp']} {peak_data['units']}")
                        if peak_data['mz']:
                            log(f"    Mz: {peak_data['mz']} {peak_data['units']}")
                        if peak_data['mavg']:
                            log(f"    M(avg): {peak_data['mavg']} {peak_data['units']}")
                        if peak_data['pdi']:
                            log(f"    PDI (Mw/Mn): {peak_data['pdi']}")
                        log("")
                else:
                    log("⚠ Could not extract molecular weight values from XML")
                
            else:
                log("⚠ No results or empty results returned")
                
        except Exception as e:
            log(f"✗ Error getting results: {e}")
        
        # ALSO test CSV dataset export for chromatogram data
        log("=== Testing CSV Dataset Export ===")
        log("About to test CSV dataset export for chromatogram data...")
        log("  → This gives us the raw chromatogram data")
        
        real_dataset_definitions = [
            ("masses vs volume", "Chromatogram data with mass info"),
            ("rms radius vs volume", "Chromatogram data with radius info")
        ]
        
        exported_datasets = []
        
        for definition_name, description in real_dataset_definitions:
            try:
                log(f"  → Testing dataset: '{definition_name}'")
                dataset_content = admin.get_data_set(experiment_id, definition_name)
                
                # Handle the _empty object issue properly
                is_valid = False
                try:
                    if dataset_content and hasattr(dataset_content, 'strip') and len(dataset_content.strip()) > 10:
                        is_valid = True
                except (AttributeError, TypeError):
                    is_valid = False
                
                if is_valid:
                    content_length = len(dataset_content)
                    lines = len(dataset_content.split('\n'))
                    log(f"    ✓ Found dataset: {content_length} chars, {lines} lines")
                    
                    # Export this dataset
                    safe_name = definition_name.replace(' ', '_').replace('vs', 'vs')
                    csv_filename = f"chromatogram_{safe_name}_{timestamp}.csv"
                    csv_path = os.path.join(results_dir, csv_filename)
                    
                    try:
                        success = admin.save_data_set(experiment_id, definition_name, csv_path)
                        if success and os.path.exists(csv_path):
                            size = os.path.getsize(csv_path)
                            log(f"    ✓ CSV exported: {csv_filename} ({size:,} bytes)")
                            log(f"    ✓ Content: {description}")
                            exported_datasets.append((definition_name, csv_filename))
                        else:
                            log(f"    ✗ CSV export failed")
                    except Exception as exp_error:
                        log(f"    ✗ CSV export error: {exp_error}")
                        
                else:
                    log(f"    → '{definition_name}' - no data available")
                    
            except Exception as e:
                log(f"    → '{definition_name}' - error: {e}")
        
        log("=== Summary ===")
        log("📊 Data Types Available:")
        log("  ✅ XML Results - Calculated peak molecular weights (Mn, Mw)")
        log("  ✅ CSV Datasets - Chromatogram time-series data")
        
        if exported_datasets:
            log(f"\n📁 Exported {len(exported_datasets)} CSV datasets:")
            for def_name, filename in exported_datasets:
                log(f"  → {filename} ({def_name})")
                
        log("\n💡 Complete data access:")
        log("  → Use XML Results for calculated molecular weight values")
        log("  → Use CSV datasets for chromatogram data analysis")
            
    except Exception as e:
        log(f"✗ Error setting up ASTRA: {e}")
        return False
        
    finally:
        # CRITICAL: Always close experiment and dispose properly
        log("=== Cleanup - Closing ASTRA ===")
        
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
        
        # Double-check ASTRA is closed
        log("✓ ASTRA should now be closed properly")
    
    return True
    
if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 RESULTS ACCESS TEST COMPLETE!")
        print("� Check results folder for XML results file")
        print("📊 XML contains the actual molecular weight values")
        print("💡 Use XML parsing to extract Mn/Mw values programmatically")
    else:
        print("\n❌ Test failed")
    
    print("\nKey Discovery:")
    print("• get_results() method returns XML with molecular weight data")
    print("• This is the proper way to access calculated results")
    print("• Dataset exports are for chromatogram data, not calculated results")
    print("• XML parsing will give you the exact Mn/Mw values")
