from flask import Flask, redirect, url_for, render_template
from config import Config

from models import db
from auth import auth_bp, init_login_manager
from routes.trips import trips_bp

# Import your route blueprints
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Wire up the database
    db.init_app(app)

    # Wire up Flask-Login and register the real auth routes
    init_login_manager(app)
    app.register_blueprint(auth_bp)

    # Register the real trips routes (replaces the old mock /trips stub)
    app.register_blueprint(trips_bp)

    # Register your UI blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)

    # Redirect the root URL to the real login page (auth_bp owns /login now)
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # NOTE: /login and /trips stub routes removed — auth_bp and trips_bp
    # now own those endpoints for real (with actual DB-backed auth and
    # validation instead of mock data).

    # Temporary UI route for Vehicles — still a stub until routes/vehicles.py exists
    @app.route('/vehicles')
    def vehicles():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('vehicles.html', current_user=mock_user)

    # Temporary UI route for Drivers — still a stub until routes/drivers.py exists
    @app.route('/drivers')
    def drivers():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('drivers.html', current_user=mock_user)

    # Temporary UI route for Maintenance — still a stub until routes/maintenance.py exists
    @app.route('/maintenance')
    def maintenance():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('maintenance.html', current_user=mock_user)

    # Temporary UI route for Fuel & Expenses — still a stub until routes/fuel_expense.py exists
    @app.route('/fuel_expense')
    def fuel_expense():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('fuel_expense.html', current_user=mock_user)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)