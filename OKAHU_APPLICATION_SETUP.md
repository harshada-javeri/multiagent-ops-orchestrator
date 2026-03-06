# Okahu Application Setup Guide

Complete guide to creating an Okahu application and viewing traces from your multi-agent orchestrator.

## Prerequisites

✅ **Already Done in This Project:**
- Monocle SDK installed (`monocle_apptrace` in requirements.txt)
- Tracing enabled in all entry points (`predict.py`, `serve.py`, `integrated_orchestrator.py`)
- Workflow name set to: `qaops-multiagent-orchestrator`

## Step 1: Create Okahu Tenant

1. Visit: **https://portal.okahu.co/en/apps/**
2. Login with your **GitHub** or **LinkedIn** account
3. A new tenant will be provisioned automatically

## Step 2: Obtain Okahu API Key

1. After login, navigate to **Settings**
2. Click on **Generate API Key**
3. Copy the generated API key (save it securely)

## Step 3: Set Environment Variable

### On Windows (PowerShell):
```powershell
$env:OKAHU_API_KEY = "your-api-key-here"
```

### On Linux/Mac:
```bash
export OKAHU_API_KEY="your-api-key-here"
```

### Persistent Setup (.env file):
Create a `.env` file in your project root:
```env
OKAHU_API_KEY=your-api-key-here
```

## Step 4: Run Your Application to Generate Traces

Run any of the entry points to start sending traces:

```powershell
# Run prediction
python predict.py

# Or start the web service
python serve.py

# Or run integrated orchestrator
python integrated_orchestrator.py
```

The application will automatically send traces to Okahu at: `https://ingest.okahu.io`

## Step 5: Create Application in Okahu Portal

1. Login to **https://portal.okahu.co**
2. Click on **New Application**
3. Under the **Components** section, click **Browse Discovered Components**
4. You should see your workflow: **`qaops-multiagent-orchestrator`**
5. Select `qaops-multiagent-orchestrator` from the list
6. Click **Add Selection**
7. Click **Save** to finish

## Step 6: Verify Traces

1. Go to your Okahu dashboard
2. Select your newly created application
3. You should see traces for:
   - Agent method calls
   - LLM API calls (Gemini)
   - Message passing between agents
   - Tool invocations (JIRA, Jenkins, Grafana)

## What Gets Traced Automatically

Monocle automatically traces:
- ✅ All agent process/execute methods
- ✅ LLM API calls (google-generativeai)
- ✅ HTTP requests to external tools
- ✅ Message flow between agents
- ✅ Latency and performance metrics
- ✅ Token usage and costs

## Troubleshooting

### 1. Error Installing Monocle SDK

**Issue:** Cannot install `monocle_apptrace`

**Solution:**
```powershell
# Verify connectivity to Okahu's PyPI repository
nslookup okahu.jfrog.io
Test-NetConnection okahu.jfrog.io -Port 443
```

If blocked, contact your network/security team to allowlist `okahu.jfrog.io`.

### 2. Workflow Not Showing in Components List

**Issue:** `qaops-multiagent-orchestrator` doesn't appear in Browse Discovered Components

**Possible Causes:**

#### A. API Key Not Set Correctly
```powershell
# In PowerShell, check if key is set
$env:OKAHU_API_KEY

# Should output your API key, not blank
```

#### B. No Network Path to Okahu Ingestion Endpoint
```powershell
# Test connectivity
nslookup ingest.okahu.io
Test-NetConnection ingest.okahu.io -Port 443
```

If this fails, contact your network/security team to allowlist `ingest.okahu.io`.

#### C. Application Hasn't Run Yet
Make sure you've run at least one of the entry points (`predict.py`, `serve.py`, etc.) **AFTER** setting the API key.

### 3. Traces Not Appearing After Application Created

**Wait Time:** It may take 1-2 minutes for traces to appear in the dashboard.

**Verify:**
```powershell
# Run a test prediction
python predict.py
```

Then refresh the Okahu dashboard.

## Network Requirements

Ensure your network allows HTTPS (port 443) to:
- ✅ `okahu.jfrog.io` - For SDK installation
- ✅ `ingest.okahu.io` - For trace ingestion
- ✅ `portal.okahu.co` - For dashboard access

