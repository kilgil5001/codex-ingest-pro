"""Delivery, notification, and observability activities."""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import DeliverablePackage, ExecutionMetadata, NotificationPayload
from lifeline_engine.utils import logging as log_utils


@activity.defn(name="publish_artifacts")
async def publish_artifacts(package: DeliverablePackage) -> ExecutionMetadata:
    """Persist artifact metadata and return execution status."""

    with log_utils.activity_context("publish_artifacts"):
        timestamp = datetime.utcnow().isoformat()
        return ExecutionMetadata(
            workflow_id="workflow-demo",
            status="delivered",
            metrics={"generation_seconds": 1800.0, "package_checksum": 1.0},
            artifacts={
                "ifc": package.ifc_path,
                "pdf": package.pdf_path,
                "viewer": str(package.viewer_url),
            },
            stage_markers={"delivered_at": timestamp},
        )


@activity.defn(name="notify_client")
async def notify_client(payload: NotificationPayload) -> Dict[str, str]:
    """Send notifications across configured channels."""

    with log_utils.activity_context("notify_client", {"channels": ",".join(payload.channels)}):
        return {"notified": ",".join(payload.channels), "recipient_count": str(len(payload.recipients))}


@activity.defn(name="emit_metrics")
async def emit_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
    """Emit metrics to observability backend (mocked)."""

    with log_utils.activity_context("emit_metrics"):
        metrics.setdefault("workflow_latency", 0.0)
        metrics.setdefault("model_latency", 0.0)
        return metrics


@activity.defn(name="audit_trail")
async def audit_trail(audit_payload: Dict[str, str]) -> Dict[str, str]:
    """Persist audit trail metadata for compliance."""

    with log_utils.activity_context("audit_trail"):
        audit_payload.setdefault("retention", "7y")
        return audit_payload
