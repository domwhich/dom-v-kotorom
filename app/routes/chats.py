from flask import Blueprint, render_template
from ..models import Chat

bp = Blueprint("chats", __name__)


@bp.route("/chats")
def chats():
    items = Chat.query.filter_by(is_visible=True) \
                       .order_by(Chat.sort_order.asc(), Chat.id.asc()).all()
    return render_template("chats.html", chats=items)