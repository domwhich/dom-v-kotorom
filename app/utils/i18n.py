import json, os
from flask import session, request

_translations: dict[str, dict] = {}


def load_translations(app):
    base = os.path.join(app.root_path, "static", "locales")
    for lang in app.config["ALLOWED_LANGS"]:
        with open(os.path.join(base, f"{lang}.json"), encoding="utf-8") as f:
            _translations[lang] = json.load(f)


def t(key: str, **kwargs) -> str:
    lang = session.get("lang", "ru")
    val = _translations.get(lang, {}).get(key, key)
    if kwargs:
        try:
            val = val.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return val


def init_lang(app):
    """before_request: берём ?lang=... и сохраняем в сессию."""
    from flask import current_app

    @app.before_request
    def _set_lang():
        lang = request.args.get("lang")
        if lang in app.config["ALLOWED_LANGS"]:
            session["lang"] = lang
        elif "lang" not in session:
            session["lang"] = app.config["DEFAULT_LANG"]