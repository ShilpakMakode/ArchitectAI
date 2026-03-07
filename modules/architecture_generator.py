"""Architecture generation module for ArchitectAI.

This module produces an AWS architecture JSON object from parsed
requirements. It supports LLM generation with deterministic fallback.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore

from utils.aws_service_mapper import map_requirements_to_services


class ArchitectureGenerator:
    """Generate AWS architecture service selections from requirements."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.prompt_template = self._load_prompt()
        base_url = os.getenv("OPENAI_BASE_URL")
        self.client = OpenAI(api_key=api_key, base_url=base_url) if (OpenAI and api_key) else None
        self.last_mode = "mapper"
        self.last_error = ""
        self.llm_attempted = False

    @staticmethod
    def _load_prompt() -> str:
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "architecture_prompt.txt"
        try:
            return prompt_path.read_text(encoding="utf-8")
        except OSError:
            return "Generate strict JSON architecture mapping for AWS."

    def _generate_with_llm(self, requirements: Dict[str, Any]) -> Optional[Dict[str, str]]:
        if not self.client:
            self.last_error = "LLM client is not initialized. Check API key and openai package."
            return None

        self.llm_attempted = True
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.prompt_template},
                    {"role": "user", "content": json.dumps(requirements)},
                ],
                temperature=0,
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            return {str(k): str(v) for k, v in parsed.items()}
        except Exception as exc:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompt_template + "\nReturn ONLY valid JSON."},
                        {"role": "user", "content": json.dumps(requirements)},
                    ],
                    temperature=0,
                )
                content = response.choices[0].message.content or "{}"
                parsed = json.loads(content)
                return {str(k): str(v) for k, v in parsed.items()}
            except Exception as second_exc:
                self.last_error = f"LLM architecture generation failed. Primary: {exc}. Fallback: {second_exc}"
                return None

    @staticmethod
    def _normalize(architecture: Dict[str, Any]) -> Dict[str, str]:
        normalized = {}
        required_keys = [
            "compute",
            "database",
            "storage",
            "cdn",
            "load_balancer",
            "network",
            "dns",
            "caching",
            "message_queue",
            "authentication",
            "monitoring",
        ]
        for key in required_keys:
            value = architecture.get(key, "Not Required")
            normalized[key] = str(value)
        return normalized

    def generate(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate architecture JSON for the given requirements."""
        if not isinstance(requirements, dict):
            raise ValueError("Requirements must be a dictionary.")

        architecture = self._generate_with_llm(requirements)
        if architecture is not None:
            self.last_mode = "llm"
        else:
            self.last_mode = "mapper"
            architecture = map_requirements_to_services(requirements)
        return self._normalize(architecture)
