# Monocle Tracing Setup

## ✅ Monocle-apptrace Enabled

Monocle tracing is now enabled in all entry points:
- `predict.py`
- `serve.py`
- `integrated_orchestrator.py`

## Configuration

### Environment Variables

```bash
# Okahu export (optional)
export OKAHU_API_KEY="your-okahu-key"
export MONOCLE_EXPORTER="okahu"

# File export (default)
export MONOCLE_EXPORTER="file"
export MONOCLE_OUTPUT_DIR="./traces"
```

## How It Works

`monocle-apptrace` automatically traces:
- All agent method calls
- LLM API calls (Gemini)
- Tool invocations (JIRA, Jenkins)
- Message passing between agents

No decorators needed - tracing is automatic!

## View Traces

### Local (File Export)
```bash
# Traces saved to ./traces directory
ls -la traces/
cat traces/latest.json
```

### Okahu Dashboard
1. Set `OKAHU_API_KEY`
2. Set `MONOCLE_EXPORTER=okahu`
3. Visit https://app.okahu.ai/traces
4. View "qaops-multiagent-orchestrator" workflow

## Test Tracing

```bash
# Run prediction with tracing
python predict.py '[ERROR] test_login FAILED'

# Check traces
ls traces/
```