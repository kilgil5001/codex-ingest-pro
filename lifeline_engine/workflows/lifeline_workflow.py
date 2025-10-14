"""Temporal workflow orchestrating the LifeLine Engine MVP."""
from __future__ import annotations

from typing import Dict

from temporalio import workflow

from lifeline_engine.activities import compliance, delivery, design, learning, market, site_analyzer
from lifeline_engine.models.domain import (
    AddressPayload,
    ConstraintLayer,
    DeliverablePackage,
    ExecutionMetadata,
    FeedbackPayload,
    MarketSnapshot,
    ProformaResult,
    RevenueModel,
    SpaceProgram,
)
from lifeline_engine.services.notifications import build_notification_payload


@workflow.defn(name="lifeline_engine.main")
class LifeLineWorkflow:
    """Main workflow mapping directly to the architecture execution tree."""

    def __init__(self) -> None:
        self.workflow_id: str = workflow.info().workflow_id

    @workflow.run
    async def run(self, raw_address: str, requirements: Dict[str, str]) -> ExecutionMetadata:
        payload: AddressPayload = await workflow.execute_activity(
            site_analyzer.normalize_address,
            raw_address,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )

        payload = await workflow.execute_activity(
            site_analyzer.geocode_address,
            payload,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        payload = await workflow.execute_activity(
            site_analyzer.fetch_administrative_area,
            payload,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )

        await workflow.execute_activity(
            site_analyzer.fetch_cadastral_info,
            payload,
            schedule_to_close_timeout=workflow.timedelta(minutes=10),
        )
        zoning = await workflow.execute_activity(
            site_analyzer.collect_zoning_rules,
            payload.administrative_area.code if payload.administrative_area else "",
            schedule_to_close_timeout=workflow.timedelta(minutes=10),
        )

        coverage = await workflow.execute_activity(
            compliance.calculate_coverage_ratio,
            zoning,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        far = await workflow.execute_activity(
            compliance.calculate_far,
            zoning,
            requirements.get("incentives", {}),
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        height_limit = await workflow.execute_activity(
            compliance.evaluate_height_restrictions,
            zoning,
            requirements.get("street_width_m", 20.0),
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        setbacks = await workflow.execute_activity(
            compliance.compute_setbacks,
            requirements.get("street_width_m", 20.0),
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        constraint_layer: ConstraintLayer = await workflow.execute_activity(
            compliance.build_constraint_layer,
            coverage,
            far,
            height_limit,
            setbacks,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )

        market_sales = await workflow.execute_activity(
            market.collect_sales_info,
            payload.administrative_area.code if payload.administrative_area else "",
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        transactions = await workflow.execute_activity(
            market.fetch_transaction_records,
            payload.administrative_area.code if payload.administrative_area else "",
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        lease_metrics = await workflow.execute_activity(
            market.analyze_lease_market,
            payload.administrative_area.code if payload.administrative_area else "",
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        market_snapshot: MarketSnapshot = await workflow.execute_activity(
            market.aggregate_market_snapshot,
            market_sales,
            transactions,
            lease_metrics,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )

        space_program: SpaceProgram = await workflow.execute_activity(
            design.llm_planner,
            requirements,
            constraint_layer.dict(),
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        massing = await workflow.execute_activity(
            design.massing_optimizer,
            space_program,
            constraint_layer.dict(),
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        floorplan = await workflow.execute_activity(
            design.floorplan_generator,
            space_program,
            massing,
            schedule_to_close_timeout=workflow.timedelta(minutes=10),
        )
        await workflow.execute_activity(
            design.facade_composer,
            space_program,
            massing,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        await workflow.execute_activity(
            design.parking_layout_generator,
            requirements,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        package: DeliverablePackage = await workflow.execute_activity(
            design.generate_deliverables,
            floorplan,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )

        revenue: RevenueModel = await workflow.execute_activity(
            market.build_revenue_model,
            space_program,
            market_snapshot,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        cost_breakdown = await workflow.execute_activity(
            market.estimate_cost,
            space_program,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )
        proforma: ProformaResult = await workflow.execute_activity(
            market.evaluate_feasibility,
            revenue,
            cost_breakdown,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )

        metadata: ExecutionMetadata = await workflow.execute_activity(
            delivery.publish_artifacts,
            package,
            schedule_to_close_timeout=workflow.timedelta(minutes=5),
        )

        notification = build_notification_payload(
            requirements.get("recipients", ["client@example.com"]),
            metadata.artifacts["viewer"],
        )
        await workflow.execute_activity(
            delivery.notify_client,
            notification,
            schedule_to_close_timeout=workflow.timedelta(minutes=2),
        )
        await workflow.execute_activity(
            delivery.emit_metrics,
            {
                "workflow_latency": 1800.0,
                "npv": proforma.npv,
                "irr": proforma.irr,
                "payback_years": proforma.payback_years,
            },
            schedule_to_close_timeout=workflow.timedelta(minutes=2),
        )
        await workflow.execute_activity(
            delivery.audit_trail,
            {"workflow_id": self.workflow_id, "payload": str(requirements)},
            schedule_to_close_timeout=workflow.timedelta(minutes=2),
        )

        return metadata

    @workflow.signal
    async def submit_feedback(self, feedback: FeedbackPayload) -> None:
        processed = await workflow.execute_activity(
            learning.capture_feedback,
            feedback,
            schedule_to_close_timeout=workflow.timedelta(minutes=2),
        )
        await workflow.execute_activity(
            learning.feedback_nlp,
            processed,
            schedule_to_close_timeout=workflow.timedelta(minutes=2),
        )

    @workflow.query
    def latest_status(self) -> Dict[str, str]:
        return {"workflow_id": self.workflow_id, "status": "processing"}
