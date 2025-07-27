from pydantic import BaseSettings

class Settings(BaseSettings):
    HACKRX_SECRET_TOKEN: str

    class Config:
        env_file = ".env"

settings = Settings()