## Additional Resources

- **Okahu Portal:** https://portal.okahu.co
- **Okahu Documentation:** https://docs.okahu.ai/
- **Okahu Playground:** https://docs.okahu.ai/#explore-okahu-playground

## Quick Test Command

```powershell
# Full test sequence
$env:OKAHU_API_KEY = "your-key-here"
python predict.py
# Then check https://portal.okahu.co for traces
```

## Support

If issues persist:
1. Verify API key is correct
2. Check network connectivity
3. Review application logs for errors
4. Contact Okahu support through the portal

# Data for okahu quickstart

# Where to Add Okahu API Key

## Option 1: Environment Variable (Recommended)

```bash
# In your terminal
export OKAHU_API_KEY="okahu_your_api_key_here"
export MONOCLE_EXPORTER="okahu"

# Run your application
python predict.py '[ERROR] test FAILED'
```

## Option 2: .env File (Persistent)

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your key:
```bash
# Open in your editor
nano .env
# or
vim .env
# or
code .env
```

3. Update these lines:
```env
OKAHU_API_KEY=okahu_your_actual_key_here
MONOCLE_EXPORTER=okahu
```

4. Run your application (automatically loads .env):
```bash
python predict.py '[ERROR] test FAILED'
```

## Option 3: Docker Environment

```bash
docker run -e OKAHU_API_KEY="your-key" -e MONOCLE_EXPORTER="okahu" \
  -p 9696:9696 qaops-orchestrator
```

## Get Your Okahu API Key

1. Visit: https://app.okahu.ai/signup
2. Create account and verify email
3. Go to: **Settings** → **API Keys**
4. Click **Create New API Key**
5. Copy the key (starts with `okahu_`)

## Verify Setup

```bash
# Check if key is set
echo $OKAHU_API_KEY

# Should output: okahu_xxxxx...
```

## Test Tracing

```bash
# With Okahu export
export OKAHU_API_KEY="your-key"
export MONOCLE_EXPORTER="okahu"
python predict.py '[ERROR] test FAILED'

# View traces at: https://app.okahu.ai/traces
```

## File Locations

