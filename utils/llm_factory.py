
from litellm import completion
from opentelemetry import trace
from utils.config import GOOGLE_API_KEY, OPENAI_API_KEY, LLM_MODEL, logger

tracer = trace.get_tracer("llm_factory")

def run_llm(prompt: str, model: str | None = None):
    model = model or LLM_MODEL

    with tracer.start_as_current_span("llm_completion"):
        # -------- GEMINI ROUTE --------
        if model.startswith("gemini"):
            if not GOOGLE_API_KEY:
                logger.warning("GOOGLE_API_KEY not found in environment variables")
                raise ValueError("GOOGLE_API_KEY missing")
            from google import genai
            client = genai.Client(api_key=GOOGLE_API_KEY)
            model_name = model.split("/")[-1]
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text
        # -------- OPENAI / OLLAMA ROUTE --------
        else:
            if model.startswith("openai") and not OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY not found in environment variables")
                raise ValueError("OPENAI_API_KEY missing")
            response = completion(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["choices"][0]["message"]["content"]