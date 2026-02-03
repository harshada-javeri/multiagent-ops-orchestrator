# FAQ - Multi-Agent QAOps Orchestrator

## General Questions

**Q: What does this system do?**
A: Automatically analyzes CI/CD failure logs using AI agents to identify root causes and generate remediation plans, reducing manual triage time by 60-80%.

**Q: Who should use this?**
A: DevOps teams, QA engineers, and development teams managing CI/CD pipelines with frequent test failures.

## Technical Questions

**Q: How do I run the system locally?**
A: Install dependencies (`pip install -r requirements.txt`), train agents (`python train.py`), then start the web service (`python serve.py`).

**Q: What API endpoints are available?**
A: `GET /health` for health checks, `POST /predict` for log analysis, and `GET /` for API documentation.

**Q: Can I deploy this in production?**
A: Yes, use Docker: `docker build -t qaops -f DockerFile .` then `docker run -p 9696:9696 qaops`.

**Q: What if I don't have a Gemini API key?**
A: The system works with mock analysis for testing. For production, obtain a Google Gemini API key and set `GEMINI_API_KEY` environment variable.

**Q: How accurate is the analysis?**
A: Current system achieves 87% classification accuracy with 75% MTTR reduction in testing scenarios.