from flask import Response

def make_responce(message: str, code: int):
    return Response({"message": message}, status=code, mimetype="application/json")