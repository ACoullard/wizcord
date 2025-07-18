from flask import Blueprint, request, Response
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict
import time

from .shared_resources import model, User
from messages_manager import ChannelMessagesObserver

current_user: User


channel_bp = Blueprint("channel", __name__, url_prefix="/channel")

observers_dict: Dict[str, ChannelMessagesObserver] = {}




@channel_bp.route('/<channel_id>')
def get_messages(channel_id):
    pass


@channel_bp.route('/<channel_id>/message-stream')
def message_stream(channel_id):
    print(model.get_channel_ids_by_server(ObjectId()))
    if channel_id not in observers_dict:
        if model.channel_exists(ObjectId(channel_id)):
            observers_dict[channel_id] = ChannelMessagesObserver()
        else:
            print("went in here")
            return "Invalid channel id", 400
    
    observer = observers_dict[channel_id]
    listener = observer.add_listener()

    
    def event_stream():
        while True:
            result = listener.retrieve_update().str_dict_format()
            yield result
    
    return Response(event_stream(), mimetype='text/event-stream')



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
        req["content"],
        current_user.id,
        timestamp,
        ObjectId(channel_id))

    return {"message": "message recieved", "id": str(result_id)}, 200