- **Environment variables**: Set in terminal or `.bashrc`/`.zshrc`
- **.env file**: `/path/to/multiagent-ops-orchestrator/.env`
- **Example file**: `.env.example` (template, don't edit directly)

# Okahu Integration - Next Steps

## 1. Sign Up for Okahu

Visit: https://app.okahu.ai/signup
- Create account with your email
- Verify email address
- Complete onboarding

## 2. Get API Key

1. Login to https://app.okahu.ai
2. Navigate to **Settings** → **API Keys**
3. Click **Create New API Key**
4. Copy the key (starts with `okahu_`)
5. Set environment variable:
   ```bash
   export OKAHU_API_KEY="okahu_your_key_here"
   ```

## 3. Install Okahu SDK

```bash
pip install monocle-observability
```

## 4. Update Integration Code

Replace `integrations/okahu_integration.py` with:

```python
from monocle import Monocle
from monocle.exporters import OkahuExporter
import os

# Initialize Monocle with Okahu
Monocle.init({
    'exporter': OkahuExporter(
        api_key=os.getenv('OKAHU_API_KEY'),
        endpoint='https://api.okahu.ai/v1/traces'
    ),
    'service_name': 'qaops-orchestrator',
    'environment': 'production'
})

def trace_agent(func):
    return Monocle.trace_agent(func)
```

## 5. Run Test Trace

```bash
# Set API key
export OKAHU_API_KEY="your_key"

# Run orchestrator
python integrated_orchestrator.py
```

## 6. View Traces in Okahu Dashboard

1. Go to https://app.okahu.ai/traces
2. Select **qaops-orchestrator** service
3. View traces for:
   - Agent invocations
   - CI log analysis
   - Remediation planning
   - Token usage
   - Latency metrics

## 7. Key Metrics to Monitor

### In Okahu Dashboard:
- **Traces**: Agent execution flow
- **Latency**: Response times per agent
- **Token Usage**: LLM API costs
- **Error Rate**: Failed agent calls
- **Throughput**: Requests per minute

### Dashboard Sections:
- **Overview**: System health
- **Traces**: Detailed execution logs
- **Metrics**: Performance graphs
- **Costs**: Token usage breakdown
- **Alerts**: Configure notifications

## 8. Set Up Alerts

1. Navigate to **Alerts** in Okahu
2. Create alert for:
   - High latency (>30s)
   - Error rate (>5%)
   - Token usage spike
3. Configure notification channels (email/Slack)

## 9. Verify Integration

Check these in Okahu:
- [ ] Service appears in dashboard
- [ ] Traces are being captured
- [ ] Agent names are visible
- [ ] Token counts are tracked
- [ ] Latency metrics show up

## 10. Troubleshooting

**No traces appearing?**
- Verify API key is correct
- Check `OKAHU_API_KEY` environment variable
- Ensure `monocle-observability` is installed
- Check network connectivity to api.okahu.ai

**Traces incomplete?**
- Add `@trace_agent` decorator to all agent methods
- Ensure Monocle.init() is called before agent execution

**High costs?**
- Review token usage in Okahu dashboard
- Optimize prompts to reduce tokens
- Set up cost alerts

## Support

- Documentation: https://docs.okahu.ai
- Support: support@okahu.ai
- Community: https://github.com/okahu-ai

# Okahu Quick Start Guide

**Goal:** Get traces from your multi-agent orchestrator into Okahu in 5 minutes.

## 1️⃣ Get Okahu API Key (2 min)

1. Visit: **https://portal.okahu.co/en/apps/**
2. Login with **GitHub** or **LinkedIn**
3. Go to **Settings** → Click **Generate API Key**
4. Copy the key

## 2️⃣ Set Environment Variable (30 sec)

**Windows PowerShell:**
```powershell
$env:OKAHU_API_KEY = "your-api-key-here"
```

**Linux/Mac:**
```bash
export OKAHU_API_KEY="your-api-key-here"
```

## 3️⃣ Verify Setup (30 sec)

```powershell
python verify_okahu.py
```

You should see all ✅ checks pass.

## 4️⃣ Run Application to Generate Traces (1 min)

```powershell
# Option 1: Run prediction
python predict.py

# Option 2: Start web service
python serve.py
```

## 5️⃣ Create Application in Okahu Portal (1 min)

1. Go to **https://portal.okahu.co**
2. Click **New Application**
3. Click **Browse Discovered Components**
4. Find and select: **`qaops-multiagent-orchestrator`**
5. Click **Add Selection** → **Save**

## 6️⃣ View Traces

Open your application in Okahu dashboard and explore:
- Agent execution traces
- LLM API calls
- Performance metrics
- Token usage

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Workflow not in component list | Wait 1-2 min after running app, then refresh |
| API key error | Check: `echo $env:OKAHU_API_KEY` (Windows) |
| Network errors | Check firewall allows `ingest.okahu.io:443` |

---

## What Gets Traced Automatically

✅ Agent method calls  
✅ LLM API requests (Gemini)  
✅ Tool invocations (JIRA, Jenkins, Grafana)  
✅ Message passing between agents  
✅ Latency & performance  
✅ Token usage & costs  

**No code changes needed** - tracing is already enabled in:
- `predict.py`
- `serve.py`
- `integrated_orchestrator.py`

---

## Reference Documents

- **Full Setup Guide:** [OKAHU_APPLICATION_SETUP.md](OKAHU_APPLICATION_SETUP.md)
- **API Key Details:** [OKAHU_API_KEY_SETUP.md](OKAHU_API_KEY_SETUP.md)
- **Monocle Info:** [MONOCLE_SETUP.md](MONOCLE_SETUP.md)

# Okahu Tracing Troubleshooting

## 🚨 Issue: "App does not exist or has no workflows associated"

This error in Okahu portal means traces are not reaching the Okahu servers.

## 🔍 Root Cause Analysis

### DNS Resolution Failure

```powershell
PS> nslookup ingest.okahu.io
*** BAWFDC01.fiery.internal can't find ingest.okahu.io: Non-existent domain
```

**Issue**: The corporate network DNS cannot resolve `ingest.okahu.io`

### Network Connectivity Test Results

| Endpoint | Status | Purpose |
|----------|--------|---------|
| ✅ `okahu.io` | Reachable | Base domain |
| ✅ `portal.okahu.co` | Reachable | Dashboard/UI |
| ✅ `okahu.jfrog.io` | Reachable | SDK downloads |
| ❌ `ingest.okahu.io` | **BLOCKED** | **Trace ingestion** |

## 🛠️ Solutions

### Option 1: Request Network Team to Allowlist (Recommended)

**Action Required**: Contact your IT/Network/Security team to allowlist:

```
Domain: ingest.okahu.io
Port: 443 (HTTPS)
Direction: Outbound
Purpose: Application telemetry/observability (Okahu tracing)
```

**Email Template:**
```
Subject: Network Access Request - Okahu Telemetry Endpoint

Hi IT Team,

I need outbound HTTPS access to the following endpoint for application observability:

Domain: ingest.okahu.io
Port: 443 (HTTPS)
Protocol: HTTPS/TLS
Purpose: Send application traces to Okahu SaaS platform for monitoring
Security: All data encrypted via TLS 1.2+

This is required for our QA/DevOps automation project to send telemetry data.

Documentation: https://docs.okahu.ai/

Please allowlist this domain in the corporate firewall.

Thanks,
[Your Name]
```

### Option 2: Alternative Trace Exporters (Workaround)

Until the network issue is resolved, use these alternatives:

#### A. File-based Tracing (Local Storage)

Already configured in your `.env`:

```env
MONOCLE_EXPORTER=file
MONOCLE_OUTPUT_DIR=./traces
```

**To Use:**
1. Change `.env` back to `MONOCLE_EXPORTER=file`
2. Run your application
3. Traces saved to `./traces/` directory
4. Manually review trace files

**Pros**: Works offline, no network needed  
**Cons**: Manual review, no dashboard visualization

#### B. AWS S3 Exporter (If AWS available)

```env
MONOCLE_EXPORTER=s3
AWS_S3_BUCKET=your-traces-bucket
AWS_REGION=us-east-1
```

**Pros**: Cloud storage, queryable with Athena  
**Cons**: Requires AWS setup and costs

#### C. OpenTelemetry Collector (Advanced)

Set up a local OTEL collector that forwards to Okahu:

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

exporters:
  otlphttp:
    endpoint: https://ingest.okahu.io/v1/traces
    headers:
      api-key: ${OKAHU_API_KEY}

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlphttp]
```

### Option 3: Use VPN/Proxy (Temporary)

If your organization has a VPN that routes through different DNS:
1. Connect to VPN
2. Test: `nslookup ingest.okahu.io`
3. If resolves, run application

### Option 4: Alternative Observability Platform

If Okahu is blocked long-term, consider alternatives:

- **Langfuse** - `https://langfuse.com`
- **Langsmith** - `https://www.langchain.com/langsmith`
- **Helicone** - `https://www.helicone.ai`
- **Prometheus + Grafana** - Self-hosted

