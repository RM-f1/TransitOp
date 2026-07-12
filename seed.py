import os
from datetime import datetime, date, timedelta
from flask import Flask

# Ensure all models are imported
from models import db, User, Vehicle, Driver, MaintenanceRecord, FuelExpense

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)

app = Flask(__name__)
# Using the absolute path to the database to prevent path-related errors
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(INSTANCE_DIR, 'transitops.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def seed():
    with app.app_context():
        print("Dropping and recreating all tables...")
        db.drop_all()
        db.create_all()

        # Add Users
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")

        dispatcher = User(username="dispatcher", role="dispatcher")
        dispatcher.set_password("dispatch123")

        db.session.add_all([admin, dispatcher])

        # Add Vehicles
        van05 = Vehicle(
            vehicle_number="Van-05", vehicle_type="van", capacity_kg=500,
            status=Vehicle.STATUS_AVAILABLE, odometer_km=18250,
        )
        truck01 = Vehicle(
            vehicle_number="Truck-01", vehicle_type="truck", capacity_kg=2000,
            status=Vehicle.STATUS_AVAILABLE, odometer_km=54210,
        )
        bike02 = Vehicle(
            vehicle_number="Bike-02", vehicle_type="bike", capacity_kg=25,
            status=Vehicle.STATUS_AVAILABLE, odometer_km=6120,
        )
        van07 = Vehicle(
            vehicle_number="Van-07", vehicle_type="van", capacity_kg=500,
            status=Vehicle.STATUS_MAINTENANCE, odometer_km=41030,
        )
        db.session.add_all([van05, truck01, bike02, van07])
        db.session.flush() 

        # Add Driver
        alex = Driver(
            name="Alex",
            license_number="DL-LMV-10231",
            license_class="LMV",
            license_expiry=date.today() + timedelta(days=365),
            phone="9876500001",
            status=Driver.STATUS_AVAILABLE,
        )
        db.session.add(alex)
        db.session.flush() 

        # Add Maintenance Records
        maint1 = MaintenanceRecord(
            vehicle_id=van07.id, description="Brake pad replacement + oil change",
            cost=4500, date=date.today() - timedelta(days=1),
            odometer_km=41030, status=MaintenanceRecord.STATUS_SCHEDULED,
        )
        maint2 = MaintenanceRecord(
            vehicle_id=truck01.id, description="Routine service",
            cost=6200, date=date.today() - timedelta(days=20),
            odometer_km=53800, status=MaintenanceRecord.STATUS_COMPLETED,
        )
        db.session.add_all([maint1, maint2])

        # Add Fuel Expenses
        fuel1 = FuelExpense(vehicle_id=van05.id, liters=18, cost=1710, date=date.today() - timedelta(days=2), odometer_km=18200)
        fuel2 = FuelExpense(vehicle_id=truck01.id, liters=45, cost=4275, date=date.today(), odometer_km=54210)
        fuel3 = FuelExpense(vehicle_id=bike02.id, liters=3, cost=285, date=date.today(), odometer_km=6120)
        db.session.add_all([fuel1, fuel2, fuel3])

        db.session.commit()

        print("Seed complete.")
        print(f"Users: {User.query.count()}")
        print(f"Vehicles: {Vehicle.query.count()}")
        print(f"Drivers: {Driver.query.count()}")
        print("Login test accounts: admin/admin123, dispatcher/dispatch123")

if __name__ == "__main__":
    seed()