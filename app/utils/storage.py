import uuid
from flask import current_app
from supabase import create_client

_client = None


def _get_client():
    global _client
    if _client is None:
        url = current_app.config["SUPABASE_URL"]
        key = current_app.config["SUPABASE_SERVICE_KEY"]
        if not url or not key:
            raise RuntimeError("Supabase не настроен: отсутствуют URL/SERVICE_KEY")
        _client = create_client(url, key)
    return _client


def upload_cover(file_storage) -> str:
    """Заливает файл в Supabase Storage, возвращает публичный URL."""
    filename = file_storage.filename or ""
    if "." not in filename:
        raise ValueError("Файл без расширения")
    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in {"png", "jpg", "jpeg", "webp", "gif"}:
        raise ValueError(f"Недопустимое расширение: {ext}")

    key = f"{uuid.uuid4().hex}.{ext}"
    bucket = current_app.config["SUPABASE_BUCKET"]
    data = file_storage.read()

    client = _get_client()
    client.storage.from_(bucket).upload(
        path=key,
        file=data,
        file_options={"content-type": file_storage.mimetype or f"image/{ext}"},
    )
    return client.storage.from_(bucket).get_public_url(key)