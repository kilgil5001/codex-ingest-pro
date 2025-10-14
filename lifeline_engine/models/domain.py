"""Domain models shared across workflows and activities."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


class ConfidenceLevel(str, Enum):
    """Qualitative indicator for upstream data quality."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GeoCoordinate(BaseModel):
    """Represents a geospatial coordinate in the WGS84 reference frame."""

    latitude: float
    longitude: float
    altitude: Optional[float] = None
    srid: int = 4326


class AdministrativeArea(BaseModel):
    """Administrative metadata for permitting and regulatory lookup."""

    code: str
    name: str
    permit_office: str
    inspector_profile: Dict[str, Any] = Field(default_factory=dict)


class CadastralParcel(BaseModel):
    """Cadastral parcel information sourced from public APIs."""

    parcel_id: str
    area_sqm: float
    ownership: str
    boundary_geojson: str
    adjacent_roads: List[str] = Field(default_factory=list)


class SetbackOverrides(BaseModel):
    """Optional overrides for computed setbacks per zoning rule."""

    front: Optional[float] = None
    side: Optional[float] = None
    rear: Optional[float] = None


class ZoningRuleset(BaseModel):
    """Aggregated zoning rules applied to the site."""

    land_use: str
    special_district: Optional[str]
    far: float
    coverage: float
    height_limit: float
    setback_overrides: SetbackOverrides = Field(default_factory=SetbackOverrides)


class AddressPayload(BaseModel):
    """Transport object for the site analysis stages."""

    raw: constr(strip_whitespace=True, min_length=5)
    normalized: Optional[str] = None
    coordinate: Optional[GeoCoordinate] = None
    administrative_area: Optional[AdministrativeArea] = None
    cadastral: Optional[CadastralParcel] = None
    zoning_rules: Optional[ZoningRuleset] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConstraintLayer(BaseModel):
    """Normalized constraint payload consumed by design services."""

    coverage_limit: float
    far_limit: float
    height_limit_m: float
    setbacks: Dict[str, float]
    geojson_reference: Optional[str] = None


class ComparableProject(BaseModel):
    """Comparable project used for competitive market analysis."""

    name: str
    distance_km: float
    price_per_sqm: float
    status: str
    score: float
    launched_at: Optional[str] = None


class TransactionRecord(BaseModel):
    """Historical transaction metrics."""

    month: str
    avg_price: float
    transactions: int


class LeaseSummary(BaseModel):
    """Key lease market indicators."""

    cap_rate: float
    vacancy_rate: float
    market_temperature: float


class MarketSnapshot(BaseModel):
    """Market intelligence summary consumed by business analysis."""

    competitive_projects: List[ComparableProject]
    transaction_trends: List[TransactionRecord]
    lease_analysis: LeaseSummary


class RevenueModel(BaseModel):
    """Revenue model across scenarios."""

    base: float
    optimistic: float
    conservative: float


class CostBreakdown(BaseModel):
    """Cost breakdown for project delivery."""

    hard_costs: float
    soft_costs: float
    contingency: float
    financing: float

    @property
    def total(self) -> float:
        return self.hard_costs + self.soft_costs + self.contingency + self.financing


class ProformaResult(BaseModel):
    """Proforma evaluation output."""

    revenue_model: RevenueModel
    cost_breakdown: CostBreakdown
    npv: float
    irr: float
    payback_years: float
    risks: List[str]


class SpaceProgramItem(BaseModel):
    """Represents a single program element within the building."""

    name: str
    area_sqm: float
    priority: str
    floor_range: str


class SpaceProgram(BaseModel):
    """Structured program definition produced by the planner."""

    program_items: List[SpaceProgramItem]
    total_gfa: float
    design_style: str


class MassingSolution(BaseModel):
    """Summarizes massing optimization results."""

    max_height: float
    envelopes: List[Dict[str, Any]]
    sunlight_score: float


class FloorplanArtifacts(BaseModel):
    """Artifacts generated during floorplan synthesis."""

    ifc_path: str
    svg_path: str
    levels: List[str]
    core_positions: List[Dict[str, float]]


class ParkingLayout(BaseModel):
    """Parking layout summary."""

    required_stalls: int
    efficiency: float
    layout_svg: str


class DeliverablePackage(BaseModel):
    """Bundle of deliverables uploaded to object storage."""

    ifc_path: str
    dxf_path: str
    pdf_path: str
    gltf_path: str
    viewer_url: HttpUrl
    summary_report_path: str
    checksum: Optional[str] = None


class FeedbackPayload(BaseModel):
    """Feedback submitted by architects after reviewing outputs."""

    workflow_id: str
    project_id: Optional[str]
    tags: List[str]
    message: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionMetadata(BaseModel):
    """Execution metadata recorded at the end of the workflow."""

    workflow_id: str
    status: str
    metrics: Dict[str, float]
    artifacts: Dict[str, str]
    stage_markers: Dict[str, str] = Field(default_factory=dict)


class NotificationPayload(BaseModel):
    """Notification delivery contract."""

    recipients: List[str]
    subject: str
    body: str
    channels: List[str] = Field(default_factory=lambda: ["email"])


class AuditRecord(BaseModel):
    """Audit log entry persisted for compliance."""

    workflow_id: str
    payload_snapshot_path: str
    result_snapshot_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
