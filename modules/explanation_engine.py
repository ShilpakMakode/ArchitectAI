"""Explanation engine for ArchitectAI.

This module provides service-level rationale for generated AWS architectures.
"""

from __future__ import annotations

from typing import Dict


SERVICE_EXPLANATIONS = {
    "Amazon VPC": "Creates a secure network boundary to isolate application resources.",
    "Application Load Balancer": "Distributes incoming traffic across containers for high availability.",
    "Amazon ECS on AWS Fargate": "Runs containerized workloads without managing servers.",
    "Amazon RDS PostgreSQL": "Provides managed relational storage for transactional data.",
    "Amazon S3": "Stores static content, user uploads, and media assets durably.",
    "Amazon CloudFront": "Caches content at edge locations to reduce global latency.",
    "Amazon Route 53": "Provides DNS routing and endpoint discovery for users.",
    "Amazon ElastiCache Redis": "Reduces database load with low-latency in-memory caching.",
    "Amazon SQS": "Decouples asynchronous tasks and smooths traffic spikes.",
    "Amazon Cognito": "Adds managed user sign-up, sign-in, and authentication.",
    "Amazon CloudWatch": "Provides logs, metrics, and alerts for operational visibility.",
}


class ExplanationEngine:
    """Generate explanation text for architecture choices."""

    def explain(self, architecture: Dict[str, str]) -> Dict[str, str]:
        explanations: Dict[str, str] = {}
        for _, service in architecture.items():
            if not service or service in {"Not Required", "Optional"}:
                continue
            explanations[service] = SERVICE_EXPLANATIONS.get(
                service,
                "Selected to satisfy a core reliability, scalability, or security requirement.",
            )
        return explanations

