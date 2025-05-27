import os

class Config():
    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    
    SECRET_KEY = os.environ.get("SECRET KEY")
    
    # Put paths to submodules here. ie:
    #  TEMPLATE_FOLDER_MAIN = os.path.join(basedir, 'app//main//templates') 