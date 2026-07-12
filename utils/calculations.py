

from models import db, Vehicle, Trip, MaintenanceRecord, FuelExpense


def total_fuel_cost(vehicle_id):
    """Sum of all fuel expenses for a given vehicle."""
    result = db.session.query(db.func.sum(FuelExpense.cost)) \
        .filter(FuelExpense.vehicle_id == vehicle_id) \
        .scalar()
    return round(result or 0.0, 2)


def total_maintenance_cost(vehicle_id):
    """Sum of all maintenance costs for a given vehicle."""
    result = db.session.query(db.func.sum(MaintenanceRecord.cost)) \
        .filter(MaintenanceRecord.vehicle_id == vehicle_id) \
        .scalar()
    return round(result or 0.0, 2)


def trip_count_by_status():
    """
    Returns dict like {'scheduled': 3, 'in_progress': 1, 'completed': 12, 'cancelled': 2}
    Used to feed dashboard chart.
    """
    rows = db.session.query(Trip.status, db.func.count(Trip.id)) \
        .group_by(Trip.status) \
        .all()
    counts = {status: count for status, count in rows}
    # Ensure all known statuses are present even if zero, so the chart
    # doesn't silently drop a category
    for status in [Trip.STATUS_SCHEDULED, Trip.STATUS_IN_PROGRESS,
                   Trip.STATUS_COMPLETED, Trip.STATUS_CANCELLED]:
        counts.setdefault(status, 0)
    return counts


def average_cost_per_km(vehicle_id):
    """
    (total fuel + total maintenance cost) / total distance driven,
    across all trips for this vehicle. Returns 0.0 if no distance logged,
    to avoid a ZeroDivisionError blowing up the reports page mid-demo.
    """
    total_distance = db.session.query(db.func.sum(Trip.distance_km)) \
        .filter(Trip.vehicle_id == vehicle_id,
                Trip.status == Trip.STATUS_COMPLETED) \
        .scalar() or 0

    if total_distance == 0:
        return 0.0

    total_cost = total_fuel_cost(vehicle_id) + total_maintenance_cost(vehicle_id)
    return round(total_cost / total_distance, 2)


def fleet_utilization():
    """
    % of vehicles currently on_trip vs total fleet.
    Good headline stat for the dashboard.
    """
    total = db.session.query(db.func.count(Vehicle.id)).scalar() or 0
    if total == 0:
        return 0.0

    on_trip = db.session.query(db.func.count(Vehicle.id)) \
        .filter(Vehicle.status == Vehicle.STATUS_ON_TRIP) \
        .scalar() or 0

    return round((on_trip / total) * 100, 1)