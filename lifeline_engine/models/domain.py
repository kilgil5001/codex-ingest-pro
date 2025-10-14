"""Domain models shared across workflows and activities."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, constr


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AddressPayload(BaseModel):
    raw: constr(strip_whitespace=True, min_length=5)
    normalized: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    altitude: Optional[float]
    administrative_area: Optional[str]
    cadastral_id: Optional[str]
    metadata: Dict[str, str] = Field(default_factory=dict)


class ConstraintLayer(BaseModel):
    coverage_limit: float
    far_limit: float
    height_limit_m: float
    setbacks: Dict[str, float]
    geojson_reference: Optional[HttpUrl]


class MarketSnapshot(BaseModel):
    competitive_projects: List[Dict[str, str]]
    transaction_trends: List[Dict[str, float]]
    lease_analysis: Dict[str, float]


class ProformaResult(BaseModel):
    revenue_scenarios: Dict[str, float]
    total_cost: float
    npv: float
    irr: float
    risks: List[str]


class SpaceProgram(BaseModel):
    program_items: List[Dict[str, str]]
    total_gfa: float
    design_style: str


class DeliverablePackage(BaseModel):
    ifc_path: str
    dxf_path: str
    pdf_path: str
    gltf_path: str
    viewer_url: HttpUrl
    summary_report_path: str


class FeedbackPayload(BaseModel):
    workflow_id: str
    tags: List[str]
    message: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionMetadata(BaseModel):
    workflow_id: str
    status: str
    metrics: Dict[str, float]
    artifacts: Dict[str, str]


class NotificationPayload(BaseModel):
    recipients: List[str]
    subject: str
    body: str
    channels: List[str] = Field(default_factory=lambda: ["email"])


class AuditRecord(BaseModel):
    workflow_id: str
    payload_snapshot_path: str
    result_snapshot_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
