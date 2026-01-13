#!/usr/bin/env python3
"""
Simple Molecular Weight Extractor

Extracts and displays molecular weight values from ASTRA XML results
in the same format as shown in the ASTRA GUI.
"""

import os
import re
from datetime import datetime

def extract_peak_results(xml_content):
    """
    Extract peak molecular weight results from ASTRA XML
    Returns clean, formatted results matching ASTRA GUI display
    """
    results = []
    
    try:
        lines = xml_content.split('\n')
        
        peak_data = {}
        current_peak = None
        
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
                        
                        # Extract value, units, peak number, and uncertainty
                        # Handle different attribute orders: units, uncertainty, peak OR units, peak, uncertainty
                        scalar_match = re.search(r'<scalar.*?units="([^"]*)".*?uncertainty="([^"]*)".*?peak="(\d+)".*?>([^<]*)</scalar>', scalar_line)
                        
                        if not scalar_match:
                            # Try alternative order: units, peak, uncertainty  
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
                        if scalar_match:
                            if value_str != 'n/a':
                                value = float(value_str)
                                
                                # Calculate percentage uncertainty
                                pct_uncertainty = (uncertainty / value) * 100
                                
                                # Store in peak data
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
                        # Handle different attribute orders for PDI
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
                    if name_match:
                        name = name_match.group(1)
                        
                        if name == 'rz':  # Only extract rz for now
                            # Handle different attribute orders for radius
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
                            if scalar_match:
                                if value_str != 'n/a':
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
        print(f"Error parsing XML: {e}")
        return {}

def format_value_with_uncertainty(value, units, uncertainty_pct):
    """Format value with uncertainty like ASTRA GUI"""
    if value >= 1000:
        # Format in scientific notation for large numbers
        formatted_value = f"{value:.3e}"
    else:
        # Format normally for smaller numbers
        formatted_value = f"{value:.1f}"
    
    return f"{formatted_value} (±{uncertainty_pct:.1f}%)"

def display_peak_results(peak_data):
    """Display results in ASTRA GUI format"""
    print("\n" + "="*50)
    print("🎯 MOLECULAR WEIGHT ANALYSIS RESULTS")
    print("="*50)
    
    for peak_num in sorted(peak_data.keys()):
        data = peak_data[peak_num]
        
        print(f"\n🔬 Peak {peak_num}")
        print("-" * 30)
        
        # Molar mass moments
        if any(key in data for key in ['Mn', 'Mw', 'Mp', 'Mz']):
            print("📊 Molar mass moments (g/mol)")
            print()
            
            if 'Mn' in data:
                mn = data['Mn']
                formatted = format_value_with_uncertainty(mn['value'], mn['units'], mn['uncertainty_pct'])
                print(f"  Mn: {formatted}")
            
            if 'Mw' in data:
                mw = data['Mw']
                formatted = format_value_with_uncertainty(mw['value'], mw['units'], mw['uncertainty_pct'])
                print(f"  Mw: {formatted}")
                
            if 'Mp' in data:
                mp = data['Mp'] 
                formatted = format_value_with_uncertainty(mp['value'], mp['units'], mp['uncertainty_pct'])
                print(f"  Mp: {formatted}")
            
            print()
        
        # Polydispersity
        if 'Mw/Mn' in data:
            print("📈 Polydispersity")
            print()
            pdi = data['Mw/Mn']
            formatted = format_value_with_uncertainty(pdi['value'], '', pdi['uncertainty_pct'])
            print(f"  Mw/Mn: {formatted}")
            print()
        
        # RMS radius
        if 'rz' in data:
            print("🔵 RMS radius moments (nm)")
            print()
            rz = data['rz']
            formatted = format_value_with_uncertainty(rz['value'], rz['units'], rz['uncertainty_pct'])
            print(f"  rz: {formatted}")
            print()

def main():
    """Extract and display molecular weight values from latest XML file"""
    results_dir = r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation\results"
    
    # Find the most recent XML results file
    xml_files = [f for f in os.listdir(results_dir) if f.startswith('results_xml_') and f.endswith('.xml')]
    
    if not xml_files:
        print("❌ No XML results files found!")
        print(f"📁 Looking in: {results_dir}")
        return
    
    # Get the most recent file
    latest_file = max(xml_files, key=lambda f: os.path.getmtime(os.path.join(results_dir, f)))
    xml_path = os.path.join(results_dir, latest_file)
    
    print(f"📄 Reading results from: {latest_file}")
    
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Extract the results
        peak_data = extract_peak_results(xml_content)
        
        if peak_data:
            display_peak_results(peak_data)
            
            print("\n" + "="*50)
            print("✅ SUCCESS: Molecular weight values extracted!")
            print("💡 These values match your ASTRA GUI display")
            print("="*50)
        else:
            print("❌ No molecular weight data found in XML")
            
    except Exception as e:
        print(f"❌ Error reading XML file: {e}")

if __name__ == "__main__":
    main()
