from flask import Blueprint, render_template
from flask_login import login_required, current_user # 1. Import login tools

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required # 2. Force the user to be logged in
def reports():
    # Keep your report data logic here
    report_data = {
        'fuel_efficiency': '8.5 km/L',
        'fleet_utilization': 75.5,
        'operational_cost': '$12,450',
        'avg_roi': '14.2%'
    }
    
    # 3. Use the REAL logged-in user from the database
    return render_template('reports.html', data=report_data, current_user=current_user)