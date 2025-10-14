"""Design generation activities."""
from __future__ import annotations

import json
from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import DeliverablePackage, SpaceProgram


@activity.defn(name="llm_planner")
async def llm_planner(requirements: Dict[str, str], constraint_layer: Dict[str, float]) -> SpaceProgram:
    program_items = [
        {"name": "Residential Unit", "area": "85", "priority": "high"},
        {"name": "Parking", "area": "120", "priority": "medium"},
    ]
    return SpaceProgram(program_items=program_items, total_gfa=205.0, design_style=requirements.get("style", "modern"))


@activity.defn(name="massing_optimizer")
async def massing_optimizer(space_program: SpaceProgram, constraint_layer: Dict[str, float]) -> Dict[str, str]:
    return {
        "gfa": str(space_program.total_gfa),
        "height": str(constraint_layer.get("height_limit_m", 35.0) * 0.9),
        "sunlight_score": "0.82",
    }


@activity.defn(name="floorplan_generator")
async def floorplan_generator(space_program: SpaceProgram, massing: Dict[str, str]) -> Dict[str, str]:
    return {
        "svg_path": "s3://designs/floorplan.svg",
        "ifc_path": "s3://designs/model.ifc",
        "core_positions": json.dumps([{"x": 5, "y": 10}]),
    }


@activity.defn(name="facade_composer")
async def facade_composer(space_program: SpaceProgram, massing: Dict[str, str]) -> Dict[str, str]:
    return {
        "facade_pattern": "parametric_grid",
        "glazing_ratio": "0.55",
    }


@activity.defn(name="parking_layout_generator")
async def parking_layout_generator(requirements: Dict[str, str]) -> Dict[str, str]:
    return {
        "required_stalls": requirements.get("required_stalls", "42"),
        "layout_svg": "s3://designs/parking.svg",
    }


@activity.defn(name="generate_deliverables")
async def generate_deliverables(design_artifacts: Dict[str, str]) -> DeliverablePackage:
    return DeliverablePackage(
        ifc_path=design_artifacts["ifc_path"],
        dxf_path="s3://designs/floorplan.dxf",
        pdf_path="s3://designs/package.pdf",
        gltf_path="s3://designs/model.gltf",
        viewer_url="https://viewer.lifeline.engine/projects/demo",
        summary_report_path="s3://designs/summary.pdf",
    )
