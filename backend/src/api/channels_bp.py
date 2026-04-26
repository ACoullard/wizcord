from flask import Blueprint, request, Response
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime, timezone
import json

from .shared_resources import model, User, redis_client

current_user: User

channel_bp = Blueprint("channel", __name__, url_prefix="/channel")


def _get_authorized_channel(channel_id: str):
    """Fetch channel and verify current user can view it.
    Returns (channel, None) on success, (None, error_response) on failure.
    """
    try:
        channel = model.get_channel_by_id(ObjectId(channel_id))
    except Exception:
        return None, ("Invalid channel id", 400)
    if channel["server_id"] not in current_user.viewable_servers():
        return None, ("Not authorized to view channel", 401)
    return channel, None


@channel_bp.route("/<channel_id>")
@login_required
def get_messages(channel_id):
    _, err = _get_authorized_channel(channel_id)
    if err:
        return err

    page_num = request.args.get("page", default=0, type=int)
    page_limit = request.args.get("limit", default=10, type=int)

    result = list(model.get_paginated_messages(ObjectId(channel_id), page_num, page_limit))[0]

    for message in result["data"]:
        message["id"] = str(message.pop("_id"))
        message["author_id"] = str(message["author_id"])

    return result


@channel_bp.route("/message-stream")
@login_required
def message_stream():
    channel_id = request.args.get("channel", type=str)
    _, err = _get_authorized_channel(channel_id)
    if err:
        return err

    def event_stream():
        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"channel:{channel_id}")
        try:
            while True:
                message = pubsub.get_message(timeout=30)
                if message is None or message["type"] != "message":
                    yield ": heartbeat\n\n"
                else:
                    yield f"data: {message['data'].decode()}\n\n"
        finally:
            pubsub.unsubscribe()
            pubsub.close()

    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Cache-Control"] = "no-cache"
    return response


@channel_bp.route("/server-member-stream")
@login_required
def server_member_stream():
    server_id = request.args.get("server", type=str)

    try:
        model.get_server_by_id(ObjectId(server_id))
    except Exception:
        return "Invalid server id", 400

    if ObjectId(server_id) not in current_user.viewable_servers():
        return "Not authorized to view server", 401

    def event_stream():
        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"server_members:{server_id}")
        try:
            while True:
                message = pubsub.get_message(timeout=30)
                if message is None or message["type"] != "message":
                    yield ": heartbeat\n\n"
                else:
                    yield f"data: {message['data'].decode()}\n\n"
        finally:
            pubsub.unsubscribe()
            pubsub.close()

    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers["X-Accel-Buffering"] = "no"
    response.headers["Cache-Control"] = "no-cache"
    return response


@channel_bp.post("/<channel_id>/post")
@login_required
def post_message(channel_id):
    _, err = _get_authorized_channel(channel_id)
    if err:
        return err

    req = request.get_json()
    timestamp = datetime.now(tz=timezone.utc)

    result_id = model.add_message(
        author_id=current_user.id,
        content=req["content"],
        timestamp=timestamp,
        channel_id=ObjectId(channel_id)
    )

    redis_client.publish(f"channel:{channel_id}", json.dumps({
        "id": str(result_id),
        "content": req["content"],
        "author_id": str(current_user.id),
        "timestamp": str(timestamp),
        "channel_id": channel_id
    }))

    return {"message": "message recieved", "id": str(result_id)}, 200
