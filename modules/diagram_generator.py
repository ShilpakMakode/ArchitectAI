"""Diagram generation module for ArchitectAI.

This module renders an AWS architecture diagram using Python Diagrams.
If diagram rendering fails, it returns structured error details so the
application can degrade gracefully.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def _is_enabled(service_name: str) -> bool:
    value = (service_name or "").strip().lower()
    return value not in {"", "not required", "optional", "none", "n/a"}


def _short_label(service_name: str, default: str) -> str:
    value = (service_name or "").strip()
    return value if _is_enabled(value) else default


class DiagramGenerator:
    """Create architecture diagram artifacts from architecture JSON."""

    def generate(self, architecture: Dict[str, str], output_path: str) -> Dict[str, Any]:
        """Generate architecture PNG diagram and return metadata."""
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        base_path = target.with_suffix("")

        try:
            from diagrams import Diagram
            from diagrams.aws.compute import ECS
            from diagrams.aws.database import ElastiCache, RDS
            from diagrams.aws.integration import SQS
            from diagrams.aws.management import Cloudwatch
            from diagrams.aws.network import CloudFront, ELB, Route53, VPC
            from diagrams.aws.security import Cognito
            from diagrams.aws.storage import S3
            from diagrams.onprem.client import Users
        except Exception as exc:
            return {
                "generated": False,
                "diagram_path": "",
                "error": f"Python Diagrams imports failed: {exc}",
            }

        try:
            with Diagram(
                "ArchitectAI AWS Architecture",
                filename=str(base_path),
                show=False,
                outformat="png",
                direction="TB",
            ):
                users = Users("Users")
                dns_label = _short_label(architecture.get("dns", ""), "Route 53")
                network_label = _short_label(architecture.get("network", ""), "VPC")
                lb_label = _short_label(architecture.get("load_balancer", ""), "Load Balancer")
                compute_label = _short_label(architecture.get("compute", ""), "Compute")
                db_label = _short_label(architecture.get("database", ""), "Database")
                storage_label = _short_label(architecture.get("storage", ""), "Storage")
                cdn_label = _short_label(architecture.get("cdn", ""), "CDN")
                queue_label = _short_label(architecture.get("message_queue", ""), "Queue")
                cache_label = _short_label(architecture.get("caching", ""), "Cache")
                auth_label = _short_label(architecture.get("authentication", ""), "Auth")
                monitor_label = _short_label(architecture.get("monitoring", ""), "CloudWatch")

                dns = Route53(dns_label)
                network = VPC(network_label)
                lb = ELB(lb_label)
                compute = ECS(compute_label)
                monitor = Cloudwatch(monitor_label)

                users >> dns
                if _is_enabled(architecture.get("cdn", "")):
                    cdn = CloudFront(cdn_label)
                    dns >> cdn >> lb
                else:
                    dns >> lb

                dns >> network
                network >> lb >> compute
                compute >> monitor

                if _is_enabled(architecture.get("database", "")):
                    db = RDS(db_label)
                    compute >> db
                if _is_enabled(architecture.get("storage", "")):
                    storage = S3(storage_label)
                    compute >> storage
                if _is_enabled(architecture.get("message_queue", "")):
                    queue = SQS(queue_label)
                    compute >> queue
                if _is_enabled(architecture.get("caching", "")):
                    cache = ElastiCache(cache_label)
                    compute >> cache
                if _is_enabled(architecture.get("authentication", "")):
                    auth = Cognito(auth_label)
                    users >> auth >> lb

            return {
                "generated": True,
                "diagram_path": str(base_path.with_suffix(".png")),
                "error": "",
            }
        except Exception as exc:
            return {
                "generated": False,
                "diagram_path": "",
                "error": f"Diagram generation failed: {exc}",
            }
