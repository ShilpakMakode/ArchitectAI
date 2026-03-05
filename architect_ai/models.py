from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class RequirementProfile:
    raw_input: str
    cloud: str
    estimated_users: Optional[int] = None
    high_scale: bool = False
    needs_global_delivery: bool = False
    needs_relational_db: bool = True
    needs_object_storage: bool = True
    ai_workload: bool = False
    needs_queue: bool = False
    needs_cache: bool = False


@dataclass
class ArchitectureSpec:
    cloud: str
    services: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    tree_lines: List[str] = field(default_factory=list)
    explanations: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "cloud": self.cloud,
            "services": self.services,
            "edges": self.edges,
            "tree_lines": self.tree_lines,
            "explanations": self.explanations,
        }

