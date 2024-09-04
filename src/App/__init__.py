from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'develop'

from App.routes import *

app.register_blueprint(core_blueprint)
app.register_blueprint(todo_blueprint)