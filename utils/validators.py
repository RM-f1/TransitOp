
from models import Vehicle, Driver

class ValidationError(Exception):
    """Raised when a dispatch rule is violated. str(e) is demo/user-facing."""
    pass

def validate_cargo_capacity(vehicle, cargo_weight_kg):
    """Cargo weight must not exceed the vehicle's rated capacity."""
    if cargo_weight_kg is None or cargo_weight_kg < 0:
        raise ValidationError("Cargo weight must be a non-negative number.")

    if cargo_weight_kg > vehicle.capacity_kg:
        raise ValidationError(
            f"Cargo weight ({cargo_weight_kg} kg) exceeds "
            f"{vehicle.vehicle_number}'s capacity ({vehicle.capacity_kg} kg)."
        )
    return True


def validate_vehicle_available(vehicle):
    """Vehicle must be status == available (not on_trip/maintenance/inactive)."""
    if not vehicle.is_available():
        raise ValidationError(
            f"{vehicle.vehicle_number} is not available "
            f"(current status: {vehicle.status})."
        )
    return True


def validate_driver_available(driver):
    """Driver must be status == available (not on_trip/off_duty)."""
    if not driver.is_available():
        raise ValidationError(
            f"{driver.name} is not available "
            f"(current status: {driver.status})."
        )
    return True


def validate_driver_license(driver, on_date=None):
    """Driver's license must not be expired as of on_date (default: today)."""
    if not driver.is_license_valid(on_date=on_date):
        raise ValidationError(
            f"{driver.name}'s license (#{driver.license_number}) expired "
            f"on {driver.license_expiry.isoformat()}."
        )
    return True


def validate_trip_transition(trip, new_status):
    """New status must be a legal transition per Trip.VALID_TRANSITIONS."""
    if not trip.can_transition_to(new_status):
        raise ValidationError(
            f"Cannot transition trip #{trip.id} from "
            f"'{trip.status}' to '{new_status}'."
        )
    return True


def validate_new_trip(vehicle, driver, cargo_weight_kg):
    
    validate_cargo_capacity(vehicle, cargo_weight_kg)
    validate_vehicle_available(vehicle)
    validate_driver_available(driver)
    validate_driver_license(driver)
    return True