# Design Document: System Architecture Diagram

## Overview

This design specifies the creation of a comprehensive system architecture diagram for the Multi-Agent QAOps Orchestrator. The diagram will be implemented using Mermaid syntax to ensure version control compatibility, easy maintenance, and broad platform support (GitHub, GitLab, documentation sites).

The diagram will visualize five key architectural aspects:
1. LLM integration with Google Gemini
2. Three-agent workflow orchestration
3. Observability through Monocle/Okahu
4. System components and external integrations
5. End-to-end data flow

The deliverable will be a Markdown file containing the Mermaid diagram with accompanying documentation, suitable for inclusion in the project's README or docs folder.

## Architecture

### Diagram Structure

The architecture diagram will use a **layered approach** with the following structure:

```
┌─────────────────────────────────────────────────────────┐
│  External Systems Layer (CI/CD, JIRA, Grafana)         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  API Layer (Flask Service: /health, /predict)          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Agent Orchestration Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Diagnostics  │→ │ RootCause    │→ │ ActionPlanner│ │
│  │ Agent        │  │ Analyzer     │  │ Agent        │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Integration Layer (LLM, Memory Bank, Tracing)         │
└─────────────────────────────────────────────────────────┘
```

### Mermaid Diagram Type Selection

We will use **Mermaid flowchart** (graph TD) for the following reasons:
- Supports complex node relationships and data flow
- Allows subgraphs for logical grouping (agents, integrations)
- Provides flexible styling options
- Widely supported across platforms
- Clear directional flow representation

Alternative considered: C4 diagrams (rejected due to limited Mermaid C4 support and complexity for this use case)

## Components and Interfaces

### 1. Diagram File Structure

**File:** `docs/architecture-diagram.md`

**Content Structure:**
```markdown
# System Architecture

## Overview
[Brief description of the system]

## Architecture Diagram
[Mermaid diagram code block]

## Component Descriptions
[Detailed explanations of each component]

## Data Flow
[Step-by-step data flow explanation]

## Running the System
[Instructions for running agents and viewing traces]
```

### 2. Mermaid Diagram Components

#### Node Types and Styling

**External Systems** (Rounded rectangles with distinct color):
- Jenkins CI/CD
- JIRA Ticketing
- Grafana Metrics

**API Layer** (Rectangle):
- Flask Service with endpoints

**Agent Nodes** (Rounded rectangles with agent-specific styling):
- TestDiagnosticsAgent
- RootCauseAnalyzerAgent
- ActionPlannerAgent

**Integration Components** (Cylinders for data stores, clouds for external services):
- Google Gemini LLM (cloud)
- Memory Bank (cylinder)
- Monocle/Okahu Tracing (cloud)

**Configuration** (Dotted rectangles):
- Environment Variables
- API Keys

#### Subgraph Organization

**Subgraph 1: Agent Orchestration**
- Contains all three agents
- Shows ADK message-passing connections
- Highlights sequential flow

**Subgraph 2: Observability**
- Monocle telemetry setup
- OpenTelemetry spans
- Okahu portal connection

**Subgraph 3: LLM Integration**
- Gemini API connection
- Model specification
- Fallback mechanism

### 3. Data Flow Arrows

**Arrow Types:**
- Solid arrows: Primary data flow
- Dashed arrows: Configuration/setup
- Thick arrows: High-volume data paths
- Dotted arrows: Fallback/alternative paths

**Labels on Arrows:**
- Data type being passed (e.g., "CI Logs", "Failed Tests", "Analysis Results")
- Protocol/method (e.g., "HTTP POST", "ADK Message")

## Data Models

### Diagram Node Definitions

```typescript
interface DiagramNode {
  id: string;              // Unique identifier for Mermaid
  label: string;           // Display text
  type: NodeType;          // Shape and styling
  description: string;     // For documentation section
}

enum NodeType {
  EXTERNAL_SYSTEM,
  API_ENDPOINT,
  AGENT,
  INTEGRATION,
  DATA_STORE,
  CONFIGURATION
}
```

### Connection Definitions

```typescript
interface Connection {
  from: string;            // Source node ID
  to: string;              // Target node ID
  label: string;           // Data/message description
  style: ConnectionStyle;  // Visual representation
}

enum ConnectionStyle {
  PRIMARY_FLOW,           // Solid arrow
  CONFIGURATION,          // Dashed arrow
  HIGH_VOLUME,           // Thick arrow
  FALLBACK               // Dotted arrow
}
```

### Workflow Stages

