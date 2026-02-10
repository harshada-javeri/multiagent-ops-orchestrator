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