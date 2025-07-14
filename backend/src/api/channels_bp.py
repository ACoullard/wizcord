from flask import Blueprint, request, session, jsonify
from flask_login import login_required, current_user
from flask_sse import sse
from .shared_resources import model, User

current_user: User


channel_bp = Blueprint("channel", __name__, url_prefix="/channel")


@channel_bp.route('/<channel_id>')
def get_messages(channel_id):
    pass


@channel_bp.post("/<channel_id>/post")
@login_required
def post_message():
    req = request.get_json()

    sse.publish({"message": req["content"]})

    model.add_message(
        author_id=current_user.id,
        channel_id=req["channelId"],
        content=req["content"]
    )