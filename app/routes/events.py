from datetime import datetime
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, abort)
from flask_login import current_user, login_required

from ..models import db, Event, User, Notification
from ..utils.decorators import editor_required
from ..utils.storage import upload_cover
from ..utils.i18n import t

bp = Blueprint("events", __name__, url_prefix="/events")


def _parse_datetime(form) -> datetime | None:
    try:
        return datetime.strptime(
            f"{form.get('date','').strip()} {form.get('time','').strip()}",
            "%Y-%m-%d %H:%M",
        )
    except ValueError:
        return None


@bp.route("/")
def list_events():
    events = Event.query.order_by(Event.date.asc()).all()
    return render_template("events.html", events=events, now=datetime.utcnow())


@bp.route("/new", methods=["GET", "POST"])
@login_required
@editor_required
def create():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        date = _parse_datetime(request.form)
        if not (title and description and date):
            flash("Заполните все поля корректно", "danger")
            return render_template("event_form.html", event=None)

        cover_url = None
        f = request.files.get("cover")
        if f and f.filename:
            try:
                cover_url = upload_cover(f)
            except Exception as e:
                flash(f"Обложка не загружена: {e}", "warning")

        event = Event(title=title, description=description, date=date,
                      cover_url=cover_url, author_id=current_user.id)
        db.session.add(event)
        db.session.flush()

        # Рассылка уведомлений всем, кроме автора
        for u in User.query.filter(User.id != current_user.id).all():
            db.session.add(Notification(
                user_id=u.id,
                type="event_created",
                payload={"title": event.title, "event_id": event.id,
                         "author": current_user.username},
            ))
        db.session.commit()
        flash(t("events.created"), "success")
        return redirect(url_for("events.list_events"))

    return render_template("event_form.html", event=None)


@bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
@editor_required
def edit(event_id: int):
    event = db.session.get(Event, event_id) or abort(404)
    if not (current_user.is_admin() or event.author_id == current_user.id):
        abort(403)

    if request.method == "POST":
        event.title = request.form.get("title", "").strip()
        event.description = request.form.get("description", "").strip()
        date = _parse_datetime(request.form)
        if not (event.title and event.description and date):
            flash("Заполните все поля корректно", "danger")
            return render_template("event_form.html", event=event)
        event.date = date
        f = request.files.get("cover")
        if f and f.filename:
            try:
                event.cover_url = upload_cover(f)
            except Exception as e:
                flash(f"Обложка не загружена: {e}", "warning")
        db.session.commit()
        return redirect(url_for("events.list_events"))

    return render_template("event_form.html", event=event)


@bp.route("/<int:event_id>/delete", methods=["POST"])
@login_required
@editor_required
def delete(event_id: int):
    event = db.session.get(Event, event_id) or abort(404)
    if not (current_user.is_admin() or event.author_id == current_user.id):
        abort(403)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for("events.list_events"))