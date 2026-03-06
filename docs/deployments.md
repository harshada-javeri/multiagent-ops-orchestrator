# Vertex AI Agent Engine Deployment

## Steps

1. Build Docker image:
   ```bash
   docker build -t qaops-orchestrator .
   ```
2. Push to Artifact Registry:
   ```bash
   docker tag qaops-orchestrator <region>-docker.pkg.dev/<project>/<repo>/qaops-orchestrator
   docker push <region>-docker.pkg.dev/<project>/<repo>/qaops-orchestrator
   ```
3. Deploy on Vertex AI Agent Engine:
   - Set environment variables from `.env`
   - Configure endpoints for Jenkins, JIRA, Grafana
   - Enable tracing and metrics

# Deployment Guide

## Local Development
```bash
python serve.py
# Service runs on http://localhost:9696
```

## Docker Deployment
```bash
# Build image
docker build -t qaops-orchestrator .

# Run container
docker run -it -p 9696:9696 qaops-orchestrator

# Test deployment
curl http://localhost:9696/health
```

## Production Considerations
- Set environment variables for API keys
- Configure logging levels
- Monitor memory usage for large log files
- Implement rate limiting for API endpoints

## API Endpoints
- `GET /health` - Health check
- `POST /predict` - Analyze CI logs
- `GET /` - API documentation