from flask import Flask, redirect, url_for, render_template
from flask_login import login_required, current_user
from config import Config
from models import db
from auth import auth_bp, init_login_manager
# Importing blueprints
from routes.trips import trips_bp
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database and Auth initialization
    db.init_app(app)
    init_login_manager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(trips_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # These routes are now protected by login_required
    @app.route('/vehicles')
    @login_required
    def vehicles():
        return render_template('vehicles.html', current_user=current_user)

    @app.route('/drivers')
    @login_required
    def drivers():
        return render_template('drivers.html', current_user=current_user)

    @app.route('/maintenance')
    @login_required
    def maintenance():
        return render_template('maintenance.html', current_user=current_user)

    @app.route('/fuel_expense')
    @login_required
    def fuel_expense():
        return render_template('fuel_expense.html', current_user=current_user)
    
    @app.route('/settings')
    @login_required
    def settings():
        return render_template('settings.html', current_user=current_user)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)