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