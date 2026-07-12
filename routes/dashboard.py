from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Vehicle, Trip

# 1. Define the Blueprint first
dashboard_bp = Blueprint('dashboard', __name__)

# 2. Define the route using the defined blueprint
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Fetch real counts from the database
    active_vehicles = Vehicle.query.filter_by(status=Vehicle.STATUS_AVAILABLE).count()
    maintenance_count = Vehicle.query.filter_by(status=Vehicle.STATUS_MAINTENANCE).count()
    pending_trips = Trip.query.filter_by(status=Trip.STATUS_SCHEDULED).count()
    
    # Calculate utilization
    total_vehicles = Vehicle.query.count()
    utilization = (active_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0

    # Get recent trips
    recent_trips = Trip.query.order_by(Trip.created_at.desc()).limit(5).all()

    return render_template('dashboard.html', 
                           active_vehicles=active_vehicles,
                           maintenance_count=maintenance_count,
                           pending_trips=pending_trips,
                           utilization=round(utilization, 1),
                           trips=recent_trips,
                           current_user=current_user)