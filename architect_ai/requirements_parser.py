import re
from typing import Optional

from .models import RequirementProfile

SUPPORTED_CLOUDS = {"aws", "gcp", "azure"}
HIGH_SCALE_USER_THRESHOLD = 100_000


def _extract_estimated_users(text: str) -> Optional[int]:
    suffix_match = re.search(r"(\d+(?:\.\d+)?)\s*([kmb])\s*(?:users|user)?", text, re.IGNORECASE)
    if suffix_match:
        value = float(suffix_match.group(1))
        suffix = suffix_match.group(2).lower()
        multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[suffix]
        return int(value * multiplier)

    plain_match = re.search(r"(\d[\d,]{2,})\s*(?:users|user)", text, re.IGNORECASE)
    if plain_match:
        return int(plain_match.group(1).replace(",", ""))

    return None


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def parse_requirements(user_input: str, default_cloud: str = "aws") -> RequirementProfile:
    normalized = user_input.strip().lower()

    cloud = default_cloud.lower()
    if "aws" in normalized:
        cloud = "aws"
    elif "gcp" in normalized or "google cloud" in normalized:
        cloud = "gcp"
    elif "azure" in normalized or "microsoft azure" in normalized:
        cloud = "azure"

    if cloud not in SUPPORTED_CLOUDS:
        cloud = "aws"

    estimated_users = _extract_estimated_users(normalized)

    global_keywords = {
        "global",
        "worldwide",
        "multi-region",
        "multiregion",
        "low latency",
        "cdn",
    }
    relational_keywords = {
        "transaction",
        "order",
        "payment",
        "ecommerce",
        "sql",
        "postgres",
        "mysql",
        "relational",
    }
    ai_keywords = {"ai", "ml", "chatbot", "llm", "inference"}
    queue_keywords = {"queue", "async", "event", "background", "chatbot"}
    storage_keywords = {"file", "image", "video", "media", "upload", "static"}
    cache_keywords = {"cache", "session", "real-time", "realtime", "low latency"}
    scale_keywords = {"scalable", "high traffic", "millions", "burst"}

    high_scale = False
    if estimated_users is not None and estimated_users >= HIGH_SCALE_USER_THRESHOLD:
        high_scale = True
    elif _contains_any(normalized, scale_keywords):
        high_scale = True

    needs_global_delivery = _contains_any(normalized, global_keywords) or high_scale
    needs_relational_db = _contains_any(normalized, relational_keywords) or True
    needs_object_storage = _contains_any(normalized, storage_keywords) or True
    ai_workload = _contains_any(normalized, ai_keywords)
    needs_queue = _contains_any(normalized, queue_keywords) or ai_workload
    needs_cache = _contains_any(normalized, cache_keywords) or high_scale or ai_workload

    return RequirementProfile(
        raw_input=user_input.strip(),
        cloud=cloud,
        estimated_users=estimated_users,
        high_scale=high_scale,
        needs_global_delivery=needs_global_delivery,
        needs_relational_db=needs_relational_db,
        needs_object_storage=needs_object_storage,
        ai_workload=ai_workload,
        needs_queue=needs_queue,
        needs_cache=needs_cache,
    )

