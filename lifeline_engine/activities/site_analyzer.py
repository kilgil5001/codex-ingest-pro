"""Activities responsible for collecting and normalizing site data."""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from temporalio import activity

from lifeline_engine.config import get_settings
from lifeline_engine.models.domain import AddressPayload
from lifeline_engine.utils.http import HttpClient


@activity.defn(name="normalize_address")
async def normalize_address(raw_address: str) -> AddressPayload:
    """Normalize incoming address strings using government APIs."""

    settings = get_settings()
    payload = AddressPayload(raw=raw_address)
    async with HttpClient(base_url="https://api.example.gov") as client:
        response = await client.get(
            "/normalize",
            params={"q": raw_address},
            headers={"X-API-Key": "${ADDRESS_API_KEY}"},
        )
    data = response.json()
    payload.normalized = data.get("normalizedAddress")
    payload.metadata.update({"source": "government", "confidence": str(data.get("confidence", 0.0))})
    if data.get("confidence", 0.0) < 0.8:
        payload.metadata["manual_review_required"] = "true"
    return payload


@activity.defn(name="geocode_address")
async def geocode_address(payload: AddressPayload) -> AddressPayload:
    """Retrieve coordinates using a multi-provider strategy."""

    providers = ["kakao", "naver"]
    async with HttpClient(timeout=5.0) as client:
        for provider in providers:
            response = await client.get(
                f"https://maps.{provider}.com/geocode",
                params={"query": payload.normalized or payload.raw},
            )
            data = response.json()
            confidence = data.get("confidence", 0.0)
            if confidence >= 0.8:
                payload.latitude = data["lat"]
                payload.longitude = data["lng"]
                payload.metadata["geocode_provider"] = provider
                payload.metadata["geocode_confidence"] = str(confidence)
                break
        else:
            payload.metadata["geocode_confidence"] = "0.0"
            payload.metadata["candidate_locations"] = json.dumps(data.get("candidates", []))
    return payload


@activity.defn(name="fetch_administrative_area")
async def fetch_administrative_area(payload: AddressPayload) -> AddressPayload:
    """Attach administrative metadata including permit office contact."""

    async with HttpClient(base_url="https://admin.codes.gov") as client:
        response = await client.get(
            "/lookup",
            params={"lat": payload.latitude, "lng": payload.longitude},
        )
    data = response.json()
    payload.administrative_area = data.get("code")
    payload.metadata["permit_office"] = data.get("permit_office")
    payload.metadata["inspector_profile"] = json.dumps(data.get("inspector_profile", {}))
    return payload


@activity.defn(name="fetch_cadastral_info")
async def fetch_cadastral_info(payload: AddressPayload) -> Dict[str, str]:
    async with HttpClient(base_url="https://vworld.gov") as client:
        response = await client.get(
            "/cadastral",
            params={"lat": payload.latitude, "lng": payload.longitude},
        )
    data = response.json()
    return {
        "geojson": json.dumps(data.get("geojson")),
        "ownership": data.get("ownership"),
        "area": str(data.get("area")),
    }


@activity.defn(name="collect_zoning_rules")
async def collect_zoning_rules(administrative_area: str) -> Dict[str, str]:
    async with HttpClient(base_url="https://zoning.gov") as client:
        response = await client.get("/rules", params={"code": administrative_area})
    data = response.json()
    return {
        "land_use": data.get("land_use"),
        "special_district": data.get("special_district"),
        "far": str(data.get("far")),
        "coverage": str(data.get("coverage")),
        "height_limit": str(data.get("height_limit")),
    }
