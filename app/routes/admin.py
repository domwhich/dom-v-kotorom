from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash)
from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from ..models import db, User, Chat, Notification
from ..utils.decorators import admin_required

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@admin_required
def index():
    return redirect(url_for("admin.users"))


@bp.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")
        if role not in ("admin", "editor", "user"):
            flash("Неверная роль", "danger")
        elif len(username) < 3:
            flash("Логин минимум 3 символа", "danger")
        elif len(password) < 8:
            flash("Пароль минимум 8 символов", "danger")
        else:
            u = User(username=username, role=role)
            u.set_password(password)
            db.session.add(u)
            try:
                db.session.commit()
                flash(f"Пользователь {username} создан", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Логин уже занят", "danger")
        return redirect(url_for("admin.users"))

    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@bp.route("/users/<int:uid>/role", methods=["POST"])
@admin_required
def change_role(uid: int):
    u = db.session.get(User, uid)
    new_role = request.form.get("role")
    if not u or new_role not in ("admin", "editor", "user"):
        flash("Неверные данные", "danger")
        return redirect(url_for("admin.users"))
    if u.id == current_user.id:
        flash("Свою роль менять нельзя", "warning")
        return redirect(url_for("admin.users"))
    if u.role != new_role:
        u.role = new_role
        db.session.add(Notification(
            user_id=u.id, type="role_assigned", payload={"role": new_role},
        ))
        db.session.commit()
        flash("Роль обновлена", "success")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:uid>/password", methods=["POST"])
@admin_required
def reset_password(uid: int):
    u = db.session.get(User, uid)
    pwd = request.form.get("password", "")
    if not u:
        flash("Нет пользователя", "danger")
    elif len(pwd) < 8:
        flash("Пароль минимум 8 символов", "danger")
    else:
        u.set_password(pwd)
        db.session.commit()
        flash("Пароль обновлён", "success")
    return redirect(url_for("admin.users"))


@bp.route("/users/<int:uid>/delete", methods=["POST"])
@admin_required
def delete_user(uid: int):
    u = db.session.get(User, uid)
    if not u:
        pass
    elif u.id == current_user.id:
        flash("Себя удалить нельзя", "warning")
    else:
        db.session.delete(u)
        db.session.commit()
        flash("Пользователь удалён", "success")
    return redirect(url_for("admin.users"))


@bp.route("/chats", methods=["GET", "POST"])
@admin_required
def chats():
    if request.method == "POST":
        c = Chat(
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip() or None,
            url=request.form.get("url", "").strip(),
            sort_order=int(request.form.get("sort_order", "0") or 0),
            is_visible=bool(request.form.get("is_visible")),
        )
        if c.title and c.url:
            db.session.add(c)
            db.session.commit()
            flash("Чат добавлен", "success")
        else:
            flash("Заполните название и ссылку", "danger")
        return redirect(url_for("admin.chats"))

    items = Chat.query.order_by(Chat.sort_order.asc(), Chat.id.asc()).all()
    return render_template("admin/chats.html", chats=items)


@bp.route("/chats/<int:cid>/toggle", methods=["POST"])
@admin_required
def toggle_chat(cid: int):
    c = db.session.get(Chat, cid)
    if c:
        c.is_visible = not c.is_visible
        db.session.commit()
    return redirect(url_for("admin.chats"))


@bp.route("/chats/<int:cid>/delete", methods=["POST"])
@admin_required
def delete_chat(cid: int):
    c = db.session.get(Chat, cid)
    if c:
        db.session.delete(c)
        db.session.commit()
    return redirect(url_for("admin.chats"))