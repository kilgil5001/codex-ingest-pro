"""Structural tests ensuring workflow wiring matches architecture tree."""
from __future__ import annotations

import inspect

from lifeline_engine.workflows.lifeline_workflow import LifeLineWorkflow


def test_workflow_has_run_method() -> None:
    assert inspect.iscoroutinefunction(LifeLineWorkflow.run)


def test_workflow_has_feedback_signal() -> None:
    assert hasattr(LifeLineWorkflow, "submit_feedback")
    assert inspect.iscoroutinefunction(LifeLineWorkflow.submit_feedback)


def test_workflow_has_status_query() -> None:
    assert callable(LifeLineWorkflow.latest_status)
