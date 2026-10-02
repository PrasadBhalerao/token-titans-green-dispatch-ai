from __future__ import annotations

from typing import Any


def calculate_fuel_liters(
    distance_km: float,
    fuel_rate_l_per_100km: float,
    idle_minutes: float = 0,
    idle_fuel_l_per_hour: float = 0,
) -> float:
    driving_fuel = distance_km * fuel_rate_l_per_100km / 100
    idle_fuel = idle_minutes * idle_fuel_l_per_hour / 60
    return driving_fuel + idle_fuel


def calculate_energy_kwh(
    distance_km: float,
    energy_rate_kwh_per_100km: float,
    idle_minutes: float = 0,
    idle_energy_kwh_per_hour: float = 0,
) -> float:
    driving_energy = distance_km * energy_rate_kwh_per_100km / 100
    idle_energy = idle_minutes * idle_energy_kwh_per_hour / 60
    return driving_energy + idle_energy


def calculate_co2e(consumption: float, co2e_factor: float) -> float:
    return consumption * co2e_factor


def calculate_route_energy_and_emissions(route: dict[str, Any], vehicle: dict[str, Any]) -> dict[str, float]:
    distance_km = float(route.get("total_distance_km", 0))
    idle_minutes = float(route.get("idle_minutes", 0))
    co2e_factor = float(vehicle.get("co2e_factor", 0))
    energy_type = str(vehicle.get("energy_type", "")).lower()

    if energy_type == "electric":
        energy_kwh = calculate_energy_kwh(
            distance_km=distance_km,
            energy_rate_kwh_per_100km=float(vehicle.get("energy_rate_kwh_per_100km", 0)),
            idle_minutes=idle_minutes,
            idle_energy_kwh_per_hour=float(vehicle.get("idle_energy_kwh_per_hour", 0)),
        )
        return {
            "fuel_liters": 0.0,
            "energy_kwh": energy_kwh,
            "co2e_kg": calculate_co2e(energy_kwh, co2e_factor),
        }

    fuel_liters = calculate_fuel_liters(
        distance_km=distance_km,
        fuel_rate_l_per_100km=float(vehicle.get("fuel_rate_l_per_100km", 0)),
        idle_minutes=idle_minutes,
        idle_fuel_l_per_hour=float(vehicle.get("idle_fuel_l_per_hour", 0)),
    )
    return {
        "fuel_liters": fuel_liters,
        "energy_kwh": 0.0,
        "co2e_kg": calculate_co2e(fuel_liters, co2e_factor),
    }
