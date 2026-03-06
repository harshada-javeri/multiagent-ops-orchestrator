# Multi-Agent QAOps Orchestrator

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

Automate CI/CD failure triage and remediation using a multi-agent system. This project reduces Mean Time To Recovery (MTTR) through intelligent log parsing, root-cause analysis, and actionable remediation planning.

---

## Architecture

### System Overview

The QAOps Orchestrator is built as a modular, multi-agent system. Each agent is responsible for a specific stage in the CI/CD failure analysis pipeline. The architecture is designed for extensibility, observability, and integration with external tools.

**Key Components:**
- **Entry Points:**  
  - [`main_orchestrator.py`](main_orchestrator.py): Main orchestration pipeline  
  - [`predict.py`](predict.py): CLI prediction script  
  - [`serve.py`](serve.py): Flask web service for API access  
  - [`integrated_orchestrator.py`](integrated_orchestrator.py): Integrated workflow with observability

- **Agents:**  
  - [`agents/test_diagnostics_agent.py`](agents/test_diagnostics_agent.py): Parses CI logs, extracts failed tests and error patterns  
  - [`agents/root_cause_agent.py`](agents/root_cause_agent.py): Performs root-cause analysis using LLM and memory  
  - [`agents/action_planner_agent.py`](agents/action_planner_agent.py): Generates remediation plans and creates JIRA tickets

- **Tools:**  
  - [`tools/jenkins_tool.py`](tools/jenkins_tool.py): Fetches CI logs from Jenkins  
  - [`tools/jira_tool.py`](tools/jira_tool.py): Handles JIRA ticket creation  
  - [`tools/grafana_tool.py`](tools/grafana_tool.py): Fetches metrics from Grafana

- **Utilities:**  
  - [`utils/logger.py`](utils/logger.py): Structured logging with correlation IDs  
  - [`utils/memory_handler.py`](utils/memory_handler.py): Persistent memory for recurring patterns

- **Observability:**  
  - [`observability.py`](observability.py): Initializes tracing and telemetry  
  - Tracing is enabled in all entry points and spans agent execution, LLM calls, and tool invocations.

**Data Flow:**
1. CI logs are ingested (from Jenkins or as input).
2. `TestDiagnosticsAgent` parses logs and extracts failure signals.
3. `RootCauseAnalyzerAgent` analyzes failures, queries memory, and uses LLM for hypotheses.
4. `ActionPlannerAgent` generates remediation steps and creates JIRA tickets.
5. Results are returned as structured output and traces are sent to Okahu.

---

## Repository Structure

```
multiagent-ops-orchestrator/
├── agents/                    # Agent implementations
│   ├── __init__.py
│   ├── test_diagnostics_agent.py
│   ├── root_cause_agent.py
│   └── action_planner_agent.py
├── tools/                     # Tool integrations
│   ├── __init__.py
│   ├── jenkins_tool.py
│   ├── jira_tool.py
│   └── grafana_tool.py
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── logger.py
│   └── memory_handler.py
├── tests/                     # Test suite
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_workspace.py
├── notebooks/                 # Demos and exploration
│   ├── demo.ipynb
│   └── kaggle_capstone_demo.ipynb
├── data/                      # Sample data
│   └── sample_logs/
│       └── jenkins_failure.log
├── docs/                      # Documentation
│   ├── architecture.md
│   ├── deployment.md
│   └── deployments.md
├── main_orchestrator.py       # Main orchestration entry point
├── predict.py                 # CLI prediction script
├── serve.py                   # Flask web service
├── integrated_orchestrator.py # Integrated workflow with observability
├── requirements.txt           # Python dependencies
├── DockerFile                 # Container definition
├── docker-compose.yml         # Docker orchestration
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore rules
├── memory_bank.json           # Persistent memory
├── observability.py           # Telemetry setup
└── README.md                  # This file
```

---

## Agents and Workflow

### 1. TestDiagnosticsAgent
- **File:** [`agents/test_diagnostics_agent.py`](agents/test_diagnostics_agent.py)
- **Role:** Parses CI logs, extracts failed tests, error patterns, and metadata.
- **Key Method:**  
  ```python
  process(logs: str) -> Message
  # Returns: {"failed_tests": [...], "error_categories": [...], "summary": "..."}
  ```

