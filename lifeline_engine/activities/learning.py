"""Feedback capture and continuous learning activities."""
from __future__ import annotations

from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import FeedbackPayload
from lifeline_engine.utils import logging as log_utils


@activity.defn(name="capture_feedback")
async def capture_feedback(feedback: FeedbackPayload) -> Dict[str, str]:
    """Capture feedback and transform into structured payload."""

    with log_utils.activity_context("capture_feedback", {"workflow": feedback.workflow_id}):
        return {
            "workflow_id": feedback.workflow_id,
            "project_id": feedback.project_id or "unknown",
            "tags": ",".join(feedback.tags),
            "message": feedback.message,
            "submitted_at": feedback.submitted_at.isoformat(),
        }


@activity.defn(name="feedback_nlp")
async def feedback_nlp(feedback: Dict[str, str]) -> Dict[str, str]:
    """Simulate NLP processing that would update the feature store."""

    with log_utils.activity_context("feedback_nlp", {"workflow": feedback["workflow_id"]}):
        embedding_id = f"style-{hash(feedback['message']) & 0xFFFF:x}"
        return {"embedding_id": embedding_id, "diff_summary": "optimize circulation"}


@activity.defn(name="daily_retraining_pipeline")
async def daily_retraining_pipeline() -> Dict[str, str]:
    """Kick off scheduled retraining (mocked)."""

    with log_utils.activity_context("daily_retraining_pipeline"):
        return {"status": "scheduled", "mlflow_run_id": "run-abc123"}


@activity.defn(name="canary_deployment")
async def canary_deployment(model_version: str) -> Dict[str, str]:
    """Deploy a canary release for the supplied model version."""

    with log_utils.activity_context("canary_deployment", {"model": model_version}):
        return {"model_version": model_version, "rollout": "10_percent"}
