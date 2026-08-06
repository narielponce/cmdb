# backend/app/config.py
import os

class Settings:
    PROJECT_NAME: str = "NetTrack Network CMDB & ITAM"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:postgres@db:5432/cmdb"
    )
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "adjuntos_remitos")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeyfornettrackcmdbsecurity2026")
    SUPERADMIN_USER: str = os.getenv("SUPERADMIN_USER", "admin")
    SUPERADMIN_PASSWORD: str = os.getenv("SUPERADMIN_PASSWORD", "adminpassword")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 600

settings = Settings()

# Crear directorio de adjuntos si no existe
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)
