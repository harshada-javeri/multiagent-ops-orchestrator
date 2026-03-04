# Example agent using Ollama via LiteLLM
import os
from utils.llm_factory import run_llm
from opentelemetry import trace

tracer = trace.get_tracer("OllamaDebugAgent")

class OllamaDebugAgent:
    def __init__(self, name="OllamaDebugAgent"):
        self.name = name
        self.model = "ollama_chat/gemma3:latest"

    def process(self, message):
        prompt = f"Analyze this stack trace and propose debugging steps:\n{message.content}"
        with tracer.start_as_current_span("llm_ollama_debug_analysis"):
            result = run_llm(prompt, self.model)
        return {"debug_steps": result}
