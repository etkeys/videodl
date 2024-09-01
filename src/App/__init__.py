from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'develop'

from App.routes import queue_blueprint

app.register_blueprint(queue_blueprint)