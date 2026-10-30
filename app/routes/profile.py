from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from ..models import db
from ..utils.i18n import t

bp = Blueprint("profile", __name__)


@bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@bp.route("/profile/name", methods=["POST"])
@login_required
def change_name():
    name = request.form.get("display_name", "").strip()
    if not name:
        flash(t("profile.name_empty"), "danger")
    elif len(name) > 64:
        flash(t("profile.name_too_long"), "danger")
    else:
        current_user.display_name = name
        db.session.commit()
        flash(t("profile.name_changed"), "success")
    return redirect(url_for("profile.profile"))


@bp.route("/profile/password", methods=["POST"])
@login_required
def change_password():
    old = request.form.get("old_password", "")
    new = request.form.get("new_password", "")
    confirm = request.form.get("confirm_password", "")

    if not current_user.check_password(old):
        flash(t("profile.wrong_password"), "danger")
    elif len(new) < 8:
        flash(t("profile.password_too_short"), "danger")
    elif new != confirm:
        flash(t("profile.password_mismatch"), "danger")
    else:
        current_user.set_password(new)
        db.session.commit()
        flash(t("profile.password_changed"), "success")

    return redirect(url_for("profile.profile"))