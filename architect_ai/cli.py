import argparse
import json
from pathlib import Path

from .architecture_generator import generate_architecture
from .diagram_generator import generate_graphviz_dot, generate_mermaid
from .explanation_layer import build_explanations, explanations_to_markdown
from .requirements_parser import parse_requirements


def run(input_text: str, cloud: str, output_dir: Path) -> Path:
    profile = parse_requirements(user_input=input_text, default_cloud=cloud)
    spec = generate_architecture(profile)
    spec.explanations = build_explanations(spec, profile)

    output_dir.mkdir(parents=True, exist_ok=True)

    tree_path = output_dir / "architecture_tree.txt"
    mermaid_path = output_dir / "architecture_diagram.mmd"
    dot_path = output_dir / "architecture_diagram.dot"
    explanations_path = output_dir / "architecture_explanations.md"
    spec_path = output_dir / "architecture_spec.json"

    tree_path.write_text("\n".join(spec.tree_lines) + "\n", encoding="utf-8")
    mermaid_path.write_text(generate_mermaid(spec), encoding="utf-8")
    dot_path.write_text(generate_graphviz_dot(spec), encoding="utf-8")
    explanations_path.write_text(explanations_to_markdown(spec.explanations), encoding="utf-8")
    spec_path.write_text(json.dumps(spec.to_dict(), indent=2), encoding="utf-8")

    print("ArchitectAI MVP output generated.")
    print(f"Cloud: {spec.cloud.upper()}")
    print(f"Input: {profile.raw_input}")
    print(f"Services: {', '.join(spec.services)}")
    print(f"Artifacts directory: {output_dir}")
    print("")
    print("Architecture Tree")
    print("-----------------")
    print("\n".join(spec.tree_lines))

    return output_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ArchitectAI MVP: parse requirements and generate cloud architecture diagrams."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Natural language architecture requirement. Example: Build scalable AI chatbot backend with 1M users",
    )
    parser.add_argument(
        "--cloud",
        default="aws",
        choices=["aws", "gcp", "azure"],
        help="Preferred cloud provider when not explicitly mentioned in input.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where generated artifacts will be written.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run(
        input_text=args.input,
        cloud=args.cloud,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()

