"""Market intelligence and proforma activities."""
from __future__ import annotations

from typing import List

from temporalio import activity

from lifeline_engine.models.domain import (
    ComparableProject,
    CostBreakdown,
    LeaseSummary,
    MarketSnapshot,
    ProformaResult,
    RevenueModel,
    SpaceProgram,
    TransactionRecord,
)
from lifeline_engine.utils import logging as log_utils
from lifeline_engine.utils.reference_data import (
    COMPARABLE_PROJECTS,
    LEASE_SUMMARY,
    TRANSACTION_HISTORY,
)


@activity.defn(name="collect_sales_info")
async def collect_sales_info(administrative_area: str) -> List[ComparableProject]:
    """Collect comparable project data for the administrative area."""

    with log_utils.activity_context("collect_sales_info", {"code": administrative_area}):
        return COMPARABLE_PROJECTS.get(administrative_area, [])


@activity.defn(name="fetch_transaction_records")
async def fetch_transaction_records(administrative_area: str) -> List[TransactionRecord]:
    """Fetch recent transaction history."""

    with log_utils.activity_context("fetch_transaction_records", {"code": administrative_area}):
        return TRANSACTION_HISTORY.get(administrative_area, [])


@activity.defn(name="analyze_lease_market")
async def analyze_lease_market(administrative_area: str) -> LeaseSummary:
    """Return lease market summary metrics."""

    with log_utils.activity_context("analyze_lease_market", {"code": administrative_area}):
        return LEASE_SUMMARY.get(
            administrative_area,
            LeaseSummary(cap_rate=4.0, vacancy_rate=3.5, market_temperature=0.6),
        )


@activity.defn(name="aggregate_market_snapshot")
async def aggregate_market_snapshot(
    sales: List[ComparableProject],
    transactions: List[TransactionRecord],
    lease_metrics: LeaseSummary,
) -> MarketSnapshot:
    """Aggregate market intelligence into a snapshot object."""

    with log_utils.activity_context("aggregate_market_snapshot"):
        return MarketSnapshot(
            competitive_projects=sales,
            transaction_trends=transactions,
            lease_analysis=lease_metrics,
        )


@activity.defn(name="build_revenue_model")
async def build_revenue_model(space_program: SpaceProgram, market: MarketSnapshot) -> RevenueModel:
    """Build a revenue model based on comparables and program mix."""

    with log_utils.activity_context("build_revenue_model", {"gfa": str(space_program.total_gfa)}):
        if not market.competitive_projects:
            base_price = 3.5
        else:
            base_price = sum(project.price_per_sqm * project.score for project in market.competitive_projects)
            base_price /= sum(project.score for project in market.competitive_projects)
            base_price /= 10000  # convert to million KRW/m²
        base = space_program.total_gfa * base_price
        optimistic = base * 1.07
        conservative = base * 0.92
        return RevenueModel(base=round(base, 2), optimistic=round(optimistic, 2), conservative=round(conservative, 2))


@activity.defn(name="estimate_cost")
async def estimate_cost(space_program: SpaceProgram) -> CostBreakdown:
    """Estimate cost breakdown from program distribution."""

    with log_utils.activity_context("estimate_cost"):
        hard_costs = space_program.total_gfa * 2.1
        soft_costs = hard_costs * 0.18
        contingency = hard_costs * 0.08
        financing = (hard_costs + soft_costs) * 0.04
        return CostBreakdown(
            hard_costs=round(hard_costs, 2),
            soft_costs=round(soft_costs, 2),
            contingency=round(contingency, 2),
            financing=round(financing, 2),
        )


@activity.defn(name="evaluate_feasibility")
async def evaluate_feasibility(revenue: RevenueModel, costs: CostBreakdown) -> ProformaResult:
    """Evaluate project feasibility using cash-flow heuristics."""

    with log_utils.activity_context("evaluate_feasibility"):
        npv = revenue.base - costs.total
        irr = (revenue.base / costs.total) if costs.total else 0.0
        payback = 3.5 if irr > 1.15 else 5.0
        risks = ["construction_cost_overrun", "sales_velocity"]
        return ProformaResult(
            revenue_model=revenue,
            cost_breakdown=costs,
            npv=round(npv, 2),
            irr=round(irr, 3),
            payback_years=payback,
            risks=risks,
        )
