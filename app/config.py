
from pathlib import Path
from pydantic import BaseSettings

project_dir = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Class for managing settings"""
    POSTGRESS_DATABASE: str
    POSTGRESS_USER: str
    POSTGRESS_PASSWORD: str
    POSTGRESS_HOST: str
    POSTGRESS_PORT: int
    DATA: Path = project_dir / "data"
    URL: str

    class Config:
        """Class for managing settings config"""
        env_file = ".env"
        case_sensitive = True
    
settings = Settings()  # type: ignore

