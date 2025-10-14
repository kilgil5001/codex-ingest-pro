"""Delivery, notification, and observability activities."""
from __future__ import annotations

from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import DeliverablePackage, ExecutionMetadata, NotificationPayload


@activity.defn(name="publish_artifacts")
async def publish_artifacts(package: DeliverablePackage) -> ExecutionMetadata:
    return ExecutionMetadata(
        workflow_id="workflow-demo",
        status="delivered",
        metrics={"generation_seconds": 1800.0},
        artifacts={
            "ifc": package.ifc_path,
            "pdf": package.pdf_path,
            "viewer": str(package.viewer_url),
        },
    )


@activity.defn(name="notify_client")
async def notify_client(payload: NotificationPayload) -> Dict[str, str]:
    return {"notified": ",".join(payload.channels)}


@activity.defn(name="emit_metrics")
async def emit_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
    metrics.setdefault("workflow_latency", 0.0)
    metrics.setdefault("model_latency", 0.0)
    return metrics


@activity.defn(name="audit_trail")
async def audit_trail(audit_payload: Dict[str, str]) -> Dict[str, str]:
    return {**audit_payload, "retention": "7y"}
