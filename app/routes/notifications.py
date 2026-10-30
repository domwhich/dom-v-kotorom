from flask import Blueprint, render_template, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user

from ..models import db, Notification

bp = Blueprint("notifications", __name__)


@bp.route("/notifications")
@login_required
def list_notifications():
    items = Notification.query.filter_by(user_id=current_user.id) \
                              .order_by(Notification.created_at.desc()).all()
    return render_template("notifications.html", notifications=items)


@bp.route("/notifications/mark-all", methods=["POST"])
@login_required
def mark_all():
    Notification.query.filter_by(user_id=current_user.id, is_read=False) \
                      .update({"is_read": True})
    db.session.commit()
    return redirect(url_for("notifications.list_notifications"))


@bp.route("/notifications/<int:nid>/read", methods=["POST"])
@login_required
def mark_one(nid: int):
    n = Notification.query.filter_by(id=nid, user_id=current_user.id).first() or abort(404)
    n.is_read = True
    db.session.commit()
    return redirect(url_for("notifications.list_notifications"))


@bp.route("/api/notifications/unread-count")
@login_required
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    latest = Notification.query.filter_by(user_id=current_user.id) \
                               .order_by(Notification.created_at.desc()).limit(5).all()
    return jsonify(
        count=count,
        latest=[{
            "id": n.id, "type": n.type, "payload": n.payload,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        } for n in latest],
    )