from flask import Blueprint, request, Response
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict

from .shared_resources import model, User
from messages_manager import ChannelMessagesObserver

current_user: User


channel_bp = Blueprint("channel", __name__, url_prefix="/channel")

observers_dict: Dict[str, ChannelMessagesObserver] = {}




@channel_bp.route("/<channel_id>")
def get_messages(channel_id):
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
    if channel_id not in observers_dict:
        if model.channel_exists(ObjectId(channel_id)):
            observers_dict[channel_id] = ChannelMessagesObserver()
        else:
            return "Invalid channel id", 400
    
    observer = observers_dict[channel_id]
    listener = observer.add_listener()

    
    def event_stream():
        while True:
            result = listener.retrieve_update().str_dict_format()
            yield f"data: {result}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")



@channel_bp.post("/<channel_id>/post")
@login_required
def post_message(channel_id):
    req = request.get_json()

    if channel_id not in observers_dict:
        observers_dict[channel_id] = ChannelMessagesObserver()


    timestamp = datetime.now(tz=timezone.utc)

    result_id = model.add_message(
        author_id=current_user.id,
        content=req["content"],
        timestamp=timestamp,
        channel_id=ObjectId(channel_id)
    )
    
    observers_dict[channel_id].publish(
        result_id,
        current_user.id,
        ObjectId(channel_id),
        req["content"],
        timestamp
    )

    return {"message": "message recieved", "id": str(result_id)}, 200