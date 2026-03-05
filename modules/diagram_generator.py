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
                route53 = Route53("Route 53")
                vpc = VPC("VPC")
                alb = ELB("ALB")
                compute = ECS("ECS Fargate")
                rds = RDS("RDS")
                s3 = S3("S3")
                cloudwatch = Cloudwatch("CloudWatch")

                users >> route53
                if _is_enabled(architecture.get("cdn", "")):
                    cdn = CloudFront("CloudFront")
                    route53 >> cdn >> alb
                else:
                    route53 >> alb

                route53 >> vpc
                vpc >> alb >> compute
                compute >> cloudwatch

                if _is_enabled(architecture.get("database", "")):
                    compute >> rds
                if _is_enabled(architecture.get("storage", "")):
                    compute >> s3
                if _is_enabled(architecture.get("message_queue", "")):
                    queue = SQS("SQS")
                    compute >> queue
                if _is_enabled(architecture.get("caching", "")):
                    cache = ElastiCache("ElastiCache")
                    compute >> cache
                if _is_enabled(architecture.get("authentication", "")):
                    auth = Cognito("Cognito")
                    users >> auth >> alb

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

