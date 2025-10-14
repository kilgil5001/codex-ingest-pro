"""Temporal worker bootstrapper for LifeLine Engine."""
from __future__ import annotations

import asyncio
from typing import Sequence

from temporalio.client import Client
from temporalio.worker import Worker

from lifeline_engine.activities import compliance, delivery, design, learning, market, site_analyzer
from lifeline_engine.config import get_settings
from lifeline_engine.workflows.lifeline_workflow import LifeLineWorkflow


async def run_worker(task_queue: str = "lifeline-engine") -> None:
    settings = get_settings()
    client = await Client.connect(settings.temporal_address)
    activities: Sequence[object] = [
        site_analyzer.normalize_address,
        site_analyzer.geocode_address,
        site_analyzer.fetch_administrative_area,
        site_analyzer.fetch_cadastral_info,
        site_analyzer.collect_zoning_rules,
        compliance.calculate_coverage_ratio,
        compliance.calculate_far,
        compliance.evaluate_height_restrictions,
        compliance.compute_setbacks,
        compliance.build_constraint_layer,
        market.collect_sales_info,
        market.fetch_transaction_records,
        market.analyze_lease_market,
        market.aggregate_market_snapshot,
        market.build_revenue_model,
        market.estimate_cost,
        market.evaluate_feasibility,
        design.llm_planner,
        design.massing_optimizer,
        design.floorplan_generator,
        design.facade_composer,
        design.parking_layout_generator,
        design.generate_deliverables,
        delivery.publish_artifacts,
        delivery.notify_client,
        delivery.emit_metrics,
        delivery.audit_trail,
        learning.capture_feedback,
        learning.feedback_nlp,
        learning.daily_retraining_pipeline,
        learning.canary_deployment,
    ]
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[LifeLineWorkflow],
        activities=activities,
    )
    await worker.run()


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