## 🧪 Verify Network Access

### Test DNS Resolution

```powershell
# Test with corporate DNS
nslookup ingest.okahu.io

# Expected if working:
# Non-authoritative answer:
# Name:    ingest.okahu.io
# Address:  [IP address]
```

### Test HTTPS Connectivity

```powershell
Test-NetConnection ingest.okahu.io -Port 443

# Expected if working:
# TcpTestSucceeded : True
```

### Test with cURL

```powershell
curl -I https://ingest.okahu.io/healthz

# Expected if working:
# HTTP/2 200
```

## 📊 Current Workaround: File-based Traces

While waiting for network access, use file-based tracing:

### 1. Update `.env`

```env
MONOCLE_EXPORTER=file
MONOCLE_OUTPUT_DIR=./traces
```

### 2. Run Application

```powershell
python predict.py "[ERROR] test failed"
```

### 3. View Traces

```powershell
# List trace files
Get-ChildItem ./traces

# View latest trace
Get-Content ./traces/*.json -Tail 50 | ConvertFrom-Json
```

### 4. Manual Analysis

Review JSON trace files for:
- Agent execution times
- LLM token usage
- Error patterns
- Call graphs

## 🔄 Next Steps

1. **Short-term** (Today):
   - Use file-based exporter
   - Submit network access request

