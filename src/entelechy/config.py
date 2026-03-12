import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """System settings for the entelechy."""
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Kernel Settings
    MAX_AUTONOMOUS_STEPS: int = 10
    HITL_CONFIDENCE_THRESHOLD: float = 0.8
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Initialize settings
settings = Settings()

def setup_logging():
    """Configure system-wide logging."""
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("entelechy.log")
        ]
    )
    logger = logging.getLogger("Entelechy")
    logger.info(f"Entelechy initialized in {settings.ENV} mode")
    return logger

logger = setup_logging()
