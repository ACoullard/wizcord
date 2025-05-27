from flask import Flask
from config import Config

def create_app(current_config=Config):
    app = Flask(__name__)
    app.config.from_object(current_config)

@create_app(Config).shell_context_processor
def make_shell_context():
    return {}