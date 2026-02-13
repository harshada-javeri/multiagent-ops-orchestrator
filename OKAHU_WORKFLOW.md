# Okahu Tracing Workflow

Visual guide showing how traces flow from your application to Okahu dashboard.

## 📊 Tracing Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  predict.py / serve.py / integrated_orchestrator.py             │
│     │                                                           │
│     ├─> from monocle_apptrace import setup_monocle_telemetry   │
│     └─> setup_monocle_telemetry(                               │
│             workflow_name="qaops-multiagent-orchestrator"       │
│         )                                                       │
│                                                                 │
│     When agents run, traces are automatically captured:         │
│     ✓ Agent.process()                                          │
│     ✓ LLM API calls (Gemini)                                   │
│     ✓ Tool invocations (JIRA, Jenkins)                         │
│     ✓ Message passing                                          │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ HTTPS POST (JSON traces)
                       │ Uses: os.environ["OKAHU_API_KEY"]
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              OKAHU INGESTION ENDPOINT                           │
│              https://ingest.okahu.io                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       │ Processes and stores traces
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                  OKAHU PORTAL                                   │
│              https://portal.okahu.co                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1️⃣  Browse Discovered Components                              │
│      └─> Shows: "qaops-multiagent-orchestrator"                │
│                                                                 │
│  2️⃣  Create New Application                                    │
│      └─> Add discovered workflow as component                   │
│                                                                 │
│  3️⃣  View Traces Dashboard                                     │
│      ├─> Execution timeline                                    │
│      ├─> Agent call graph                                      │
│      ├─> Performance metrics                                   │
│      ├─> Token usage & costs                                   │
│      └─> Error traces                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 Complete Setup Workflow

### Phase 1: One-Time Setup

```
Step 1: Create Okahu Account
  ↓
Login at portal.okahu.co
  ↓
Generate API Key (Settings)
  ↓
Step 2: Set Environment Variable
  ↓
$env:OKAHU_API_KEY = "your-key"
  ↓
Step 3: Verify Setup
  ↓
python verify_okahu.py
  ↓
All checks pass ✅
```

### Phase 2: Run & Discover

```
Step 4: Run Application
  ↓
python predict.py
python serve.py
  ↓
Monocle automatically sends traces
  ↓
Traces arrive at ingest.okahu.io
  ↓
Step 5: Create Application in Okahu
  ↓
Portal → New Application
  ↓
Browse Discovered Components
  ↓
Find: qaops-multiagent-orchestrator
  ↓
Add Selection → Save
```

### Phase 3: Monitor & Analyze

```
Step 6: View Dashboard
  ↓
Navigate to your application
  ↓
Explore traces:
  ├─> Agent execution flow
  ├─> LLM token usage
  ├─> Performance bottlenecks
  └─> Error patterns
```

## 🎯 What Gets Traced

| Component | What's Captured | Why It Matters |
|-----------|----------------|----------------|
| **Agent Calls** | All `.process()` and `.execute()` methods | See agent orchestration flow |
| **LLM API** | Gemini API requests & responses | Track token usage & costs |
| **Tool Usage** | JIRA, Jenkins, Grafana calls | Monitor integration health |
| **Messages** | Inter-agent communication | Debug agent coordination |
| **Timing** | Latency per operation | Identify performance issues |
| **Errors** | Exceptions & failures | Quick troubleshooting |

## 🔍 Trace Anatomy

Each trace contains:

```json
{
  "workflow_name": "qaops-multiagent-orchestrator",
  "trace_id": "abc123...",
  "timestamp": "2026-02-13T10:30:00Z",
  "spans": [
    {
      "name": "TestDiagnosticsAgent.process",
      "duration_ms": 1250,
      "attributes": {
        "agent": "TestDiagnosticsAgent",
        "input_size": 2048,
        "failed_tests_found": 2
      }
    },
    {
      "name": "gemini.generate_content",
      "duration_ms": 980,
      "attributes": {
        "model": "gemini-1.5-flash",
        "input_tokens": 512,
        "output_tokens": 256,
        "cost_usd": 0.00034
      }
    },
    {
      "name": "JiraTool.create_ticket",
      "duration_ms": 450,
      "attributes": {
        "ticket_id": "QA-1234",
        "priority": "high"
      }
    }
  ]
}
```

## 📈 Dashboard Features

### Available in Okahu:

- **Timeline View**: See the sequence of operations
- **Flame Graph**: Visualize nested calls and performance
- **Metrics**: Latency p50/p95/p99, throughput, error rate
- **Cost Tracking**: LLM token usage broken down by agent
- **Filtering**: Search by time range, agent, status
- **Alerts**: Set up notifications for anomalies

## 🚨 Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **No workflow in components** | Component list is empty | Run application first, wait 1-2 min |
| **Traces not appearing** | Dashboard shows no data | Check API key, verify network access |
| **Wrong workflow name** | Different name appears | Check `setup_monocle_telemetry()` call |
| **Network timeout** | Connection errors | Verify `ingest.okahu.io:443` is accessible |

## 💡 Pro Tips

1. **Unique Workflow Names**: Use descriptive names to identify different environments
   ```python
   setup_monocle_telemetry(workflow_name="qaops-prod")
   setup_monocle_telemetry(workflow_name="qaops-staging")
   ```

2. **Test Workflow**: Run test with a different workflow name first
   ```python
   setup_monocle_telemetry(workflow_name="qaops-test")
   ```

3. **Dashboard Bookmarks**: Bookmark common views for quick access

4. **Alert Setup**: Configure alerts for high latency or error spikes

## 📚 Reference

- **Quick Start**: [OKAHU_QUICKSTART.md](OKAHU_QUICKSTART.md)
- **Full Setup Guide**: [OKAHU_APPLICATION_SETUP.md](OKAHU_APPLICATION_SETUP.md)
- **Verification Script**: Run `python verify_okahu.py`
- **End-to-End Test**: Run `python test_okahu_tracing.py`
