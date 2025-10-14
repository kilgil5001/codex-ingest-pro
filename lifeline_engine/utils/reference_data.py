"""Reference datasets used to emulate integrations in tests."""
from __future__ import annotations

from typing import Dict, List

from lifeline_engine.models.domain import (
    AdministrativeArea,
    CadastralParcel,
    ComparableProject,
    LeaseSummary,
    TransactionRecord,
    ZoningRuleset,
)


ADDRESS_ALIAS = {
    "서울특별시 강남구 테헤란로 427": "서울 강남구 테헤란로 427",
    "테헤란로 427": "서울 강남구 테헤란로 427",
}

GEOCODE_INDEX = {
    "서울 강남구 테헤란로 427": (37.5035, 127.0509, 82.0),
    "부산 해운대구 APEC로 55": (35.169, 129.136, 15.5),
}

ADMINISTRATIVE_AREAS: Dict[str, AdministrativeArea] = {
    "서울 강남구 테헤란로 427": AdministrativeArea(
        code="11680",
        name="서울특별시 강남구",
        permit_office="강남구청 건축허가과",
        inspector_profile={"case_success_rate": "0.92", "notes": "상업시설 경험 많음"},
    ),
    "부산 해운대구 APEC로 55": AdministrativeArea(
        code="26290",
        name="부산광역시 해운대구",
        permit_office="해운대구청 도시디자인과",
        inspector_profile={"case_success_rate": "0.88", "notes": "관광지구 특화"},
    ),
}

CADASTRAL_INFO: Dict[str, CadastralParcel] = {
    "서울 강남구 테헤란로 427": CadastralParcel(
        parcel_id="1168010600104270000",
        area_sqm=1820.5,
        ownership="private",
        boundary_geojson="{...}",
        adjacent_roads=["테헤란로", "선릉로"],
    ),
    "부산 해운대구 APEC로 55": CadastralParcel(
        parcel_id="2629010600100550000",
        area_sqm=2205.3,
        ownership="mixed",
        boundary_geojson="{...}",
        adjacent_roads=["APEC로", "센텀남대로"],
    ),
}

ZONING_RULESETS: Dict[str, ZoningRuleset] = {
    "11680": ZoningRuleset(
        land_use="일반상업지역",
        special_district="commercial-core",
        far=8.0,
        coverage=0.7,
        height_limit=150.0,
    ),
    "26290": ZoningRuleset(
        land_use="일반상업지역",
        special_district="tourism",
        far=6.0,
        coverage=0.6,
        height_limit=120.0,
    ),
}

COMPARABLE_PROJECTS: Dict[str, List[ComparableProject]] = {
    "11680": [
        ComparableProject(
            name="테헤란 메가타워",
            distance_km=0.45,
            price_per_sqm=4650000,
            status="on_sale",
            score=0.91,
            launched_at="2024-01",
        ),
        ComparableProject(
            name="선릉 프라임센터",
            distance_km=0.7,
            price_per_sqm=4380000,
            status="completed",
            score=0.87,
            launched_at="2023-09",
        ),
    ],
    "26290": [
        ComparableProject(
            name="센텀 헤리티지",
            distance_km=0.9,
            price_per_sqm=3950000,
            status="on_sale",
            score=0.84,
            launched_at="2023-11",
        )
    ],
}

TRANSACTION_HISTORY: Dict[str, List[TransactionRecord]] = {
    "11680": [
        TransactionRecord(month="2023-12", avg_price=4.12, transactions=31),
        TransactionRecord(month="2024-01", avg_price=4.25, transactions=33),
        TransactionRecord(month="2024-02", avg_price=4.3, transactions=35),
    ],
    "26290": [
        TransactionRecord(month="2023-12", avg_price=3.6, transactions=18),
        TransactionRecord(month="2024-01", avg_price=3.72, transactions=22),
        TransactionRecord(month="2024-02", avg_price=3.8, transactions=24),
    ],
}

LEASE_SUMMARY: Dict[str, LeaseSummary] = {
    "11680": LeaseSummary(cap_rate=4.2, vacancy_rate=2.8, market_temperature=0.71),
    "26290": LeaseSummary(cap_rate=4.7, vacancy_rate=3.4, market_temperature=0.66),
}
