from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
import config_dev as config
from flask_moment import Moment
from flask_admin import Admin
from flaskext.markdown import Markdown

from app.admin_models import add_admin, AdminIndexView
from app.libs import db
from app.models import AnonymousUser, User

bootstrap = Bootstrap()
moment = Moment()
admin = Admin(name='后台管理系统', template_mode='bootstrap3', index_view=AdminIndexView())

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'
login_manager.login_message = '请先登录或注册'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


login_manager.anonymous_user = AnonymousUser


def create_app():
    app = Flask(__name__)
    Markdown(app)
    app.config.from_object(config)
    bootstrap.init_app(app=app)
    login_manager.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    register_blueprint(app)
    admin.init_app(app)
    add_admin(admin)
    return app


def register_blueprint(app):
    from app.main import main as main_blueprint
    from app.msg_board import msg as msg_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(msg_blueprint)


