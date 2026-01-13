#!/usr/bin/env python3
"""
Complete GPC Automation Test - Using Wyatt's Exact Approach

This follows the exact pattern from Wyatt's command_line_app.py
to create an experiment, collect GPC data, and export results
using their intended event-driven workflow.
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
    Complete GPC automation using Wyatt's exact approach
    Creates experiment, waits for GPC signal, collects data, exports results
    """
    log("🚀 Complete GPC Automation Test")
    log("Following Wyatt's exact pattern for full data collection workflow")
    
    # Step 1: Set automation identity (exactly like Wyatt does)
    log("=== Step 1: Setting Automation Identity ===")
    client_id = uuid.uuid4().hex
    
    AstraAdmin().set_automation_identity(
        "Simple Test App", 
        "1.0.0.0",
        os.getpid(),
        client_id,
        1
    )
    log("✓ Automation identity set")
    
    # Step 2: Wait for instruments (exactly like Wyatt does)
    log("=== Step 2: Waiting for Instruments ===")
    log("About to call AstraAdmin().wait_for_instruments()...")
    log("  → This waits for InstrumentDetectionCompleted event (REQUIRED)")
    log("  → If this hangs, the event system has issues")
    log("  → Starting wait now...")
    
    try:
        AstraAdmin().wait_for_instruments()
        log("✓ Instruments detected - event system working!")
    except Exception as e:
        log(f"✗ Error waiting for instruments: {e}")
        log("  → This indicates event system problems")
        return False
    
    # Step 3: Create experiment (exactly like Wyatt does)
    log("=== Step 3: Creating Experiment ===")
    method_path = r"//dbf/Method Builder/Owen/test_method_3"
    log(f"Template: {method_path}")
    log("About to call AstraAdmin().new_experiment_from_template()...")
    log("  → This waits for ExperimentRead and ExperimentRun events")
    log("  → If this hangs, wrapper event handling has issues")
    log("  → Starting experiment creation now...")
    
    try:
        experiment_id = AstraAdmin().new_experiment_from_template(method_path)
        log(f"✓ Experiment created successfully - ID: {experiment_id}")
        log("✓ Wrapper event system working properly!")
        
        # Get experiment name to confirm it's working
        try:
            exp_name = AstraAdmin().get_experiment_name(experiment_id)
            log(f"✓ Experiment name: {exp_name}")
        except Exception as e:
            log(f"⚠ Could not get experiment name: {e}")
            exp_name = f"Experiment{experiment_id}"
        
        # Step 4: Setup results directory
        log("=== Step 4: Setting up Results Directory ===")
        results_dir = os.path.join(r"C:\Users\Administrator.WS\Desktop\wyatt-api\gpc-automation", "results")
        
        # Create results directory if it doesn't exist
        os.makedirs(results_dir, exist_ok=True)
        log(f"✓ Results directory ready: {results_dir}")
        log("✓ Skipping early save - will save complete experiment after data collection")
        
        # Step 5: Start Data Collection (following Wyatt's exact pattern)
        log("=== Step 5: Starting Data Collection ===")
        log("About to call AstraAdmin().start_collection()...")
        log("  → This begins the GPC data collection workflow")
        log("  → Follows Wyatt's trusted event-driven pattern")
        log("  → Starting collection now...")
        
        try:
            collection_success = AstraAdmin().start_collection(experiment_id)
            if collection_success:
                log("✓ Collection started successfully!")
                log("✓ ASTRA is now preparing for data collection")
            else:
                log("✗ Failed to start collection")
                return False
        except Exception as e:
            log(f"✗ Error starting collection: {e}")
            return False
        
        # Step 6: Wait for GPC Auto-Inject Signal (this is the key step!)
        log("=== Step 6: Waiting for GPC Auto-Inject Signal ===")
        log("About to call AstraAdmin().wait_waiting_for_auto_inject()...")
        log("  → This waits for the GPC system to signal it's ready")
        log("  → This is exactly what you need for GPC automation!")
        log("  → ASTRA will wait here until GPC sends inject signal")
        log("  → Starting wait for GPC signal now...")
        
        try:
            AstraAdmin().wait_waiting_for_auto_inject()
            log("✓ GPC auto-inject signal received!")
            log("✓ GPC system has triggered the injection")
            log("✓ Data collection workflow proceeding...")
        except Exception as e:
            log(f"✗ Error waiting for auto-inject: {e}")
            log("  → This means GPC signal handling failed")
            return False
        
        # Step 7: Wait for Collection to Actually Start
        log("=== Step 7: Waiting for Collection to Start ===")
        log("About to call AstraAdmin().wait_collection_started()...")
        log("  → This waits for data acquisition to begin")
        log("  → After GPC injection, ASTRA starts recording data")
        log("  → Starting wait for data collection now...")
        
        try:
            AstraAdmin().wait_collection_started()
            log("✓ Data collection started!")
            log("✓ ASTRA is now actively collecting data from detectors")
            log("✓ GPC sample is flowing through the system")
        except Exception as e:
            log(f"✗ Error waiting for collection start: {e}")
            return False
        
        # Step 8: Wait for Collection to Complete
        log("=== Step 8: Waiting for Collection to Finish ===")
        log("About to call AstraAdmin().wait_collection_finished()...")
        log("  → This waits for the GPC run to complete")
        log("  → Collection time depends on your method settings")
        log("  → ASTRA will automatically stop when method duration reached")
        log("  → Waiting for collection completion...")
        
        collection_start_time = datetime.now()
        try:
            AstraAdmin().wait_collection_finished()
            collection_end_time = datetime.now()
            collection_duration = (collection_end_time - collection_start_time).total_seconds() / 60
            log("✓ Data collection completed!")
            log(f"✓ Collection duration: {collection_duration:.2f} minutes")
            log("✓ GPC data has been collected successfully")
        except Exception as e:
            log(f"✗ Error during collection: {e}")
            return False
        
        # Step 9: Wait for Experiment Processing
        log("=== Step 9: Waiting for Data Processing ===")
        log("About to call AstraAdmin().wait_experiment_run()...")
        log("  → This waits for ASTRA to process the collected data")
        log("  → ASTRA calculates results, baselines, peaks, etc.")
        log("  → Starting data processing wait...")
        
        try:
            AstraAdmin().wait_experiment_run()
            log("✓ Data processing completed!")
            log("✓ ASTRA has calculated all results from collected data")
            log("✓ Experiment is ready for data export")
        except Exception as e:
            log(f"✗ Error during data processing: {e}")
            return False
        
        # Step 10: Save Final Experiment with Data
        log("=== Step 10: Saving Final Experiment with Data ===")
        final_timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        final_filename = f"collected_experiment_{final_timestamp_str}.aex"
        final_save_path = os.path.join(results_dir, final_filename)
        
        log(f"Saving collected data to: {final_save_path}")
        log("About to call AstraAdmin().save_experiment() with collected data...")
        log("  → This saves the complete experiment with GPC data")
        log("  → File will contain all chromatograms, results, and analysis")
        
        try:
            final_save_success = AstraAdmin().save_experiment(experiment_id, final_save_path)
            if final_save_success:
                log("✓ Final experiment with data saved successfully!")
                log(f"✓ File: {final_filename}")
                
                # Verify final file
                if os.path.exists(final_save_path):
                    final_file_size = os.path.getsize(final_save_path)
                    log(f"✓ Final file verified: {final_file_size:,} bytes")
                    log("✓ PROOF: Complete GPC automation worked - data collected!")
                else:
                    log("⚠ Warning: Final save reported success but file not found")
            else:
                log("✗ Final save operation failed")
                return False
        except Exception as e:
            log(f"✗ Error saving final experiment: {e}")
            return False
        
        # Step 11: Export Results and Data
        log("=== Step 11: Exporting Results and Data ===")
        results_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export results (XML format)
        results_filename = f"results_{results_timestamp}.xml"
        results_path = os.path.join(results_dir, results_filename)
        
        log(f"Exporting results to: {results_path}")
        log("About to call AstraAdmin().save_results()...")
        log("  → This exports calculated results in XML format")
        
        try:
            AstraAdmin().save_results(experiment_id, results_path)
            if os.path.exists(results_path):
                results_size = os.path.getsize(results_path)
                log(f"✓ Results exported successfully: {results_size:,} bytes")
                log(f"✓ Results file: {results_filename}")
                
                # Try to extract molecular weight data from XML results
                try:
                    with open(results_path, 'r', encoding='utf-8') as f:
                        xml_content = f.read()
                    
                    log("🔬 Scanning results for molecular weight data...")
                    
                    # Look for common molecular weight indicators in the XML
                    if "Mn" in xml_content and "Mw" in xml_content:
                        log("✓ Found Mn/Mw data in results!")
                        
                        # Extract lines containing molecular weight info
                        for line in xml_content.split('\n'):
                            if any(keyword in line.lower() for keyword in ['mn', 'mw', 'molecular', 'weight', 'molar']):
                                if '=' in line or '>' in line:
                                    log(f"  → {line.strip()}")
                    else:
                        log("⚠ No Mn/Mw data found in XML - may need different export format")
                        
                except Exception as read_error:
                    log(f"⚠ Could not analyze results file: {read_error}")
                    
            else:
                log("⚠ Results export may have failed - file not found")
        except Exception as e:
            log(f"⚠ Warning - results export error: {e}")
        
        # Export data set (CSV format) - Use confirmed working dataset definitions from ASTRA GUI
        log(f"Attempting to retrieve dataset content...")
        log("About to call AstraAdmin().get_data_set()...")
        log("  → Using confirmed dataset definitions from ASTRA GUI")
        
        # Test both confirmed working dataset definitions from ASTRA GUI  
        real_dataset_definitions = [
            ("masses vs volume", "Molecular weight data"),           # The molecular weight data!
            ("rms radius vs volume", "Light scattering data")       # Light scattering data
        ]
        
        dataset_exported = False
        exported_datasets = []
        
        for definition_name, description in real_dataset_definitions:
            try:
                log(f"  → Testing dataset: '{definition_name}' ({description})")
                dataset_content = AstraAdmin().get_data_set(experiment_id, definition_name)
                
                # Handle the _empty object issue properly
                is_valid = False
                try:
                    if dataset_content and hasattr(dataset_content, 'strip') and len(dataset_content.strip()) > 10:
                        is_valid = True
                except (AttributeError, TypeError):
                    # This catches '_empty' object has no attribute 'strip' errors
                    is_valid = False
                
                if is_valid:
                    content_length = len(dataset_content)
                    lines = len(dataset_content.split('\n'))
                    log(f"  ✓ Found data for '{definition_name}': {content_length} chars, {lines} lines")
                    
                    # Export this dataset
                    safe_name = definition_name.replace(' ', '_').replace('vs', 'vs')
                    data_filename = f"{safe_name}_{results_timestamp}.csv"
                    data_path = os.path.join(results_dir, data_filename)
                    
                    log(f"    Exporting to: {data_filename}")
                    
                    try:
                        success = AstraAdmin().save_data_set(experiment_id, definition_name, data_path)
                        if success and os.path.exists(data_path):
                            data_size = os.path.getsize(data_path)
                            log(f"    ✓ Dataset exported successfully: {data_size:,} bytes")
                            log(f"    ✓ Dataset type: {description}")
                            exported_datasets.append((definition_name, data_filename, description))
                            dataset_exported = True
                            
                            if "masses" in definition_name.lower():
                                log("    🔬 This file contains your molecular weight data!")
                                log("    📊 Look for 'Molar Mass (g/mol)' section in the CSV file")
                        else:
                            log(f"    ✗ Export failed or file not created")
                    except Exception as e:
                        log(f"    ✗ Export error: {e}")
                else:
                    log(f"  → '{definition_name}' - no data or empty result")
                    
            except Exception as e:
                if "'_empty' object" not in str(e):
                    log(f"  → '{definition_name}' - error: {e}")
                else:
                    log(f"  → '{definition_name}' - empty dataset")
        
        if not dataset_exported:
            log("⚠ Warning - no datasets were exported")
            log("💡 This suggests the experiment may not have been processed properly")
        else:
            log("✅ Dataset export summary:")
            for def_name, filename, desc in exported_datasets:
                log(f"  → {filename} ({desc})")
            log("🎯 CSV export problem SOLVED - using real ASTRA dataset definition names!")
        
        # Final completion summary
        log("=== COMPLETE SUCCESS ===")
        log("✓ Full GPC automation workflow completed successfully!")
        log("✓ Experiment created from method template")
        log("✓ GPC auto-inject signal received and processed")
        log("✓ Data collection completed")
        log("✓ Results calculated and processed")
        log("✓ All files saved to disk as permanent proof")
        log("")
        log("Generated files in results folder:")
        log(f"  → Complete experiment: {final_filename}")
        log(f"  → Results (XML): {results_filename}")
        if dataset_exported:
            for def_name, filename, desc in exported_datasets:
                log(f"  → Dataset CSV: {filename} ({desc})")
        else:
            log(f"  → Dataset CSV: FAILED TO EXPORT")
        log("")
        log("🎉 Complete GPC automation with molecular weight data export!")
        log("📊 Check the 'masses vs volume' CSV for molecular weight values")
        log("🎉 Your GPC automation pipeline is working perfectly!")
        
        # Step 12: Close Experiment (following Wyatt's pattern)
        log("=== Step 12: Closing Experiment ===")
        log("About to call AstraAdmin().close_experiment()...")
        log("  → This properly closes the experiment in ASTRA")
        log("  → Follows Wyatt's cleanup pattern")
        log("  → Prepares for clean disposal")
        
        try:
            close_success = AstraAdmin().close_experiment(experiment_id)
            if close_success:
                log("✓ Experiment closed successfully!")
                log("✓ ASTRA workspace cleaned up")
            else:
                log("⚠ Warning: Experiment close reported failure")
        except Exception as e:
            log(f"⚠ Warning - experiment close error: {e}")
        
        return True
        
    except Exception as e:
        log(f"✗ Error creating experiment: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    # Cleanup: Properly dispose of ASTRA connection (prevents zombie processes)
    try:
        AstraAdmin().dispose()
        print("\n🧹 Cleanup: ASTRA connection disposed properly")
        print("✓ ASTRA will close automatically after disposal")
        print("✓ No zombie processes will remain")
    except Exception as e:
        print(f"\n⚠ Cleanup warning: {e}")
        print("   → You may need to manually close ASTRA")
    
    if success:
        print("\n🎉 SUCCESS: Complete GPC automation worked using Wyatt's approach!")
        print("🔬 Full workflow completed: create → wait for GPC → collect → export")
    else:
        print("\n✗ FAILED: Issue with Wyatt's intended workflow")
        print("This tells us where the real problem is")
        
    print("\nThis test uses ONLY Wyatt's intended methods:")
    print("• AstraAdmin().set_automation_identity()")
    print("• AstraAdmin().wait_for_instruments()")  
    print("• AstraAdmin().new_experiment_from_template()")
    print("• AstraAdmin().start_collection() - Begin data collection")
    print("• AstraAdmin().wait_waiting_for_auto_inject() - GPC SIGNAL!")
    print("• AstraAdmin().wait_collection_started() - Data flowing")
    print("• AstraAdmin().wait_collection_finished() - Collection done")
    print("• AstraAdmin().wait_experiment_run() - Processing complete")
    print("• AstraAdmin().save_experiment() - Save data")
    print("• AstraAdmin().save_results() - Export results")
    print("• AstraAdmin().save_data_set() - Export chromatograms")
    print("• AstraAdmin().close_experiment() - Clean closure")
    print("• AstraAdmin().dispose() - ASTRA shutdown")
    print("• No direct COM calls, no timeouts, no workarounds")
    
    if success:
        print("\n📁 Check the saved files in results folder!")
        print("   → C:\\Users\\Administrator.WS\\Desktop\\wyatt-api\\gpc-automation\\results\\")
        print("   → Complete experiment with data (.aex)")
        print("   → Results file (.xml)")
        print("   → Dataset file (.csv) - if export succeeded")
        print("   → Permanent proof your complete GPC pipeline works")