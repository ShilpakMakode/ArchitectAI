"""Streamlit UI for ArchitectAI MVP.

ArchitectAI converts natural language system requirements into:
1) structured requirements JSON
2) AWS architecture JSON
3) architecture diagram
4) service-level explanations
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict

import streamlit as st
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv() -> bool:
        """Fallback when python-dotenv is not installed."""
        return False

from modules.architecture_generator import ArchitectureGenerator
from modules.diagram_generator import DiagramGenerator
from modules.explanation_engine import ExplanationEngine
from modules.requirement_parser import RequirementParser


OUTPUT_ROOT = Path("outputs")
DIAGRAM_DIR = OUTPUT_ROOT / "diagrams"


def _save_json(data: Dict, output_path: Path) -> None:
    """Persist JSON artifact to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> None:
    """Render Streamlit UI and run the ArchitectAI pipeline."""
    load_dotenv()
    st.set_page_config(page_title="ArchitectAI", layout="wide")

    st.title("ArchitectAI")
    st.caption("AI-powered AWS architecture generator")

    with st.sidebar:
        st.subheader("Configuration")
        model = st.text_input("OpenAI Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        use_llm = st.toggle("Use OpenAI API", value=bool(os.getenv("OPENAI_API_KEY")))
        st.caption(f"Base URL: {os.getenv('OPENAI_BASE_URL', '(default OpenAI)')}")
        st.markdown("Install Graphviz system binary for diagram rendering.")

    user_input = st.text_area(
        "System Requirement",
        placeholder="Build a scalable video streaming platform for 1M users.",
        height=140,
    )

    if st.button("Generate Architecture", type="primary"):
        if not user_input.strip():
            st.error("Please enter a requirement description.")
            return

        api_key = os.getenv("OPENAI_API_KEY") if use_llm else None
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            parser = RequirementParser(api_key=api_key, model=model)
            requirements_json = parser.parse(user_input)
        except Exception as exc:
            st.error(f"Requirement parsing failed: {exc}")
            return

        try:
            architecture_gen = ArchitectureGenerator(api_key=api_key, model=model)
            architecture_json = architecture_gen.generate(requirements_json)
        except Exception as exc:
            st.error(f"Architecture generation failed: {exc}")
            return

        explanation_engine = ExplanationEngine()
        explanations_json = explanation_engine.explain(architecture_json)

        with st.expander("LLM Diagnostics", expanded=True):
            st.write(
                {
                    "llm_toggle_enabled": use_llm,
                    "api_key_loaded": bool(os.getenv("OPENAI_API_KEY")),
                    "model": model,
                    "base_url": os.getenv("OPENAI_BASE_URL", ""),
                    "parser_llm_attempted": parser.llm_attempted,
                    "parser_mode_used": parser.last_mode,
                    "parser_error": parser.last_error,
                    "architecture_llm_attempted": architecture_gen.llm_attempted,
                    "architecture_mode_used": architecture_gen.last_mode,
                    "architecture_error": architecture_gen.last_error,
                }
            )

        # Persist structured outputs for reproducibility and later modules.
        _save_json(requirements_json, OUTPUT_ROOT / f"{run_id}_requirements.json")
        _save_json(architecture_json, OUTPUT_ROOT / f"{run_id}_architecture.json")
        _save_json(explanations_json, OUTPUT_ROOT / f"{run_id}_explanations.json")

        diagram_generator = DiagramGenerator()
        diagram_result = diagram_generator.generate(
            architecture=architecture_json,
            output_path=str(DIAGRAM_DIR / f"{run_id}.png"),
        )

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Requirements JSON")
            st.json(requirements_json)

            st.subheader("Architecture JSON")
            st.json(architecture_json)

        with col2:
            st.subheader("Design Explanations")
            st.json(explanations_json)

            st.subheader("Architecture Diagram")
            if diagram_result["generated"]:
                st.image(diagram_result["diagram_path"], use_container_width=True)
                st.success(f"Diagram saved at: {diagram_result['diagram_path']}")
            else:
                st.warning(diagram_result["error"])

        st.info(f"Run artifacts saved in: {OUTPUT_ROOT.resolve()}")


if __name__ == "__main__":
    main()
