import os
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "products.sqlite")

def require_env(name: str) -> str:
    """Ensure an environment variable is present and return it, raising an exception otherwise."""
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required environment variable: '{name}'. Please configure it in your .env file.")
    return v

def get_deepseek_api_key() -> str:
    """Return the configured DeepSeek API key, or empty string if not set."""
    return os.getenv("DEEPSEEK_API_KEY", "")

def is_live_mode_available() -> bool:
    """Check if the DeepSeek API key is present and is not a default placeholder."""
    key = get_deepseek_api_key()
    return bool(key and "your_deepseek" not in key.lower())

def get_llm(temperature: float = 0.2, max_tokens: int = 800) -> ChatDeepSeek:
    """Instantiate and return the ChatDeepSeek LLM client."""
    require_env("DEEPSEEK_API_KEY")
    return ChatDeepSeek(
        model="deepseek-chat",
        temperature=temperature,
        max_tokens=max_tokens
    )

def print_banner(title: str):
    """Utility to print centered decorative text banners."""
    print("=" * 72)
    print(title.center(72))
    print("=" * 72)
