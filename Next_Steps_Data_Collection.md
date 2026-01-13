# Next Steps: Data Collection Workflow

## Current Status ✅
The `simple_experiment_test.py` script is ready to test:
- Follows Wyatt's exact initialization sequence
- Creates experiment using proper wrapper methods
- Leaves experiment open for inspection
- Should work without hanging if event system is properly initialized

## Test Plan for Simple Experiment Creation

### Prerequisites
- Close any running ASTRA instances
- Ensure method template exists: `//dbf/Method Builder/Owen/test_method_3`

### Test Steps
```bash
cd "C:\Users\owenm\OneDrive\Desktop\gpc\gpc-automation"
python simple_experiment_test.py
```

### Expected Results
- Script should complete without hanging
- ASTRA opens automatically
- Experiment is created and visible in ASTRA UI
- Can inspect experiment properties manually

---

## Next Phase: Full Data Collection Workflow

Once experiment creation works reliably, implement full collection workflow:

### 1. Start Collection Phase
```python
# After experiment creation:
AstraAdmin().start_collection(experiment_id)

# Wait for collection phases (these should not hang if events work):
AstraAdmin().wait_preparing_for_collection()
AstraAdmin().wait_waiting_for_auto_inject()
```

### 2. Injection Detection Phase
```python
# Manual approach - let user control timing:
print("ASTRA is ready for injection")
print("Trigger your Waters HPLC injection now...")
input("Press ENTER after injection is triggered...")

# Wait for collection to start and finish:
AstraAdmin().wait_collection_started()
AstraAdmin().wait_collection_finished()
```

### 3. Data Export Phase
```python
# Save experiment
exp_path = "output.astrax"
AstraAdmin().save_experiment(experiment_id, exp_path)

# Export results and datasets
AstraAdmin().save_results(experiment_id, "results.xml")
AstraAdmin().save_data_set(experiment_id, "Molar Mass Distribution", "dataset.csv")
```

### 4. Parameter Setting (Optional)
```python
# Before starting collection, can set parameters:
sample_info = SampleInfo(name="Test Sample", concentration=0.002, ...)
AstraAdmin().set_sample(experiment_id, sample_info)
AstraAdmin().set_injected_volume(experiment_id, 0.100)  # 100 µL in mL
AstraAdmin().set_pump_flow_rate(experiment_id, 0.5)
```

## Key Event Sequence for Full Workflow

1. **Initialization**
   - `set_automation_identity()`
   - `wait_for_instruments()` ← Critical for event system

2. **Experiment Setup**
   - `new_experiment_from_template()`
   - Set parameters (optional)

3. **Collection Workflow**
   - `start_collection()`
   - `wait_preparing_for_collection()`
   - `wait_waiting_for_auto_inject()`
   - [User triggers injection]
   - `wait_collection_started()`
   - `wait_collection_finished()`

4. **Data Export**
   - `save_experiment()`
   - `save_results()`
   - `save_data_set()`

5. **Cleanup** (optional)
   - Leave open for inspection, or
   - `close_experiment()` and `request_quit()`

## Alternative: Use Wyatt's High-Level Method

Instead of manual collection workflow, use Wyatt's `collect_data()` method:

```python
# This handles the entire collection workflow internally:
sample_info = SampleInfo(name="Sample", concentration=0.002, ...)

AstraAdmin().collect_data(
    method_path="//dbf/Method Builder/Owen/test_method_3",
    experiment_path="output.astrax", 
    sample=sample_info,
    duration=30.0,        # minutes
    injection_volume=100, # µL  
    flow_rate=0.5,       # mL/min
    progress_update=print # callback for progress
)
```

This method internally handles all the event waiting and should be more reliable.

## Critical Success Factors

1. **Event System Must Work**: If `simple_experiment_test.py` hangs, fix event initialization first
2. **Follow Wyatt's Sequence**: Don't bypass or modify their intended workflow
3. **User-Controlled Timing**: Let user trigger injection and confirm completion
4. **Leave Open for Inspection**: Don't close ASTRA/experiment until verified

## Troubleshooting If Collection Hangs

1. **Check which wait method hangs**: Add logging between each wait call
2. **Use manual confirmation**: Replace hanging wait with user input
3. **Verify ASTRA UI state**: Check if ASTRA actually transitions to expected states
4. **Consider polling fallback**: If events fail, poll experiment status instead

The key insight: If the event system works for experiment creation, it should work for collection too.