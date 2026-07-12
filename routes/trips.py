
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required

from models import db, Vehicle, Driver, Trip
from utils.validators import (
    ValidationError,
    validate_new_trip,
    validate_trip_transition,
)

trips_bp = Blueprint("trips", __name__)


@trips_bp.route("/trips")
@login_required
def list_trips():
    trips = Trip.query.order_by(Trip.scheduled_start.desc()).all()
    return render_template("trips.html", trips=trips)


@trips_bp.route("/trips/new")
@login_required
def new_trip():
    available_vehicles = Vehicle.query.filter_by(
        status=Vehicle.STATUS_AVAILABLE
    ).all()
    available_drivers = Driver.query.filter_by(
        status=Driver.STATUS_AVAILABLE
    ).all()
    return render_template(
        "trip_form.html",
        vehicles=available_vehicles,
        drivers=available_drivers,
    )


@trips_bp.route("/trips", methods=["POST"])
@login_required
def create_trip():
    vehicle_id = request.form.get("vehicle_id", type=int)
    driver_id = request.form.get("driver_id", type=int)
    origin = request.form.get("origin", "").strip()
    destination = request.form.get("destination", "").strip()
    cargo_weight_kg = request.form.get("cargo_weight_kg", type=float)
    scheduled_start_raw = request.form.get("scheduled_start", "").strip()

    # Basic presence checks before we even touch the DB / validators
    if not all([vehicle_id, driver_id, origin, destination, scheduled_start_raw]):
        flash("All fields are required.", "danger")
        return redirect(url_for("trips.new_trip"))

    if cargo_weight_kg is None:
        flash("Cargo weight must be a number.", "danger")
        return redirect(url_for("trips.new_trip"))

    try:
        scheduled_start = datetime.fromisoformat(scheduled_start_raw)
    except ValueError:
        flash("Invalid scheduled start date/time.", "danger")
        return redirect(url_for("trips.new_trip"))

    vehicle = Vehicle.query.get(vehicle_id)
    driver = Driver.query.get(driver_id)

    if not vehicle or not driver:
        flash("Selected vehicle or driver no longer exists.", "danger")
        return redirect(url_for("trips.new_trip"))

    try:
        # Runs: cargo capacity -> vehicle available -> driver available -> license valid
        validate_new_trip(vehicle, driver, cargo_weight_kg)
    except ValidationError as e:
        flash(str(e), "danger")
        return redirect(url_for("trips.new_trip"))

    trip = Trip(
        vehicle_id=vehicle.id,
        driver_id=driver.id,
        origin=origin,
        destination=destination,
        cargo_weight_kg=cargo_weight_kg,
        scheduled_start=scheduled_start,
        status=Trip.STATUS_SCHEDULED,
    )

    # Flip vehicle + driver to on_trip so they can't be double-booked
    vehicle.status = Vehicle.STATUS_ON_TRIP
    driver.status = Driver.STATUS_ON_TRIP

    db.session.add(trip)
    db.session.commit()

    flash(
        f"Trip #{trip.id} created: {vehicle.vehicle_number} / {driver.name}, "
        f"{origin} -> {destination}.",
        "success",
    )
    return redirect(url_for("trips.list_trips"))


@trips_bp.route("/trips/<int:trip_id>/status", methods=["POST"])
@login_required
def update_trip_status(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    new_status = request.form.get("new_status", "").strip()

    if new_status not in Trip.ALL_STATUSES:
        flash(f"'{new_status}' is not a valid trip status.", "danger")
        return redirect(url_for("trips.list_trips"))

    try:
        validate_trip_transition(trip, new_status)
    except ValidationError as e:
        flash(str(e), "danger")
        return redirect(url_for("trips.list_trips"))

    trip.status = new_status

    if new_status == Trip.STATUS_IN_PROGRESS:
        trip.actual_start = datetime.utcnow()

    elif new_status in (Trip.STATUS_COMPLETED, Trip.STATUS_CANCELLED):
        trip.actual_end = datetime.utcnow()
        # Free up the vehicle and driver regardless of completed vs cancelled
        vehicle = Vehicle.query.get(trip.vehicle_id)
        driver = Driver.query.get(trip.driver_id)
        if vehicle:
            vehicle.status = Vehicle.STATUS_AVAILABLE
        if driver:
            driver.status = Driver.STATUS_AVAILABLE

    db.session.commit()

    flash(f"Trip #{trip.id} updated to '{new_status}'.", "success")
    return redirect(url_for("trips.list_trips"))