### 2. RootCauseAnalyzerAgent
- **File:** [`agents/root_cause_agent.py`](agents/root_cause_agent.py)
- **Role:** Performs root-cause analysis using LLM and memory bank.
- **Key Method:**  
  ```python
  process(diagnostics: Message) -> Message
  # Returns: {"analysis": "...", "confidence": 0.85, "root_causes": [...]}
  ```

### 3. ActionPlannerAgent
- **File:** [`agents/action_planner_agent.py`](agents/action_planner_agent.py)
- **Role:** Generates remediation plans and creates JIRA tickets.
- **Key Method:**  
  ```python
  process(analysis: Message) -> Message
  # Returns: {"plan": "...", "ticket_url": "...", "priority": "HIGH"}
  ```

**Workflow:**  
Agents are orchestrated in sequence. Each agent receives a `Message` object, processes it, and passes the result to the next agent. The final output includes failed tests, analysis, remediation plan, ticket URL, and confidence score.

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/harshada-javeri/multiagent-ops-orchestrator.git
cd multiagent-ops-orchestrator
```

### 2. Create a Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and edit as needed:
```bash
cp .env.example .env
```
Set required variables in `.env` (see `.env.example` for all options):
- `GOOGLE_API_KEY`
- `JIRA_URL`, `JIRA_USER`, `JIRA_TOKEN`
- `JENKINS_URL`
- `GRAFANA_URL` (optional)

### 5. Train Agents

```bash
python train.py
```

### 6. Run the Orchestrator

**Option A: CLI Prediction**
```bash
python predict.py '[ERROR] test_login FAILED'
```

**Option B: Web Service**
```bash
python serve.py
```

**Option C: Main Orchestrator**
```bash
python main_orchestrator.py
```

---

## Usage

### Basic Example

```python
from tools.jenkins_tool import fetch_ci_logs
from main_orchestrator import run_qaops_pipeline

logs = fetch_ci_logs()
result = run_qaops_pipeline(logs)

print(f"Failed Tests: {result.content['failed_tests']}")
print(f"Analysis: {result.content['analysis']}")
print(f"Remediation Plan: {result.content['plan']}")
print(f"JIRA Ticket: {result.content['ticket']}")
```

### Sample Output

```json
{
  "failed_tests": ["test_login_timeout", "test_checkout_flaky"],
  "error_categories": ["timeout", "race_condition"],
  "analysis": "Login timeout due to database query performance degradation. Checkout test exhibits race condition in payment mock.",
  "root_causes": [
    "Database index missing on user_sessions table",
    "Non-deterministic mock payment response timing"
  ],
  "plan": [
    "Action 1: Add database index on user_sessions.created_at",
    "Action 2: Increase payment mock response delay to 100ms",
    "Action 3: Increase login timeout to 30s (temporary fix)"
  ],
  "ticket_url": "https://jira.company.com/browse/QA-1234",
  "priority": "HIGH"
}
```

---

## Observability & Tracing

- Tracing is enabled in all entry points (`predict.py`, `serve.py`, `integrated_orchestrator.py`).
- Telemetry is initialized via [`observability.py`](observability.py) and sends traces to Okahu.
- To view traces:
  1. Set `OKAHU_API_KEY` in your environment.
  2. Run the application.
  3. Visit [Okahu Portal](https://portal.okahu.co/en/apps/) and browse discovered components.

---

## Testing

Run the test suite to validate agent logic and tool integrations:

```bash
pytest tests/ -v
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Virtual environment not activating | Ensure Python is in PATH; use full path: `python3 -m venv venv` |
| `GOOGLE_API_KEY` not recognized | Set in `.env` or export: `export GOOGLE_API_KEY="..."` |
| JIRA authentication fails | Verify token scope includes "issue:create"; test with JIRA CLI |
| Docker build fails | Ensure Docker daemon is running; check `requirements.txt` for version conflicts |
| Memory bank errors | Ensure `memory_bank.json` is writable; check directory permissions |
| Tests fail with import errors | Run from project root: `cd multiagent-ops-orchestrator && pytest` |

---

## License

This project is licensed under the MIT License — see LICENSE file for details.

---

## Support & Contact

- **Issues:** Open a GitHub issue for bugs or feature requests
- **Questions:** Check the [Discussions](https://github.com/harshada-javeri/multiagent-ops-orchestrator/discussions) tab
- **Email:** harshada.javeri@gmail.com

---