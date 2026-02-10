# Integration Guide: Okahu + AWS AgentCore

## Overview
This project integrates with:
- **AWS AgentCore**: Production agent runtime and gateway
- **Okahu**: AI observability and tracing

## Quick Setup

### 1. Install Dependencies
```bash
pip install boto3 awscli
```

### 2. Configure Environment
```bash
export OKAHU_API_KEY="your-okahu-key"
export AGENTCORE_RUNTIME_ID="your-runtime-id"
export AWS_REGION="us-east-1"
```

### 3. Run Integrated Orchestrator
```bash
python integrated_orchestrator.py
```

## AgentCore Deployment

### Deploy with Terraform
```bash
cd deployment
terraform init
terraform apply -var="docker_image_uri=<your-ecr-uri>"
```

### Deploy with Docker
```bash
docker build -t qaops-agentcore .
docker push <ecr-uri>/qaops-agentcore:latest
```

## Okahu Observability

Traces are automatically captured for:
- Agent invocations
- CI log analysis
- Remediation planning

View traces at: https://app.okahu.ai

## Architecture

```
CI Logs → Integrated Orchestrator → AgentCore Runtime
                ↓
         Okahu Tracing
```

## Files Added
- `integrations/agentcore_integration.py` - AWS AgentCore client
- `integrations/okahu_integration.py` - Okahu tracer
- `integrated_orchestrator.py` - Combined orchestrator
- `deployment/agentcore.tf` - Infrastructure as code