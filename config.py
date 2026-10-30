import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    _db_url = os.environ.get("DATABASE_URL", "sqlite:///dom.db")
    # Render выдаёт postgres://, SQLAlchemy хочет postgresql://
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
    SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "event-covers")

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 МБ на загрузку
    ALLOWED_LANGS = ["ru", "en"]
    DEFAULT_LANG = "ru"