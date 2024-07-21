from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .myconfig import *

db = SQLAlchemy()


def create_app(database_uri):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "iris-email-analyzer"
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.app_context().push()

    from .views import views
    app.register_blueprint(views)

    from .models import User

    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "views.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
