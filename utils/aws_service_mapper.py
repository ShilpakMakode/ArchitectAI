"""AWS service mapping utilities for ArchitectAI.

This module converts structured requirement signals into a baseline
AWS architecture service map. The logic is deterministic so the system
still works when an LLM response is unavailable.
"""

from __future__ import annotations

from typing import Any, Dict


def _as_bool(value: Any) -> bool:
    """Normalize truthy/falsy values from mixed sources."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def _as_int(value: Any, default: int = 0) -> int:
    """Normalize numeric user counts."""
    try:
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return int(float(value))
    except (TypeError, ValueError):
        return default


def map_requirements_to_services(requirements: Dict[str, Any]) -> Dict[str, str]:
    """Generate baseline AWS service selections from structured requirements."""
    expected_users = _as_int(requirements.get("expected_users"))
    authentication = _as_bool(requirements.get("authentication"))
    file_storage = _as_bool(requirements.get("file_storage"))
    global_users = _as_bool(requirements.get("global_users"))
    application_type = str(requirements.get("application_type", "web app")).lower()

    high_scale = expected_users >= 100_000
    streaming_like = any(keyword in application_type for keyword in ["video", "stream", "media"])
    realtime_like = any(keyword in application_type for keyword in ["chat", "realtime", "real-time"])

    architecture = {
        "compute": "Amazon ECS on AWS Fargate",
        "database": "Amazon RDS PostgreSQL",
        "storage": "Amazon S3" if file_storage or streaming_like else "Not Required",
        "cdn": "Amazon CloudFront" if global_users or streaming_like or high_scale else "Not Required",
        "load_balancer": "Application Load Balancer",
        "network": "Amazon VPC",
        "dns": "Amazon Route 53",
        "caching": "Amazon ElastiCache Redis" if realtime_like or high_scale else "Optional",
        "message_queue": "Amazon SQS" if realtime_like or high_scale else "Optional",
        "authentication": "Amazon Cognito" if authentication else "Not Required",
        "monitoring": "Amazon CloudWatch",
    }

    return architecture

