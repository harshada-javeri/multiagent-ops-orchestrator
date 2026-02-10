"""Okahu Observability Integration for QAOps Orchestrator"""
import os
from functools import wraps

class OkahuTracer:
    def __init__(self):
        self.api_key = os.getenv('OKAHU_API_KEY')
        self.enabled = bool(self.api_key)
    
    def trace_agent(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.enabled:
                print(f"[OKAHU] Tracing: {func.__name__}")
            result = func(*args, **kwargs)
            return result
        return wrapper

tracer = OkahuTracer()