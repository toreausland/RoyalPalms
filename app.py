import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User

login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    configs = {
        'development': 'config.DevelopmentConfig',
        'production': 'config.ProductionConfig',
    }
    app.config.from_object(configs.get(config_name, configs['development']))

    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vennligst logg inn for å få tilgang.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.topics import topics_bp
    from blueprints.admin import admin_bp
    from blueprints.documents import documents_bp
    from blueprints.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(topics_bp, url_prefix='/temaer')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(documents_bp, url_prefix='/dokumenter')
    app.register_blueprint(profile_bp, url_prefix='/profil')

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
