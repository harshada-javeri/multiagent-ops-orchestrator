import os
import subprocess

models = [
    "gemini/gemini-2.5-flash",
    "openai/gpt-4o-mini",
    "ollama_chat/gemma3:latest"
]

for model in models:
    print(f"\n--- Running orchestrator with model: {model} ---")
    env = os.environ.copy()
    env["LLM_MODEL"] = model
    subprocess.run(["python", "predict.py", "sample_ci_logs.txt"], env=env)
