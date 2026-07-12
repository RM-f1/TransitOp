
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


#user auth-----
class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="dispatcher")  # admin | dispatcher
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "role": self.role}

    def __repr__(self):
        return f"<User {self.username}>"


#vehicle----
class Vehicle(db.Model):
    __tablename__ = "vehicles"

    # --- status strings (exact — use these everywhere) ---
    STATUS_AVAILABLE = "available"
    STATUS_ON_TRIP = "on_trip"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_INACTIVE = "inactive"
    ALL_STATUSES = [STATUS_AVAILABLE, STATUS_ON_TRIP, STATUS_MAINTENANCE, STATUS_INACTIVE]

    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g. "Van-05"
    vehicle_type = db.Column(db.String(50), nullable=False)  # van, truck, bike, etc.
    capacity_kg = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_AVAILABLE, index=True)
    odometer_km = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trips = db.relationship("Trip", backref="vehicle", lazy=True)
    maintenance_records = db.relationship("MaintenanceRecord", backref="vehicle", lazy=True)
    fuel_expenses = db.relationship("FuelExpense", backref="vehicle", lazy=True)

    @validates("capacity_kg", "odometer_km")
    def validate_positive(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value

    def is_available(self):
        return self.status == self.STATUS_AVAILABLE

    def __repr__(self):
        return f"<Vehicle {self.vehicle_number}>"

    def to_dict(self):
        return {
            "id": self.id,
            "vehicle_number": self.vehicle_number,
            "vehicle_type": self.vehicle_type,
            "capacity_kg": self.capacity_kg,
            "status": self.status,
            "odometer_km": self.odometer_km,
        }


#driver
class Driver(db.Model):
    __tablename__ = "drivers"

    STATUS_AVAILABLE = "available"
    STATUS_ON_TRIP = "on_trip"
    STATUS_OFF_DUTY = "off_duty"
    ALL_STATUSES = [STATUS_AVAILABLE, STATUS_ON_TRIP, STATUS_OFF_DUTY]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g. "Alex"
    license_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    license_class = db.Column(db.String(20), nullable=False)  # e.g. "LMV", "HMV"
    license_expiry = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, default=STATUS_AVAILABLE, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trips = db.relationship("Trip", backref="driver", lazy=True)

    def is_available(self):
        return self.status == self.STATUS_AVAILABLE

    def is_license_valid(self, on_date=None):
        on_date = on_date or datetime.utcnow().date()
        return self.license_expiry >= on_date

    def __repr__(self):
        return f"<Driver {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "license_number": self.license_number,
            "license_class": self.license_class,
            "license_expiry": self.license_expiry.isoformat() if self.license_expiry else None,
            "status": self.status,
        }



class Trip(db.Model):
    __tablename__ = "trips"

    STATUS_SCHEDULED = "scheduled"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    ALL_STATUSES = [STATUS_SCHEDULED, STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_CANCELLED]

    # allowed status transitions — routes/trips.py should check against this
    VALID_TRANSITIONS = {
        STATUS_SCHEDULED: [STATUS_IN_PROGRESS, STATUS_CANCELLED],
        STATUS_IN_PROGRESS: [STATUS_COMPLETED, STATUS_CANCELLED],
        STATUS_COMPLETED: [],
        STATUS_CANCELLED: [],
    }

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey("drivers.id"), nullable=False)

    origin = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    cargo_weight_kg = db.Column(db.Float, nullable=False, default=0.0)
    distance_km = db.Column(db.Float)

    status = db.Column(db.String(20), nullable=False, default=STATUS_SCHEDULED, index=True)
    scheduled_start = db.Column(db.DateTime, nullable=False, index=True)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fuel_expenses = db.relationship("FuelExpense", backref="trip", lazy=True)

    @validates("cargo_weight_kg", "distance_km")
    def validate_positive(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value

    def can_transition_to(self, new_status):
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])

    def __repr__(self):
        return f"<Trip {self.id}: {self.origin} -> {self.destination}>"

    def to_dict(self):
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "driver_id": self.driver_id,
            "origin": self.origin,
            "destination": self.destination,
            "cargo_weight_kg": self.cargo_weight_kg,
            "distance_km": self.distance_km,
            "status": self.status,
            "scheduled_start": self.scheduled_start.isoformat() if self.scheduled_start else None,
            "actual_start": self.actual_start.isoformat() if self.actual_start else None,
            "actual_end": self.actual_end.isoformat() if self.actual_end else None,
        }



# MaintenanceRecord

class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_records"

    STATUS_SCHEDULED = "scheduled"
    STATUS_COMPLETED = "completed"
    ALL_STATUSES = [STATUS_SCHEDULED, STATUS_COMPLETED]

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    date = db.Column(db.Date, nullable=False, index=True)
    odometer_km = db.Column(db.Float)
    status = db.Column(db.String(20), nullable=False, default=STATUS_SCHEDULED)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates("cost", "odometer_km")
    def validate_positive(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value

    def __repr__(self):
        return f"<Maintenance {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "description": self.description,
            "cost": self.cost,
            "date": self.date.isoformat() if self.date else None,
            "odometer_km": self.odometer_km,
            "status": self.status,
        }



# FuelExpense

class FuelExpense(db.Model):
    __tablename__ = "fuel_expenses"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=True)  # nullable: fuel not always tied to a trip
    liters = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    odometer_km = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates("liters", "cost", "odometer_km")
    def validate_positive(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value

    @property
    def cost_per_liter(self):
        return round(self.cost / self.liters, 2) if self.liters else 0

    def __repr__(self):
        return f"<FuelExpense {self.id}>"

    def to_dict(self):
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "trip_id": self.trip_id,
            "liters": self.liters,
            "cost": self.cost,
            "date": self.date.isoformat() if self.date else None,
            "odometer_km": self.odometer_km,
        }