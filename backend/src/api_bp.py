from flask import Blueprint, Response, request, session
from flask_login import login_required, current_user
from shared_resources import model, encrypt

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/init-e2ee")
def init_e2ee():
    """Initializes the x25519 key exchange that starts the end 2 end encryption (E2EE).
    Returns the public key and signature while storing the private key in the session.
    """
    public_key, private_key = encrypt.init_x25519_exchange()
    
    session["x255_private_key_bytes"] = private_key.private_bytes_raw()

    public_key_string = encrypt.public_key_to_string(public_key)

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
    try:
        symmetric_key = encrypt.complete_x25519_exchange(
            session["x255_private_key_bytes"], recieved_public_key)
    except Exception as e:
        return make_error_responce("Key exchange failed.", 401)

    session["symmetric_key"] = symmetric_key


@api_bp.route("/servers")
@login_required
def get_available_servers():
    server_ids = model.get_viewable_server_ids(current_user.id)


def make_error_responce(message: str, code: int):
    return Response({"message": message}, status=code, mimetype="application/json")