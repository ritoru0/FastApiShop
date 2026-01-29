from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
   
    SECRET_KEY: str
    ALGORITHM: str = "HS256" 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  

   
    REAL_DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",              
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore"                
    )

settings = Settings()