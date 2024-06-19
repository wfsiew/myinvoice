from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_base_url: str
    id_srv_base_url: str
    client_id: str
    client_secret: str
    tin: str
    brn: str
    api_base_url_pwc: str
    client_id_pwc: str
    client_secret_pwc: str
    scope_pwc: str

    model_config = SettingsConfigDict(env_file=".envx")