2. **Medium-term** (This week):
   - Follow up with IT team
   - Test connectivity once allowlisted

3. **Long-term** (After access granted):
   - Switch back to `MONOCLE_EXPORTER=okahu`
   - Create application in Okahu portal
   - Set up dashboards & alerts

## 📝 How to Switch Back to Okahu After Network Fix

Once `ingest.okahu.io` is accessible:

```powershell
# 1. Test connectivity
Test-NetConnection ingest.okahu.io -Port 443

# 2. Update .env
# Change: MONOCLE_EXPORTER=okahu

# 3. Restart application
python serve.py

# 4. Verify traces reach Okahu
# Visit: https://portal.okahu.co/en/apps/
# Browse Discovered Components → Should see your workflow
```

## 🆘 Additional Help

- **Okahu Support**: Contact through https://portal.okahu.co
- **Documentation**: https://docs.okahu.ai/
- **Network Team**: Your internal IT support

## 📎 Attachments for IT Team

If your IT team needs justification:

1. **What is Okahu?**
   - SaaS observability platform for AI/ML applications
   - Provides monitoring, tracing, and cost tracking
   - Industry-standard OpenTelemetry protocol

2. **Security**
   - All data encrypted via TLS 1.3
   - API key authentication
   - No inbound connections required

3. **Alternative**
   - If blocking is permanent, we can self-host observability
   - This would require additional infrastructure costs

---

**Status**: Network access to `ingest.okahu.io` is currently BLOCKED  
**Workaround**: Using file-based tracing (`MONOCLE_EXPORTER=file`)  
**Action Required**: IT team to allowlist `ingest.okahu.io:443`

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
        "model": "gemini-2.5-flash-lite",
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

# Fix: App Does Not Exist in Okahu

## Problem
Error: `App 'cicd_agent_o4d1k6' does not exist or has no workflows associated.`

## Solution: Create App in Okahu

### Step 1: Run Your Application First
```bash
source .venv/bin/activate
export MONOCLE_EXPORTER=okahu
python predict.py '[ERROR] test_login FAILED'
```

This sends traces to Okahu and creates a "discovered component".

### Step 2: Create App in Okahu Portal

1. **Login to Okahu**
   - Visit: https://app.okahu.ai

2. **Go to Discovered Components**
   - Navigate to: **Discover** → **Components**
   - Or: https://app.okahu.ai/discover/components

3. **Find Your Workflow**
   - Look for: `qaops-multiagent-orchestrator`
   - This is the workflow_name from `setup_monocle_telemetry()`

4. **Create App**
   - Click on `qaops-multiagent-orchestrator`
   - Click **"Create App"** or **"Add to App"**
   - Give it a name: `QAOps Orchestrator`
   - Click **Save**

5. **View Traces**
   - Go to: **Apps** → **QAOps Orchestrator**
   - Click **Traces** tab
   - You should see your agent execution traces

## Alternative: Change Workflow Name

If you want a specific app name, update the workflow name:

### In predict.py:
```python
setup_monocle_telemetry(workflow_name="qaops-orchestrator")
```

### In serve.py:
```python
setup_monocle_telemetry(workflow_name="qaops-orchestrator")
```

### In integrated_orchestrator.py:
```python
setup_monocle_telemetry(workflow_name="qaops-orchestrator")
```

Then run again and create the app in Okahu.

## Verify Setup

```bash
# 1. Set exporter to Okahu
export MONOCLE_EXPORTER=okahu

# 2. Run prediction
python predict.py '[ERROR] test FAILED'

# 3. Check Okahu
# Visit: https://app.okahu.ai/discover/components
# Look for: qaops-multiagent-orchestrator

# 4. Create app from discovered component

# 5. View traces
# Visit: https://app.okahu.ai/apps
```

## Expected Result

After creating the app, you should see:
- ✅ Agent execution traces
- ✅ Latency metrics
- ✅ Token usage (if using LLM)
- ✅ Error rates
- ✅ Execution flow diagram

