import os
from typing import List

class Settings:
    PROJECT_NAME: str = "PROOFFIT AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Enterprise AI Data Readiness Assessment Engine. Know your data before you trust your AI."
    API_PREFIX: str = "/api"
    MAX_FILE_SIZE_BYTES: int = 100_000_000  # 100 MB max upload
    ALLOWED_EXTENSIONS: List[str] = [".csv"]
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

settings = Settings()
