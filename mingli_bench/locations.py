"""Location and timezone normalization helpers.

The project keeps this module intentionally small and auditable. It covers the
locations present in the bundled benchmark fixtures and returns explicit
warnings when a place name is too broad for a reliable timezone decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_TZ_OFFSET_HOURS = 8.0


@dataclass(frozen=True)
class TimezoneResolution:
    """Normalized timezone information for one location query."""

    query_location: Optional[str]
    query_country: Optional[str]
    normalized_location: str
    timezone: str
    utc_offset_hours: float
    confidence: str
    warnings: Tuple[str, ...] = ()

    def as_dict(self) -> Dict[str, object]:
        """Return a JSON-friendly representation."""

        return {
            "query_location": self.query_location,
            "query_country": self.query_country,
            "normalized_location": self.normalized_location,
            "timezone": self.timezone,
            "utc_offset_hours": self.utc_offset_hours,
            "confidence": self.confidence,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class _LocationRule:
    normalized_location: str
    timezone: str
    utc_offset_hours: float
    confidence: str


_LOCATION_RULES: Dict[str, _LocationRule] = {
    "中国": _LocationRule("China", "Asia/Shanghai", 8.0, "country_default"),
    "china": _LocationRule("China", "Asia/Shanghai", 8.0, "country_default"),
    "大陆": _LocationRule("Mainland China", "Asia/Shanghai", 8.0, "regional"),
    "中国大陆": _LocationRule("Mainland China", "Asia/Shanghai", 8.0, "regional"),
    "北京": _LocationRule("Beijing", "Asia/Shanghai", 8.0, "city"),
    "广东": _LocationRule("Guangdong", "Asia/Shanghai", 8.0, "province"),
    "潮汕": _LocationRule("Chaoshan", "Asia/Shanghai", 8.0, "region"),
    "香港": _LocationRule("Hong Kong", "Asia/Hong_Kong", 8.0, "region"),
    "中国香港": _LocationRule("Hong Kong", "Asia/Hong_Kong", 8.0, "region"),
    "中國香港": _LocationRule("Hong Kong", "Asia/Hong_Kong", 8.0, "region"),
    "hong kong": _LocationRule("Hong Kong", "Asia/Hong_Kong", 8.0, "region"),
    "hk": _LocationRule("Hong Kong", "Asia/Hong_Kong", 8.0, "region"),
    "台湾": _LocationRule("Taiwan", "Asia/Taipei", 8.0, "region"),
    "台灣": _LocationRule("Taiwan", "Asia/Taipei", 8.0, "region"),
    "中国台湾": _LocationRule("Taiwan", "Asia/Taipei", 8.0, "region"),
    "中國台灣": _LocationRule("Taiwan", "Asia/Taipei", 8.0, "region"),
    "taiwan": _LocationRule("Taiwan", "Asia/Taipei", 8.0, "region"),
    "taipei": _LocationRule("Taiwan", "Asia/Taipei", 8.0, "city"),
    "malaysia": _LocationRule("Malaysia", "Asia/Kuala_Lumpur", 8.0, "country"),
    "马来西亚": _LocationRule("Malaysia", "Asia/Kuala_Lumpur", 8.0, "country"),
    "馬來西亞": _LocationRule("Malaysia", "Asia/Kuala_Lumpur", 8.0, "country"),
    "kuala lumpur": _LocationRule("Malaysia", "Asia/Kuala_Lumpur", 8.0, "city"),
    "新加坡": _LocationRule("Singapore", "Asia/Singapore", 8.0, "country"),
    "singapore": _LocationRule("Singapore", "Asia/Singapore", 8.0, "country"),
    "宫崎县": _LocationRule("Miyazaki, Japan", "Asia/Tokyo", 9.0, "prefecture"),
    "miyazaki": _LocationRule("Miyazaki, Japan", "Asia/Tokyo", 9.0, "prefecture"),
    "日本": _LocationRule("Japan", "Asia/Tokyo", 9.0, "country"),
    "japan": _LocationRule("Japan", "Asia/Tokyo", 9.0, "country"),
}

_AMBIGUOUS_LOCATION_NAMES = {"usa", "us", "u.s.", "u.s.a.", "美国", "美國"}


def _clean_token(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = str(value).strip()
    if not cleaned:
        return None
    return " ".join(cleaned.lower().split())


def resolve_timezone(
    location: Optional[str] = None,
    *,
    country: Optional[str] = None,
    default_timezone: str = DEFAULT_TIMEZONE,
    default_tz_offset_hours: float = DEFAULT_TZ_OFFSET_HOURS,
) -> TimezoneResolution:
    """Resolve benchmark place names to a fixed timezone offset.

    The returned offset is a conventional local civil-time offset, not a full
    historical daylight-saving-time model. Ambiguous locations fall back to the
    provided default and include a warning.
    """

    location_key = _clean_token(location)
    country_key = _clean_token(country)

    for key in (location_key, country_key):
        if key in _LOCATION_RULES:
            rule = _LOCATION_RULES[key]
            return TimezoneResolution(
                query_location=location,
                query_country=country,
                normalized_location=rule.normalized_location,
                timezone=rule.timezone,
                utc_offset_hours=rule.utc_offset_hours,
                confidence=rule.confidence,
            )

    warnings = []
    if location_key in _AMBIGUOUS_LOCATION_NAMES or country_key in _AMBIGUOUS_LOCATION_NAMES:
        normalized_location = "Ambiguous USA"
        warnings.append("ambiguous_usa_location_requires_state_or_city")
    else:
        normalized_location = "Unknown"
        warnings.append("unknown_location")
    warnings.append("timezone_defaulted_to_utc_plus_8")

    return TimezoneResolution(
        query_location=location,
        query_country=country,
        normalized_location=normalized_location,
        timezone=default_timezone,
        utc_offset_hours=default_tz_offset_hours,
        confidence="default",
        warnings=tuple(warnings),
    )


__all__ = [
    "DEFAULT_TIMEZONE",
    "DEFAULT_TZ_OFFSET_HOURS",
    "TimezoneResolution",
    "resolve_timezone",
]
