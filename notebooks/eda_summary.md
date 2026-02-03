# EDA and Feature Engineering for QAOps

## Dataset Overview
- **Source**: CI/CD failure logs from Jenkins, GitHub Actions
- **Format**: Text logs with structured error patterns
- **Size**: 10KB - 5MB per log file
- **Target**: Failure classification and remediation planning

## Key Features Extracted
1. **Error Patterns**: Timeout, connection errors, assertion failures
2. **Test Names**: Failed test identifiers
3. **Stack Traces**: Error location and context
4. **Build Metadata**: Timestamps, duration, environment

## Feature Engineering
- Text preprocessing for log parsing
- Pattern extraction using regex
- Error categorization (timeout, flaky, deterministic)
- Confidence scoring for predictions

## Model Selection
- **Baseline**: Rule-based pattern matching
- **Advanced**: LLM-powered analysis (Gemini)
- **Evaluation**: MTTR reduction, accuracy, business impact