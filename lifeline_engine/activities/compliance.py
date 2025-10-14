"""Activities computing regulatory constraints."""
from __future__ import annotations

import math
from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import ConstraintLayer


@activity.defn(name="calculate_coverage_ratio")
async def calculate_coverage_ratio(zoning_payload: Dict[str, str]) -> float:
    base_ratio = float(zoning_payload.get("coverage", 0.6))
    special_district = zoning_payload.get("special_district")
    if special_district == "commercial-core":
        base_ratio += 0.1
    return min(base_ratio, 0.9)


@activity.defn(name="calculate_far")
async def calculate_far(zoning_payload: Dict[str, str], incentives: Dict[str, bool]) -> float:
    far = float(zoning_payload.get("far", 2.5))
    if incentives.get("public_contribution"):
        far *= 1.1
    if incentives.get("green_building"):
        far *= 1.05
    return min(far, 6.0)


@activity.defn(name="evaluate_height_restrictions")
async def evaluate_height_restrictions(zoning_payload: Dict[str, str], street_width_m: float) -> float:
    base_limit = float(zoning_payload.get("height_limit", 35))
    daylight_envelope = street_width_m * 1.5
    return min(base_limit, daylight_envelope)


@activity.defn(name="compute_setbacks")
async def compute_setbacks(street_width_m: float) -> Dict[str, float]:
    front = max(3.0, street_width_m * 0.1)
    side = 1.5
    rear = 2.0
    return {"front": front, "side": side, "rear": rear}


@activity.defn(name="build_constraint_layer")
async def build_constraint_layer(
    coverage: float,
    far: float,
    height_limit: float,
    setbacks: Dict[str, float],
) -> ConstraintLayer:
    return ConstraintLayer(
        coverage_limit=coverage,
        far_limit=far,
        height_limit_m=height_limit,
        setbacks=setbacks,
        geojson_reference=None,
    )
