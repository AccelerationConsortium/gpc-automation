# ASTRA Automation API - Key Requirements Summary

## Critical Discovery: Event System is Mandatory

The ASTRA automation hanging issues were caused by **bypassing Wyatt's required event-based initialization sequence**. The documentation makes clear that certain steps are mandatory and must be done in order.

## Required Initialization Sequence

```python
from astra_admin import AstraAdmin

# Step 1: REQUIRED - Set identity before any other operations
AstraAdmin().set_automation_identity(
    entity_name, entity_version, process_id, client_guid, enabled=1
)

# Step 2: REQUIRED - Wait for InstrumentDetectionCompleted event
AstraAdmin().wait_for_instruments()

# Step 3: Now safe to create experiments
experiment_id = AstraAdmin().new_experiment_from_template(method_path)
```

## Why This Sequence Matters

### 1. SetAutomationIdentity is Required First
- **Must be called before any other COM operations**
- Without it, all functions fail with `E_REQUEST_OUT_OF_SEQUENCE`
- Acts as authentication/registration with ASTRA

### 2. InstrumentDetectionCompleted Event is Mandatory
- **Documentation states: "It is required to wait for the InstrumentDetectionCompleted event before starting any collections"**
- `wait_for_instruments()` waits for this specific event
- Just checking `InstrumentsDetected` property is insufficient - it only indicates detection happened, not that instruments are ready
- The event system must be properly initialized for all subsequent operations

### 3. Event System Drives Everything
- All ASTRA operations are asynchronous
- Events signal completion: `ExperimentRead`, `ExperimentRun`, `PreparingForCollection`, `WaitingForAutoInject`, etc.
- Bypassing the event system breaks the entire communication flow

## What Was Wrong in Previous Implementation

```python
# INCORRECT - bypassed required event waiting
while not aa.has_instrument_detection_completed():  # Wrong approach
    time.sleep(1)

# Direct COM calls without proper event handling
experiment_id = aa.astra_com.NewExperimentFromTemplate(...)  # Breaks event tracking
```

## Correct Implementation Pattern

```python
# CORRECT - follows Wyatt's intended pattern
AstraAdmin().set_automation_identity(...)
AstraAdmin().wait_for_instruments()  # Waits for required event
experiment_id = AstraAdmin().new_experiment_from_template(...)  # Uses wrapper properly
```

## Key Documentation References

1. **Getting Started Guide**: "It is required to wait for the InstrumentDetectionCompleted event...after creating the Astra class instance"
2. **Interface Documentation**: "It is required that before executing any operation...the COM client identifies itself to ASTRA"
3. **Wyatt's Example Code**: `command_line_app.py` shows the exact sequence

## Units and Important Notes

- **Injected Volume**: ASTRA UI shows µL, but automation API expects **mL**
- **Concentration**: ASTRA UI shows mg/mL, but automation API expects **g/mL**
- **AstraAdmin is Singleton**: Always use `AstraAdmin()`, not multiple instances
- **Thread Safety**: Use in single thread only for event handling

## Bottom Line

Don't bypass Wyatt's system - it's designed to work correctly when used as intended. The hanging was caused by skipping mandatory initialization steps, not by flaws in the event system.