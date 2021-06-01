import os

from flask import Flask, redirect, url_for, send_from_directory, render_template

from CLIMB.database import Database
from CLIMB.email import Email

db = Database()
email = Email()


def create_app():
    """ Initialize the core application. """

    app = Flask(__name__,)
    app.config.from_object('config.Config')

    db.init_app(app)
    email.init_app(app)

    with app.app_context():
        # Import and register blueprints
        from .auth import auth_bp
        from .dashboard import dashboard_bp
        from .first_run import first_run_bp

        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        app.register_blueprint(first_run_bp, url_prefix='/init')

        # Set the response for favicon
        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(app.root_path, 'static'),
                                       'favicon.ico', mimetype='image/vnd.microsoft.icon')

        # Home page redirect to dashboard
        @app.route('/')
        def home():
            return redirect(url_for('dashboard_bp.dashboard'))

        # Error pages
        @app.errorhandler(401)
        def unauthorized_error(error):
            return render_template('401.jinja2'), 401

        @app.errorhandler(403)
        def forbidden_error(error):
            return render_template('403.jinja2'), 403

        @app.errorhandler(404)
        def not_found_error(error):
            return render_template('404.jinja2'), 404

        @app.errorhandler(500)
        def internal_error(error):
            return render_template('500.jinja2'), 500

        return app
