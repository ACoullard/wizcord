from flask import Flask
from config import Config

def create_app(current_config=Config):
    app = Flask(__name__)
    app.config.from_object(current_config)
    
    from main import main_blueprint
    main_blueprint.template_folder = current_config.TEMPLATE_FOLDER_MAIN
    app.register_blueprint(main_blueprint)
    