from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    # Log configuration
    LOG_LEVEL: str = "INFO"


settings = Settings() 