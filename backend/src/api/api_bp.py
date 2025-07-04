import base64
from bson import ObjectId
from flask import Blueprint, request, session
from flask_login import login_required, current_user
from .shared_resources import model, encrypt, User
from .login_bp import login_bp

from utils import make_responce

api_bp = Blueprint("api", __name__, url_prefix="/api")

api_bp.register_blueprint(login_bp)

current_user: User

@api_bp.route("/init-e2ee")
def init_e2ee():
    """Initializes the x25519 key exchange that starts the end 2 end encryption (E2EE).
    Returns the public key and signature while storing the private key in the session.
    """
    public_key, private_key = encrypt.init_x25519_exchange()
    
    session["x255_private_key_bytes"] = private_key.private_bytes_raw()

    public_key_b64 = base64.b64encode(public_key.public_bytes_raw())

    # public_key_string = encrypt.public_key_to_string(public_key)
    public_key_string = public_key_b64.decode("utf-8")

    return {
        "x255_public_key": public_key_string,
    }


@api_bp.post("/respond-e2ee")
def respond_e2ee():
    """Endpoint for responding with a x25519 public key and completing the key exchange,
    allowing end to end encryption to begin.
    """
    req = request.get_json()
    recieved_public_key = req["public_key"]

    client_public_bytes = base64.b64decode(recieved_public_key)
    try:
        symmetric_key = encrypt.complete_x25519_exchange(
            session["x255_private_key_bytes"], client_public_bytes)
        
        session["symmetric_key"] = symmetric_key
        return make_responce("sucessful key exchange", 200)
    
    except Exception as e:
        print(e)
        return make_responce("Key exchange failed.", 401)

    
# @api_bp.route("/servers")
# def get_available_servers():
#     print("test!!!!!!!!!!!!!")
#     return [{"id":1, "name":"test server 1"}, 
#             {"i2d":1, "name":"test server "}, 
#             {"id":1, "name":"test server 3"},
#             {"id":3, "name": "yippeeeeeeeeeee"}]

@api_bp.route("/servers")
@login_required
def get_available_servers():
    server_ids = current_user.viewable_servers
    res = []
    for id in server_ids:
        server = model.get_server_by_id(id)
        res.append({
            "id": str(id),
            "name": server["name"],
            })

    return res


@api_bp.post("/post")
@login_required
def post_message():
    req = request.get_json()
    
    model.add_message(
        author_id=current_user.id,
        channel_id=req["channelId"],
        content=req["content"]
    )    


@api_bp.get("/server-data/<server_id>")
@login_required
def get_server_data(server_id):
    server_id = ObjectId(server_id)
    if server_id not in current_user.viewable_servers:
        return make_responce("Not authorized to view server data", 401)
    
    server_data = model.get_server_by_id(server_id)
    channels = model.get_channel_ids_by_server(server_id)
    users = model.get_user_ids_in_server(server_id)
    
    channels = [str(channel) for channel in channels]
    users = [str(user) for user in users]

    return {
        "name": server_data["name"],
        "roles": server_data.get("roles"),
        "channels": channels,
        "users": users
    }
