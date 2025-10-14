"""Activities computing regulatory constraints."""
from __future__ import annotations

from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import ConstraintLayer
from lifeline_engine.utils import logging as log_utils


@activity.defn(name="calculate_coverage_ratio")
async def calculate_coverage_ratio(zoning_payload: Dict[str, str]) -> float:
    """Calculate the coverage ratio with adjustments for special districts."""

    with log_utils.activity_context("calculate_coverage_ratio", {"payload": str(zoning_payload)}):
        base_ratio = float(zoning_payload.get("coverage", 0.6))
        if zoning_payload.get("special_district") == "commercial-core":
            base_ratio += 0.05
        elif zoning_payload.get("special_district") == "tourism":
            base_ratio += 0.02
        return min(base_ratio, 0.9)


@activity.defn(name="calculate_far")
async def calculate_far(zoning_payload: Dict[str, str], incentives: Dict[str, bool]) -> float:
    """Determine FAR with incentive multipliers."""

    with log_utils.activity_context("calculate_far", {"incentives": str(incentives)}):
        far = float(zoning_payload.get("far", 3.0))
        if incentives.get("public_contribution"):
            far *= 1.1
        if incentives.get("green_building"):
            far *= 1.05
        return min(far, 9.0)


@activity.defn(name="evaluate_height_restrictions")
async def evaluate_height_restrictions(zoning_payload: Dict[str, str], street_width_m: float) -> float:
    """Evaluate maximum building height considering street-width envelope."""

    with log_utils.activity_context("evaluate_height_restrictions", {"street_width": str(street_width_m)}):
        base_limit = float(zoning_payload.get("height_limit", 35))
        daylight_envelope = street_width_m * 1.5
        scenic_cap = 120.0 if zoning_payload.get("special_district") == "tourism" else 999
        return min(base_limit, daylight_envelope, scenic_cap)


@activity.defn(name="compute_setbacks")
async def compute_setbacks(street_width_m: float) -> Dict[str, float]:
    """Compute front/side/rear setbacks based on street width."""

    with log_utils.activity_context("compute_setbacks", {"street_width": str(street_width_m)}):
        front = max(3.0, street_width_m * 0.1)
        side = 1.5 if street_width_m >= 10 else 1.2
        rear = 2.5
        return {"front": round(front, 2), "side": round(side, 2), "rear": rear}


@activity.defn(name="build_constraint_layer")
async def build_constraint_layer(
    coverage: float,
    far: float,
    height_limit: float,
    setbacks: Dict[str, float],
) -> ConstraintLayer:
    """Build a constraint layer object consumed by downstream services."""

    with log_utils.activity_context("build_constraint_layer"):
        return ConstraintLayer(
            coverage_limit=coverage,
            far_limit=far,
            height_limit_m=height_limit,
            setbacks=setbacks,
            geojson_reference=None,
        )
