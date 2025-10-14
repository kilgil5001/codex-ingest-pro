"""Activities responsible for collecting and normalizing site data."""
from __future__ import annotations

import hashlib
from typing import Dict

from temporalio import activity

from lifeline_engine.models.domain import (
    AddressPayload,
    ConfidenceLevel,
    GeoCoordinate,
)
from lifeline_engine.utils import logging as log_utils
from lifeline_engine.utils.reference_data import (
    ADDRESS_ALIAS,
    ADMINISTRATIVE_AREAS,
    CADASTRAL_INFO,
    GEOCODE_INDEX,
    ZONING_RULESETS,
)


async def _confidence_from_string(value: str) -> ConfidenceLevel:
    if not value:
        return ConfidenceLevel.LOW
    if any(char.isdigit() for char in value):
        return ConfidenceLevel.HIGH
    return ConfidenceLevel.MEDIUM


def _normalized_address(raw_address: str) -> str:
    cleaned = " ".join(raw_address.strip().replace("  ", " ").split())
    return ADDRESS_ALIAS.get(cleaned, cleaned)


def _fallback_coordinate(address: str) -> GeoCoordinate:
    digest = hashlib.sha256(address.encode("utf-8")).digest()
    lat = 35 + (digest[0] / 255) * 5
    lng = 125 + (digest[1] / 255) * 5
    altitude = 30 + (digest[2] / 255) * 20
    return GeoCoordinate(latitude=round(lat, 6), longitude=round(lng, 6), altitude=round(altitude, 2))


@activity.defn(name="normalize_address")
async def normalize_address(raw_address: str) -> AddressPayload:
    """Normalize incoming address strings using deterministic heuristics."""

    with log_utils.activity_context("normalize_address", {"raw": raw_address}):
        normalized = _normalized_address(raw_address)
        confidence = await _confidence_from_string(normalized)
        payload = AddressPayload(raw=raw_address, normalized=normalized)
        payload.metadata.update({
            "normalized_confidence": confidence.value,
            "requires_confirmation": str(confidence == ConfidenceLevel.LOW).lower(),
        })
        return payload


@activity.defn(name="geocode_address")
async def geocode_address(payload: AddressPayload) -> AddressPayload:
    """Retrieve coordinates using reference datasets and deterministic fallback."""

    address = payload.normalized or payload.raw
    with log_utils.activity_context("geocode_address", {"address": address}):
        coordinate_tuple = GEOCODE_INDEX.get(address)
        if coordinate_tuple:
            payload.coordinate = GeoCoordinate(
                latitude=coordinate_tuple[0],
                longitude=coordinate_tuple[1],
                altitude=coordinate_tuple[2],
            )
            payload.metadata["geocode_provider"] = "reference-index"
            payload.metadata["geocode_confidence"] = ConfidenceLevel.HIGH.value
        else:
            fallback = _fallback_coordinate(address)
            payload.coordinate = fallback
            payload.metadata["geocode_provider"] = "deterministic-fallback"
            payload.metadata["geocode_confidence"] = ConfidenceLevel.MEDIUM.value
        return payload


@activity.defn(name="fetch_administrative_area")
async def fetch_administrative_area(payload: AddressPayload) -> AddressPayload:
    """Attach administrative metadata including permit office contact."""

    address = payload.normalized or payload.raw
    with log_utils.activity_context("fetch_administrative_area", {"address": address}):
        payload.administrative_area = ADMINISTRATIVE_AREAS.get(address)
        if payload.administrative_area:
            payload.metadata["administrative_code"] = payload.administrative_area.code
            payload.metadata["permit_office"] = payload.administrative_area.permit_office
        else:
            payload.metadata["administrative_code"] = "unknown"
        return payload


@activity.defn(name="fetch_cadastral_info")
async def fetch_cadastral_info(payload: AddressPayload) -> Dict[str, str]:
    """Fetch cadastral parcel data for the site."""

    address = payload.normalized or payload.raw
    with log_utils.activity_context("fetch_cadastral_info", {"address": address}):
        payload.cadastral = CADASTRAL_INFO.get(address)
        if payload.cadastral:
            payload.metadata["cadastral_parcel"] = payload.cadastral.parcel_id
            return {
                "geojson": payload.cadastral.boundary_geojson,
                "ownership": payload.cadastral.ownership,
                "area": str(payload.cadastral.area_sqm),
            }
        return {
            "geojson": "{}",
            "ownership": "unknown",
            "area": "0",
        }


@activity.defn(name="collect_zoning_rules")
async def collect_zoning_rules(administrative_area: str) -> Dict[str, str]:
    """Collect zoning rules using cached data from reference datasets."""

    with log_utils.activity_context("collect_zoning_rules", {"code": administrative_area}):
        zoning = ZONING_RULESETS.get(administrative_area)
        if zoning:
            return {
                "land_use": zoning.land_use,
                "special_district": zoning.special_district or "",
                "far": str(zoning.far),
                "coverage": str(zoning.coverage),
                "height_limit": str(zoning.height_limit),
            }
        return {
            "land_use": "미확인",
            "special_district": "",
            "far": "3.0",
            "coverage": "0.6",
            "height_limit": "45.0",
        }
