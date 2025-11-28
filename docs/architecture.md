# Architecture Overview

```mermaid
sequenceDiagram
    participant Jenkins
    participant TestDiagnosticsAgent
    participant RootCauseAnalyzerAgent
    participant ActionPlannerAgent
    participant JIRA

    Jenkins->>TestDiagnosticsAgent: CI logs
    TestDiagnosticsAgent->>RootCauseAnalyzerAgent: failed_tests
    RootCauseAnalyzerAgent->>ActionPlannerAgent: analysis
    ActionPlannerAgent->>JIRA: create ticket
    ActionPlannerAgent->>LoggerAgent: plan, ticket
```