```typescript
interface WorkflowStage {
  agent: string;
  input: string;
  processing: string;
  output: string;
  tracingPoint: boolean;
}

const workflow: WorkflowStage[] = [
  {
    agent: "TestDiagnosticsAgent",
    input: "Raw CI Logs",
    processing: "Parse logs, extract failed tests, identify patterns",
    output: "Failed tests list with error patterns",
    tracingPoint: true
  },
  {
    agent: "RootCauseAnalyzerAgent",
    input: "Failed tests with patterns",
    processing: "LLM analysis via Gemini API",
    output: "Root cause hypotheses",
    tracingPoint: true
  },
  {
    agent: "ActionPlannerAgent",
    input: "Root cause analysis",
    processing: "Generate remediation plan",
    output: "Action plan + JIRA ticket",
    tracingPoint: true
  }
];
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Required System Components Present

*For any* generated architecture diagram, the diagram SHALL contain all required system components including: TestDiagnosticsAgent, RootCauseAnalyzerAgent, ActionPlannerAgent, Google Gemini API (models/gemini-1.5-flash), Jenkins CI/CD, JIRA, Grafana, Memory_Bank, Flask service with /health and /predict endpoints, Monocle telemetry, Okahu portal, and Docker deployment.

**Validates: Requirements 1.1, 1.2, 2.1, 3.1, 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 2: Complete Agent Workflow Representation

*For any* generated architecture diagram, the three agents SHALL be connected in sequential order (TestDiagnosticsAgent → RootCauseAnalyzerAgent → ActionPlannerAgent) with each agent having a description of its primary responsibility and data transformation labels on connecting edges.

**Validates: Requirements 2.2, 2.3, 2.5**

### Property 3: LLM Integration Details

*For any* generated architecture diagram, the RootCauseAnalyzerAgent SHALL have a connection to Google Gemini API with labels indicating the model (gemini-1.5-flash), environment variable configuration (GEMINI_API_KEY, GOOGLE_API_KEY), usage purpose ("intelligent root cause analysis"), and a fallback path to mock analysis.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**

### Property 4: End-to-End Data Flow

*For any* generated architecture diagram, there SHALL be a complete data flow path from raw CI logs through TestDiagnosticsAgent (outputting failed tests), to RootCauseAnalyzerAgent (outputting LLM analysis), to ActionPlannerAgent (outputting remediation plan and JIRA ticket), with each transformation labeled on the connecting edges.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 5: Observability Tracing Integration

*For any* generated architecture diagram, the diagram SHALL show Monocle telemetry integration with setup_monocle_telemetry() references, workflow names ("qaops-multiagent-orchestrator", "predict", "cicd-workflow"), OpenTelemetry spans, trace data flow to Okahu portal with API key configuration, and tracing indicators at all agent workflow steps.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 5.6**

### Property 6: ADK Message-Passing Protocol

*For any* generated architecture diagram, the connections between agents SHALL indicate the ADK framework message-passing protocol being used for inter-agent communication.

**Validates: Requirements 2.4**

### Property 7: Configuration Sources Visibility

*For any* generated architecture diagram, the diagram SHALL show configuration sources including environment variables and their usage points throughout the system.

**Validates: Requirements 4.6**

### Property 8: Valid Mermaid Syntax in Markdown

*For any* generated documentation file, the file SHALL be valid Markdown containing a Mermaid code block (```mermaid) with syntactically correct Mermaid flowchart syntax, and SHALL use component names consistent with the actual codebase.

**Validates: Requirements 6.1, 6.2, 6.6**

### Property 9: Documentation Structure Completeness

*For any* generated documentation file, the file SHALL include a title, introduction section, the Mermaid diagram, component descriptions section, data flow explanation section, and operational instructions for running agents and viewing traces.

**Validates: Requirements 7.2, 7.3, 8.1, 8.2, 8.3**

### Property 10: Legend or Key Included

*For any* generated architecture diagram documentation, the file SHALL include a legend or key section explaining the symbols, shapes, and arrow types used in the diagram.

**Validates: Requirements 6.4**

### Property 11: Operational Instructions Completeness

*For any* generated documentation file, the operational instructions SHALL include steps to run agents, reference to setup_monocle_telemetry() calls, workflow name ("multiagent-orchestrator"), instructions to access portal.okahu.ai, and prerequisites for Okahu API key setup.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

## Error Handling

### Mermaid Syntax Errors

**Error Condition:** Invalid Mermaid syntax that prevents rendering

**Handling Strategy:**
- Validate Mermaid syntax before finalizing the diagram
- Use Mermaid CLI or online validator during development
- Include syntax validation as part of the testing strategy
- Provide clear error messages if syntax issues are detected

