from flask import Flask, render_template
from config import Config
from models import mongo, mail
from services.realtime import realtime_service
from flask_mail import Mail
from dotenv import load_dotenv # type: ignore
import os

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    mongo.init_app(app)
    mail.init_app(app)
    realtime_service.init_app(app)

    # Initialize User collection
    with app.app_context():
        from models.user import User
        User.init_collection()

    # Print environment variables for debugging
    print("MAIL_USERNAME:", app.config['MAIL_USERNAME'])
    print("MAIL_PASSWORD:", app.config['MAIL_PASSWORD'])
    print("MAIL_DEFAULT_SENDER:", app.config['MAIL_DEFAULT_SENDER'])

    # Create an admin user
    def create_admin():
        with app.app_context():
            admin_username = app.config["ADMIN_USERNAME"]
            admin_email = app.config["ADMIN_EMAIL"]
            admin_password = app.config["ADMIN_PASSWORD"]
            admin_role = app.config["ADMIN_ROLE"]

            if not User.find_by_email(admin_email):
                User.register_user(admin_username, admin_email, admin_password, role=admin_role)
                print("Admin user account created successfully")
            else:
                print("Admin user account already exists")

    create_admin()

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.responderRoute import responder_bp
    from routes.organizationRoute import organization_bp
    from routes.victimRoute import victim_bp
    from routes.resourceRoute import resource_bp
    from routes.reportRoute import report_bp
    from routes.victimProfileRoute import victimProfile_bp
    from routes.organizationProfileRoute import organizationProfile_bp
    from routes.responderProfileRoute import responderProfile_bp
    from routes.adminRoute import admin_bp
    from routes.settingsRoute import settings_bp
    from routes.main import main_bp  
    from routes.emergency import emergency_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(responder_bp, url_prefix='/responder')
    app.register_blueprint(organization_bp, url_prefix='/organization')
    app.register_blueprint(victim_bp, url_prefix='/victim')
    app.register_blueprint(resource_bp, url_prefix='/resource')
    app.register_blueprint(report_bp, url_prefix='/report')
    app.register_blueprint(victimProfile_bp, url_prefix='/victim/profile')
    app.register_blueprint(organizationProfile_bp, url_prefix='/organization/profile')
    app.register_blueprint(responderProfile_bp, url_prefix='/responder/profile')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(settings_bp)
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(emergency_bp, url_prefix='/emergency')

    @app.route('/')
    def landing():
        return render_template('frontpage.html')

    return app

if __name__ == '__main__':
    app = create_app()
    # Debugging: Print all registered routes
    realtime_service.socketio.run(app, debug=True)
