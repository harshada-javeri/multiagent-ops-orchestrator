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
