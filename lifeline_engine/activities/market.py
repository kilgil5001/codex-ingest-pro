"""Market intelligence and proforma activities."""
from __future__ import annotations

from typing import Dict, List

from temporalio import activity

from lifeline_engine.models.domain import MarketSnapshot, ProformaResult


@activity.defn(name="collect_sales_info")
async def collect_sales_info(administrative_area: str) -> List[Dict[str, str]]:
    return [
        {
            "project": "Sunrise Towers",
            "distance_km": "0.8",
            "price_per_sqm": "4200000",
            "status": "on_sale",
        }
    ]


@activity.defn(name="fetch_transaction_records")
async def fetch_transaction_records(administrative_area: str) -> List[Dict[str, float]]:
    return [
        {"month": "2024-01", "avg_price": 3.9, "transactions": 25},
        {"month": "2024-02", "avg_price": 4.1, "transactions": 28},
    ]


@activity.defn(name="analyze_lease_market")
async def analyze_lease_market(administrative_area: str) -> Dict[str, float]:
    return {"cap_rate": 4.5, "vacancy_rate": 3.2, "market_temperature": 0.65}


@activity.defn(name="aggregate_market_snapshot")
async def aggregate_market_snapshot(
    sales: List[Dict[str, str]],
    transactions: List[Dict[str, float]],
    lease_metrics: Dict[str, float],
) -> MarketSnapshot:
    return MarketSnapshot(
        competitive_projects=sales,
        transaction_trends=transactions,
        lease_analysis=lease_metrics,
    )


@activity.defn(name="build_revenue_model")
async def build_revenue_model(space_program: Dict[str, str], market: MarketSnapshot) -> Dict[str, float]:
    base = sum(float(item.get("area", 0)) * 4.2 for item in market.competitive_projects)
    return {
        "base": base,
        "optimistic": base * 1.05,
        "conservative": base * 0.9,
    }


@activity.defn(name="estimate_cost")
async def estimate_cost(space_program: Dict[str, str]) -> float:
    structure_cost = float(space_program.get("structure_cost", 0))
    finish_cost = float(space_program.get("finish_cost", 0))
    systems_cost = float(space_program.get("systems_cost", 0))
    return structure_cost + finish_cost + systems_cost


@activity.defn(name="evaluate_feasibility")
async def evaluate_feasibility(
    revenue: Dict[str, float],
    total_cost: float,
) -> ProformaResult:
    base_revenue = revenue.get("base", 0.0)
    npv = base_revenue - total_cost
    irr = (base_revenue / total_cost) if total_cost else 0.0
    return ProformaResult(
        revenue_scenarios=revenue,
        total_cost=total_cost,
        npv=npv,
        irr=irr,
        risks=["construction_cost_overrun", "sales_velocity"],
    )
