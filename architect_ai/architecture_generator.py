from collections import OrderedDict
from typing import Dict, List, Tuple

from .models import ArchitectureSpec, RequirementProfile

SERVICE_MAP: Dict[str, Dict[str, str]] = {
    "aws": {
        "network": "VPC",
        "load_balancer": "Application Load Balancer",
        "compute": "ECS Service",
        "autoscaling": "Auto Scaling",
        "relational_db": "RDS",
        "object_storage": "S3",
        "cdn": "CloudFront",
        "queue": "SQS",
        "cache": "ElastiCache",
    },
    "gcp": {
        "network": "VPC Network",
        "load_balancer": "Cloud Load Balancing",
        "compute": "Cloud Run",
        "autoscaling": "Cloud Run Auto Scaling",
        "relational_db": "Cloud SQL",
        "object_storage": "Cloud Storage",
        "cdn": "Cloud CDN",
        "queue": "Pub/Sub",
        "cache": "Memorystore",
    },
    "azure": {
        "network": "Virtual Network",
        "load_balancer": "Application Gateway",
        "compute": "Container Apps",
        "autoscaling": "Azure Autoscale",
        "relational_db": "Azure SQL Database",
        "object_storage": "Blob Storage",
        "cdn": "Azure Front Door",
        "queue": "Service Bus",
        "cache": "Azure Cache for Redis",
    },
}


def _render_ascii_tree(root: str, children: Dict[str, List[str]]) -> List[str]:
    lines: List[str] = [root]

    def visit(node: str, prefix: str) -> None:
        node_children = children.get(node, [])
        for index, child in enumerate(node_children):
            is_last = index == len(node_children) - 1
            branch = "`- " if is_last else "|- "
            lines.append(f"{prefix}{branch}{child}")
            extension = "   " if is_last else "|  "
            visit(child, prefix + extension)

    visit(root, "")
    return lines


def _add_edge_unique(edges: List[Tuple[str, str]], src: str, dst: str) -> None:
    if (src, dst) not in edges:
        edges.append((src, dst))


def generate_architecture(profile: RequirementProfile) -> ArchitectureSpec:
    cloud = profile.cloud if profile.cloud in SERVICE_MAP else "aws"
    service_names = SERVICE_MAP[cloud]

    network = service_names["network"]
    load_balancer = service_names["load_balancer"]
    compute = service_names["compute"]

    tree_children: "OrderedDict[str, List[str]]" = OrderedDict()
    tree_children[network] = [load_balancer]
    tree_children[load_balancer] = [compute]
    tree_children[compute] = []

    optional_vpc_children: List[str] = []
    if profile.needs_relational_db:
        optional_vpc_children.append(service_names["relational_db"])
        tree_children[service_names["relational_db"]] = []
    if profile.needs_object_storage:
        optional_vpc_children.append(service_names["object_storage"])
        tree_children[service_names["object_storage"]] = []
    if profile.needs_global_delivery:
        optional_vpc_children.append(service_names["cdn"])
        tree_children[service_names["cdn"]] = []

    tree_children[network].extend(optional_vpc_children)

    if profile.needs_cache:
        tree_children[compute].append(service_names["cache"])
        tree_children[service_names["cache"]] = []
    if profile.needs_queue:
        tree_children[compute].append(service_names["queue"])
        tree_children[service_names["queue"]] = []
    if profile.high_scale:
        tree_children[compute].append(service_names["autoscaling"])
        tree_children[service_names["autoscaling"]] = []

    services: List[str] = []
    for node, node_children in tree_children.items():
        if node not in services:
            services.append(node)
        for child in node_children:
            if child not in services:
                services.append(child)

    edges: List[Tuple[str, str]] = []
    for parent, node_children in tree_children.items():
        for child in node_children:
            _add_edge_unique(edges, parent, child)

    if profile.needs_global_delivery and profile.needs_object_storage:
        _add_edge_unique(edges, service_names["cdn"], service_names["object_storage"])
    if profile.needs_global_delivery:
        _add_edge_unique(edges, service_names["cdn"], load_balancer)
    if profile.needs_relational_db:
        _add_edge_unique(edges, compute, service_names["relational_db"])
    if profile.needs_object_storage:
        _add_edge_unique(edges, compute, service_names["object_storage"])

    tree_lines = _render_ascii_tree(network, tree_children)
    return ArchitectureSpec(
        cloud=cloud,
        services=services,
        edges=edges,
        tree_lines=tree_lines,
    )

