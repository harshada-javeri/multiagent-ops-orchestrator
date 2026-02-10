# AWS AgentCore Deployment Configuration

resource "aws_bedrock_agentcore_runtime" "qaops" {
  name            = "qaops-orchestrator"
  image_uri       = var.docker_image_uri
  memory_mb       = 4096
  timeout_seconds = 300
  
  environment_variables = {
    OKAHU_API_KEY          = var.okahu_api_key
    AGENTCORE_RUNTIME_ID   = aws_bedrock_agentcore_runtime.qaops.id
  }
}

resource "aws_bedrock_agentcore_gateway" "qaops" {
  name = "qaops-gateway"
  
  authorization_configuration {
    type = "JWT"
  }
}

output "runtime_id" {
  value = aws_bedrock_agentcore_runtime.qaops.id
}

output "gateway_id" {
  value = aws_bedrock_agentcore_gateway.qaops.id
}