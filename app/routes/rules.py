from flask import Blueprint, render_template
bp = Blueprint("rules", __name__)


@bp.route("/rules")
def rules():
    return render_template("rules.html")