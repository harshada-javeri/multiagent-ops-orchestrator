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
