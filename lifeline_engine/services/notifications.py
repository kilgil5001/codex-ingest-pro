"""Service helpers for notifications and dashboards."""
from __future__ import annotations

from typing import Iterable

from lifeline_engine.models.domain import NotificationPayload


def build_notification_payload(recipients: Iterable[str], artifact_url: str) -> NotificationPayload:
    channels = ["email", "slack", "webpush"]
    body = f"설계 패키지가 준비되었습니다. 확인: {artifact_url}"
    return NotificationPayload(
        recipients=list(recipients),
        subject="생명결 엔진 - 설계 패키지 완료",
        body=body,
        channels=channels,
    )
