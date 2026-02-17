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