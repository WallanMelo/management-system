import json
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # PostgreSQL
    # ==========================
    database_host: str
    database_port: int
    database_name: str
    database_user: str
    database_password: str

    # ==========================
    # JWT
    # ==========================
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # ==========================
    # Google Drive
    # ==========================
    google_credentials: str
    google_drive_root_folder_id: str | None = None

    google_client_id: str | None = None
    google_client_secret: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

    polling_interval: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


    @property
    def google_credentials_dict(self) -> dict:
        """Converte a string JSON do Google para dicionario tratando as quebras de linha da chave privada."""
        data = json.loads(self.google_credentials)
        if "private_key" in data and isinstance(data["private_key"], str):
            data["private_key"] = data["private_key"].replace("\\n", "\n")
        return data


settings = Settings()