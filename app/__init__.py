from flask import Flask, session
from flask_login import LoginManager, current_user

from config import Config
from .models import db, User, Notification, ROLE_NAMES
from .utils.i18n import load_translations, init_lang, t

login_manager = LoginManager()


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = None

    load_translations(app)
    init_lang(app)

    app.jinja_env.globals["_"] = t
    app.jinja_env.globals["ROLE_NAMES"] = ROLE_NAMES

    from .routes.auth import bp as auth_bp
    from .routes.main import bp as main_bp
    from .routes.events import bp as events_bp
    from .routes.chats import bp as chats_bp
    from .routes.rules import bp as rules_bp
    from .routes.profile import bp as profile_bp
    from .routes.notifications import bp as notif_bp
    from .routes.admin import bp as admin_bp

    for bp in (auth_bp, main_bp, events_bp, chats_bp,
               rules_bp, profile_bp, notif_bp, admin_bp):
        app.register_blueprint(bp)

    @app.context_processor
    def inject_globals():
        unread = 0
        if current_user.is_authenticated:
            unread = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {
            "unread_count": unread,
            "current_lang": session.get("lang", "ru"),
        }

    return app


@login_manager.user_loader
def load_user(uid: str):
    return db.session.get(User, int(uid))