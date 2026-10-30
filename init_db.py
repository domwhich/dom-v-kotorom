from app import create_app
from app.models import db, User
from config import Config

app = create_app(Config)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        u = User(username="admin", role="admin")
        u.set_password("changeme123")
        db.session.add(u)
        db.session.commit()
        print("✓ Создан admin / changeme123  —  СМЕНИТЕ ПАРОЛЬ!")
    else:
        print("admin уже существует")