import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("Config")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-2.5-flash-lite")

if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not found in environment variables")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")