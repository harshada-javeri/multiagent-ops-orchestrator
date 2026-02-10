# ✅ Monocle Tracing Status

## Enabled Components

### Entry Points (Auto-instrumented)
All entry points have `setup_monocle_telemetry()` at the top:

1. ✅ **predict.py** - Line 7
2. ✅ **serve.py** - Line 7  
3. ✅ **integrated_orchestrator.py** - Line 6

### Agents (Auto-traced)
No decorators needed - monocle-apptrace auto-instruments:

1. ✅ **TestDiagnosticsAgent** - `process()` method
2. ✅ **RootCauseAnalyzerAgent** - `process()` method
3. ✅ **ActionPlannerAgent** - `process()` method

## What Gets Traced

- Agent method calls (process, __init__)
- LLM API calls (Gemini generate_content)
- Tool invocations (JIRA, Jenkins)
- Message passing between agents
- Execution time and latency
- Token usage (for LLM calls)

## Test Tracing

```bash
# Install monocle-apptrace
pip install monocle-apptrace

# Test with file export (default)
python predict.py '[ERROR] test_login FAILED'

# Check traces
ls traces/
cat traces/*.json
```

## Export to Okahu

```bash
# Set environment variables
export OKAHU_API_KEY="your-okahu-key"
export MONOCLE_EXPORTER="okahu"

# Run prediction
python predict.py '[ERROR] test FAILED'

# View in Okahu dashboard
# https://app.okahu.ai/traces
# Look for workflow: "qaops-multiagent-orchestrator"
```

## Trace Data Structure

```json
{
  "workflow_name": "qaops-multiagent-orchestrator",
  "spans": [
    {
      "name": "TestDiagnosticsAgent.process",
      "start_time": "2024-01-01T00:00:00Z",
      "duration_ms": 45,
      "attributes": {
        "agent": "TestDiagnostics",
        "input": "CI logs",
        "output": "failed_tests"
      }
    },
    {
      "name": "RootCauseAnalyzerAgent.process",
      "start_time": "2024-01-01T00:00:01Z",
      "duration_ms": 1200,
      "attributes": {
        "agent": "RootCause",
        "llm_model": "gemini-1.5-pro",
        "tokens": 150
      }
    }
  ]
}
```

## Verification Checklist

- [x] monocle-apptrace in requirements.txt
- [x] setup_monocle_telemetry() in predict.py
- [x] setup_monocle_telemetry() in serve.py
- [x] setup_monocle_telemetry() in integrated_orchestrator.py
- [x] All agents inherit from Agent base class
- [x] No manual decorators needed (auto-instrumentation)

## Next Steps

1. Run `python predict.py '[ERROR] test'` to generate traces
2. Check `traces/` directory for local files
3. Set OKAHU_API_KEY to export to Okahu
4. View traces in https://app.okahu.ai/traces
5. Monitor agent performance and token usage