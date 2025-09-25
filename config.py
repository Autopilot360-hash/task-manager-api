import os
from typing import Optional

class Settings:
    # Base de données
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./tasks.db"
    )
    
    # Sécurité
    secret_key: str = os.getenv(
        "SECRET_KEY", 
        "votre-clé-secrète-très-sécurisée-changez-en-production"
    )
    
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    
    # Environnement
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

settings = Settings()
