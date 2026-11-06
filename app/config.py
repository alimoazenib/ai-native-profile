import os
from dotenv import load_dotenv

load_dotenv()

# LLM API configuration (supports OpenAI, Hamravesh, OpenRouter, or university endpoints)
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# External GitHub API configuration
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "torvalds")