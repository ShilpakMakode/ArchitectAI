import re
from typing import List

from .models import ArchitectureSpec


def _node_id(service_name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_]", "_", service_name.strip())
    if not sanitized:
        return "node"
    if sanitized[0].isdigit():
        sanitized = f"n_{sanitized}"
    return sanitized


def generate_mermaid(spec: ArchitectureSpec) -> str:
    lines: List[str] = ["flowchart TD"]
    for service in spec.services:
        node = _node_id(service)
        lines.append(f'    {node}["{service}"]')
    for source, destination in spec.edges:
        lines.append(f"    {_node_id(source)} --> {_node_id(destination)}")
    return "\n".join(lines) + "\n"


def generate_graphviz_dot(spec: ArchitectureSpec) -> str:
    lines: List[str] = [
        "digraph ArchitectAI {",
        "    rankdir=TB;",
        "    node [shape=box, style=rounded];",
    ]
    for service in spec.services:
        lines.append(f'    "{service}";')
    for source, destination in spec.edges:
        lines.append(f'    "{source}" -> "{destination}";')
    lines.append("}")
    return "\n".join(lines) + "\n"

