"""Service helpers for notifications and dashboards."""
from __future__ import annotations

from typing import Iterable, List

from lifeline_engine.models.domain import NotificationPayload


def _default_channels() -> List[str]:
    return ["email", "slack", "webpush"]


def build_notification_payload(recipients: Iterable[str], artifact_url: str) -> NotificationPayload:
    channels = _default_channels()
    body = "\n".join(
        [
            "생명결 엔진 설계 패키지가 준비되었습니다.",
            f"바로 확인하기: {artifact_url}",
            "파트너 추천과 사업성 지표는 대시보드에서 실시간 갱신됩니다.",
        ]
    )
    return NotificationPayload(
        recipients=list(recipients),
        subject="생명결 엔진 - 설계 패키지 완료",
        body=body,
        channels=channels,
    )
