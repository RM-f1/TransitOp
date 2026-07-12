from flask import Blueprint, render_template

# Set up the blueprint for the dashboard route
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # Dummy data so your UI definitely works while teammate finishes the DB logic
    kpi_data = {
        'active_vehicles': 12,
        'available_vehicles': 8,
        'in_maintenance': 2,
        'active_trips': 4,
        'pending_trips': 3,
        'drivers_on_duty': 5,
        'fleet_utilization': 75.5
    }
    
    dummy_trips = [
        {'id': 'TRP-001', 'driver': 'Alex', 'vehicle': 'Van-05', 'status': 'On Trip'},
        {'id': 'TRP-002', 'driver': 'Sam', 'vehicle': 'Truck-02', 'status': 'Completed'}
    ]

    # In a real app, you would pass the current_user. Hardcoding for UI testing.
    mock_user = {'role': 'Fleet Manager'}

    return render_template('dashboard.html', kpis=kpi_data, trips=dummy_trips, current_user=mock_user)