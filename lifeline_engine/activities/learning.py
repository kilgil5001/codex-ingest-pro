"""Feedback capture and continuous learning activities."""
from __future__ import annotations

from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import FeedbackPayload


@activity.defn(name="capture_feedback")
async def capture_feedback(feedback: FeedbackPayload) -> Dict[str, str]:
    return {
        "workflow_id": feedback.workflow_id,
        "tags": ",".join(feedback.tags),
        "message": feedback.message,
    }


@activity.defn(name="feedback_nlp")
async def feedback_nlp(feedback: Dict[str, str]) -> Dict[str, str]:
    return {"embedding_id": "style-vec-123", "diff_summary": "adjust circulation"}


@activity.defn(name="daily_retraining_pipeline")
async def daily_retraining_pipeline() -> Dict[str, str]:
    return {"status": "scheduled", "mlflow_run_id": "run-abc123"}


@activity.defn(name="canary_deployment")
async def canary_deployment(model_version: str) -> Dict[str, str]:
    return {"model_version": model_version, "rollout": "10_percent"}
