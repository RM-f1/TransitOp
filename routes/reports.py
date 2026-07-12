from flask import Blueprint, render_template

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
def reports():
    # Dummy data ensuring the UI works perfectly right now
    report_data = {
        'fuel_efficiency': '8.5 km/L',
        'fleet_utilization': 75.5,
        'operational_cost': '$12,450',
        'avg_roi': '14.2%'
    }
    
    # THE FIX: Pass the dummy user so base.html can render the sidebar
    mock_user = {'role': 'Fleet Manager'}
    
    return render_template('reports.html', data=report_data, current_user=mock_user)