from flask import Flask, redirect, url_for, render_template
from config import Config

# Import your route blueprints
from routes.dashboard import dashboard_bp
from routes.reports import reports_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register your UI blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)

    # Redirect the root URL to your Login page
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    # Login Route
    @app.route('/login')
    def login():
        return render_template('login.html')

    # Temporary UI route for Vehicles
    @app.route('/vehicles')
    def vehicles():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('vehicles.html', current_user=mock_user)

    # Temporary UI route for Drivers
    @app.route('/drivers')
    def drivers():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('drivers.html', current_user=mock_user)

    # Temporary UI route for Trips
    @app.route('/trips')
    def trips():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('trips.html', current_user=mock_user)

    # Temporary UI route for Maintenance
    @app.route('/maintenance')
    def maintenance():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('maintenance.html', current_user=mock_user)

    # Temporary UI route for Fuel & Expenses
    @app.route('/fuel_expense')
    def fuel_expense():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('fuel_expense.html', current_user=mock_user)
    
    # Temporary UI route for Settings
    @app.route('/settings')
    def settings():
        mock_user = {'role': 'Fleet Manager'}
        return render_template('settings.html', current_user=mock_user)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)