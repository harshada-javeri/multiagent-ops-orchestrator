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