### Missing Component References

**Error Condition:** Required system components are not represented in the diagram

**Handling Strategy:**
- Create a checklist of all required components from requirements
- Validate against checklist before considering diagram complete
- Use automated tests to verify component presence
- Document any intentionally omitted components with rationale

### Inconsistent Naming

**Error Condition:** Component names in diagram don't match codebase

**Handling Strategy:**
- Extract actual component names from codebase (agents/, serve.py, etc.)
- Create a naming reference document
- Validate diagram names against codebase names
- Update diagram to use canonical names from code

### Rendering Issues

**Error Condition:** Diagram doesn't render properly on target platforms

**Handling Strategy:**
- Test rendering on GitHub, GitLab, and common documentation platforms
- Use widely-supported Mermaid features (avoid experimental syntax)
- Provide fallback static image if Mermaid rendering fails
- Document known rendering limitations

## Testing Strategy

### Dual Testing Approach

This feature will use both unit tests and property-based tests to ensure comprehensive validation:

**Unit Tests** will focus on:
- Specific examples of valid Mermaid syntax
- Edge cases like empty diagrams or minimal diagrams
- File creation and location verification
- Markdown formatting correctness

**Property-Based Tests** will focus on:
- Universal properties that hold for all valid diagrams
- Component presence across different diagram variations
- Data flow completeness regardless of styling choices
- Syntax validity for randomly generated diagram variations

### Property-Based Testing Configuration

**Library:** Python with `hypothesis` for property-based testing

**Test Configuration:**
- Minimum 100 iterations per property test
- Each property test references its design document property
- Tag format: **Feature: system-architecture-diagram, Property {number}: {property_text}**

### Test Categories

#### 1. Content Validation Tests

**Unit Tests:**
- Test that a minimal valid diagram contains required sections
- Test that specific component names appear in expected format
- Test edge case: diagram with only agents (missing integrations)
- Test edge case: diagram with only integrations (missing agents)

**Property Tests:**
- Property 1: Required System Components Present
- Property 2: Complete Agent Workflow Representation
- Property 3: LLM Integration Details
- Property 4: End-to-End Data Flow
- Property 5: Observability Tracing Integration
- Property 6: ADK Message-Passing Protocol
- Property 7: Configuration Sources Visibility

#### 2. Format Validation Tests

**Unit Tests:**
- Test that file is valid Markdown
- Test that Mermaid code block is properly fenced
- Test that file has .md extension
- Test specific Mermaid syntax patterns (node definitions, edges)

**Property Tests:**
- Property 8: Valid Mermaid Syntax in Markdown

#### 3. Documentation Structure Tests

**Unit Tests:**
- Test that file contains a title (H1 heading)
- Test that introduction section exists
- Test that component descriptions section exists
- Test that file is created in docs/ directory

**Property Tests:**
- Property 9: Documentation Structure Completeness
- Property 10: Legend or Key Included
- Property 11: Operational Instructions Completeness

#### 4. Integration Tests

**Unit Tests:**
- Test that diagram file can be read and parsed
- Test that Mermaid syntax can be validated by Mermaid CLI
- Test that file renders correctly in Markdown preview
- Test that all referenced components exist in codebase

### Testing Tools

**Mermaid Validation:**
- Mermaid CLI for syntax validation
- Online Mermaid Live Editor for visual verification
- Automated syntax checking in CI/CD pipeline

**Markdown Validation:**
- Markdown linters (markdownlint)
- Markdown parsers to verify structure
- Link checkers for any references

**Content Validation:**
- Regular expressions for component name matching
- Graph parsing libraries to validate node/edge structure
- String search for required keywords and phrases

### Test Execution Strategy

1. **Development Phase:**
   - Run unit tests after each diagram iteration
   - Manually verify rendering in GitHub preview
   - Use Mermaid Live Editor for syntax validation

2. **Pre-Commit:**
   - Run all unit tests
   - Run property-based tests (100 iterations each)
   - Validate Mermaid syntax with CLI

3. **CI/CD Pipeline:**
   - Full test suite execution
   - Render diagram and capture screenshot
   - Validate against codebase component names
   - Check for documentation completeness

### Success Criteria

The diagram implementation is considered complete when:
- All unit tests pass
- All property-based tests pass (100 iterations each)
- Diagram renders correctly on GitHub
- All required components are present and connected
- Documentation is complete with explanations
- Operational instructions are clear and complete
- Mermaid syntax is valid
- Component names match codebase
