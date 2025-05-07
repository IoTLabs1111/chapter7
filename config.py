from pydantic_settings import BaseSettings, SettingsConfigDict

class BaseConfig(BaseSettings):
    DB_URL: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_CLOUD_NAME: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

base_config = BaseConfig()
