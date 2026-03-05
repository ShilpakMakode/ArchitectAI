from typing import Dict

from .models import ArchitectureSpec, RequirementProfile

BASE_EXPLANATIONS: Dict[str, str] = {
    "VPC": "Provides network isolation and security boundaries for core services.",
    "Application Load Balancer": "Distributes incoming traffic across backend containers and improves availability.",
    "ECS Service": "Runs containerized backend APIs with managed orchestration.",
    "Auto Scaling": "Automatically increases or decreases service instances based on demand.",
    "RDS": "Provides managed relational storage for transactional and application data.",
    "S3": "Stores static assets, logs, and user-uploaded objects with high durability.",
    "CloudFront": "Reduces global latency by caching content at edge locations.",
    "SQS": "Decouples asynchronous workloads and smooths traffic spikes.",
    "ElastiCache": "Improves read performance and reduces database load via in-memory caching.",
    "VPC Network": "Provides private networking and segmentation for GCP services.",
    "Cloud Load Balancing": "Balances external traffic across backend compute instances.",
    "Cloud Run": "Runs stateless containerized services with minimal operational overhead.",
    "Cloud Run Auto Scaling": "Scales container instances automatically as request volume changes.",
    "Cloud SQL": "Managed relational database service for structured transactional data.",
    "Cloud Storage": "Durable object storage for media, artifacts, and backups.",
    "Cloud CDN": "Caches content near users to reduce latency and origin load.",
    "Pub/Sub": "Handles asynchronous messaging and event-driven processing.",
    "Memorystore": "Managed in-memory cache for faster reads and lower database pressure.",
    "Virtual Network": "Private network boundary for Azure workloads.",
    "Application Gateway": "Layer-7 traffic distribution and routing for backend services.",
    "Container Apps": "Runs containerized apps with managed scaling and simplified operations.",
    "Azure Autoscale": "Adjusts service capacity dynamically based on demand.",
    "Azure SQL Database": "Managed relational database for consistent transactional workloads.",
    "Blob Storage": "Object storage for static content, uploads, and archival data.",
    "Azure Front Door": "Global edge routing and caching to reduce user latency.",
    "Service Bus": "Reliable asynchronous messaging between distributed components.",
    "Azure Cache for Redis": "In-memory caching layer for low-latency reads.",
}


def build_explanations(spec: ArchitectureSpec, profile: RequirementProfile) -> Dict[str, str]:
    explanations: Dict[str, str] = {}

    for service in spec.services:
        reason = BASE_EXPLANATIONS.get(service, "Selected to satisfy a required architecture capability.")

        if service in {"Auto Scaling", "Cloud Run Auto Scaling", "Azure Autoscale"} and profile.estimated_users:
            reason += f" Target scale: about {profile.estimated_users:,} users."
        if service in {"CloudFront", "Cloud CDN", "Azure Front Door"} and profile.needs_global_delivery:
            reason += " This supports global user access with lower response times."
        if service in {"RDS", "Cloud SQL", "Azure SQL Database"} and profile.high_scale:
            reason += " For high-scale workloads, deploy with high availability and read replicas where needed."
        if service in {"ElastiCache", "Memorystore", "Azure Cache for Redis"} and profile.ai_workload:
            reason += " Useful for conversational context/session caching in AI chatbot backends."
        if service in {"SQS", "Pub/Sub", "Service Bus"} and profile.ai_workload:
            reason += " This helps absorb burst traffic from inference requests."

        explanations[service] = reason

    return explanations


def explanations_to_markdown(explanations: Dict[str, str]) -> str:
    lines = ["# Architecture Explanations", ""]
    for service, reason in explanations.items():
        lines.append(f"- **{service}**: {reason}")
    lines.append("")
    return "\n".join(lines)

