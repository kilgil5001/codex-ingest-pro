"""Design generation activities."""
from __future__ import annotations

from typing import Dict, List

from temporalio import activity

from lifeline_engine.models.domain import (
    ConstraintLayer,
    DeliverablePackage,
    FloorplanArtifacts,
    MassingSolution,
    ParkingLayout,
    SpaceProgram,
    SpaceProgramItem,
)
from lifeline_engine.utils import logging as log_utils


def _program_for_requirements(requirements: Dict[str, str], constraint: ConstraintLayer) -> List[SpaceProgramItem]:
    base_program = [
        SpaceProgramItem(name="Residential Unit", area_sqm=85.0, priority="high", floor_range="2-15"),
        SpaceProgramItem(name="Parking", area_sqm=constraint.setbacks.get("front", 3.0) * 20, priority="medium", floor_range="B1"),
        SpaceProgramItem(name="Commercial Podium", area_sqm=450.0, priority="high", floor_range="1"),
    ]
    if requirements.get("amenities") == "premium":
        base_program.append(
            SpaceProgramItem(name="Sky Lounge", area_sqm=180.0, priority="medium", floor_range="16")
        )
    return base_program


@activity.defn(name="llm_planner")
async def llm_planner(requirements: Dict[str, str], constraint_layer: Dict[str, float]) -> SpaceProgram:
    """Plan programmatic distribution leveraging constraint inputs."""

    constraint = ConstraintLayer(**constraint_layer)
    with log_utils.activity_context("llm_planner", {"style": requirements.get("style", "modern")}):
        items = _program_for_requirements(requirements, constraint)
        total_gfa = sum(item.area_sqm for item in items)
        return SpaceProgram(program_items=items, total_gfa=round(total_gfa, 2), design_style=requirements.get("style", "modern"))


@activity.defn(name="massing_optimizer")
async def massing_optimizer(space_program: SpaceProgram, constraint_layer: Dict[str, float]) -> MassingSolution:
    """Perform simplified massing optimization with envelope checks."""

    constraint = ConstraintLayer(**constraint_layer)
    with log_utils.activity_context("massing_optimizer", {"gfa": str(space_program.total_gfa)}):
        base_height = min(constraint.height_limit_m, (space_program.total_gfa / 120.0) * 3)
        sunlight_score = min(0.95, 0.75 + constraint.coverage_limit * 0.2)
        envelopes = [
            {"level": "podium", "height": 12.0},
            {"level": "tower", "height": round(base_height, 2)},
        ]
        return MassingSolution(max_height=round(base_height, 2), envelopes=envelopes, sunlight_score=round(sunlight_score, 2))


@activity.defn(name="floorplan_generator")
async def floorplan_generator(space_program: SpaceProgram, massing: MassingSolution) -> FloorplanArtifacts:
    """Generate floorplan artifacts with deterministic paths."""

    with log_utils.activity_context("floorplan_generator"):
        levels = ["B1", "1F", "2F-15F", "RF"]
        core_positions = [{"x": 6.2, "y": 11.5}, {"x": 18.4, "y": 11.5}]
        return FloorplanArtifacts(
            ifc_path="s3://lifeline/projects/demo/model.ifc",
            svg_path="s3://lifeline/projects/demo/floorplan.svg",
            levels=levels,
            core_positions=core_positions,
        )


@activity.defn(name="facade_composer")
async def facade_composer(space_program: SpaceProgram, massing: MassingSolution) -> Dict[str, str]:
    """Compose facade strategy derived from style and massing."""

    with log_utils.activity_context("facade_composer", {"style": space_program.design_style}):
        glazing_ratio = 0.5 if space_program.design_style == "modern" else 0.45
        return {
            "facade_pattern": "parametric_grid" if massing.sunlight_score > 0.8 else "vertical_fins",
            "glazing_ratio": f"{glazing_ratio:.2f}",
        }


@activity.defn(name="parking_layout_generator")
async def parking_layout_generator(requirements: Dict[str, str]) -> ParkingLayout:
    """Generate parking layout summary."""

    with log_utils.activity_context("parking_layout_generator"):
        required_stalls = int(requirements.get("required_stalls", 42))
        efficiency = 0.78 if required_stalls > 50 else 0.82
        return ParkingLayout(required_stalls=required_stalls, efficiency=efficiency, layout_svg="s3://lifeline/projects/demo/parking.svg")


@activity.defn(name="generate_deliverables")
async def generate_deliverables(floorplan: FloorplanArtifacts) -> DeliverablePackage:
    """Create the final deliverable package artifacts."""

    with log_utils.activity_context("generate_deliverables", {"ifc": floorplan.ifc_path}):
        return DeliverablePackage(
            ifc_path=floorplan.ifc_path,
            dxf_path="s3://lifeline/projects/demo/floorplan.dxf",
            pdf_path="s3://lifeline/projects/demo/package.pdf",
            gltf_path="s3://lifeline/projects/demo/model.gltf",
            viewer_url="https://viewer.lifeline.engine/projects/demo",
            summary_report_path="s3://lifeline/projects/demo/summary.pdf",
            checksum="abc123",
        )
