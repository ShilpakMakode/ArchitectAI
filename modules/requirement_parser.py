"""Requirement parsing module for ArchitectAI.

This module converts free-form user requirements into a predictable JSON
contract used by downstream architecture generation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime when dependency missing
    OpenAI = None  # type: ignore


DEFAULT_REQUIREMENT_OUTPUT: Dict[str, Any] = {
    "application_type": "web application",
    "expected_users": 1000,
    "authentication": False,
    "file_storage": False,
    "global_users": False,
}


def _to_bool(value: Any) -> bool:
    """Normalize boolean values from string/numeric payloads."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "y"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


class RequirementParser:
    """Parse user system descriptions into structured requirement JSON."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> None:
        self.model = model
        self.prompt_template = self._load_prompt()
        self.client = OpenAI(api_key=api_key) if (OpenAI and api_key) else None

    @staticmethod
    def _load_prompt() -> str:
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "parser_prompt.txt"
        try:
            return prompt_path.read_text(encoding="utf-8")
        except OSError:
            return "Return strict JSON with keys: application_type, expected_users, authentication, file_storage, global_users."

    @staticmethod
    def _extract_expected_users(text: str) -> int:
        suffix_match = re.search(r"(\d+(?:\.\d+)?)\s*([kmb])\s*(users|user)?", text, re.IGNORECASE)
        if suffix_match:
            value = float(suffix_match.group(1))
            suffix = suffix_match.group(2).lower()
            multiplier = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[suffix]
            return int(value * multiplier)

        number_match = re.search(r"(\d[\d,]{2,})\s*(users|user)?", text, re.IGNORECASE)
        if number_match:
            return int(number_match.group(1).replace(",", ""))

        return DEFAULT_REQUIREMENT_OUTPUT["expected_users"]

    def _heuristic_parse(self, user_input: str) -> Dict[str, Any]:
        normalized = user_input.strip().lower()
        return {
            "application_type": self._infer_application_type(normalized),
            "expected_users": self._extract_expected_users(normalized),
            "authentication": any(k in normalized for k in ["login", "auth", "oauth", "signin", "sign in"]),
            "file_storage": any(k in normalized for k in ["file", "upload", "image", "video", "media", "storage"]),
            "global_users": any(k in normalized for k in ["global", "worldwide", "multi-region", "multiregion"]),
        }

    @staticmethod
    def _infer_application_type(text: str) -> str:
        if "video" in text or "stream" in text:
            return "video streaming platform"
        if "chatbot" in text or "chat" in text:
            return "chatbot backend"
        if "ecommerce" in text or "e-commerce" in text:
            return "ecommerce platform"
        if "analytics" in text or "data pipeline" in text:
            return "analytics platform"
        return DEFAULT_REQUIREMENT_OUTPUT["application_type"]

    def _parse_with_llm(self, user_input: str) -> Optional[Dict[str, Any]]:
        if not self.client:
            return None

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.prompt_template},
                    {"role": "user", "content": user_input},
                ],
                temperature=0,
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception:
            # Fallback keeps app functional even if the API call fails.
            return None

    @staticmethod
    def _normalize_output(parsed: Dict[str, Any]) -> Dict[str, Any]:
        output = dict(DEFAULT_REQUIREMENT_OUTPUT)
        output.update(parsed or {})

        # Strong type normalization for downstream modules.
        output["application_type"] = str(output.get("application_type", DEFAULT_REQUIREMENT_OUTPUT["application_type"]))
        try:
            output["expected_users"] = int(float(str(output.get("expected_users", DEFAULT_REQUIREMENT_OUTPUT["expected_users"])).replace(",", "")))
        except (TypeError, ValueError):
            output["expected_users"] = DEFAULT_REQUIREMENT_OUTPUT["expected_users"]

        output["authentication"] = _to_bool(output.get("authentication"))
        output["file_storage"] = _to_bool(output.get("file_storage"))
        output["global_users"] = _to_bool(output.get("global_users"))
        return output

    def parse(self, user_input: str) -> Dict[str, Any]:
        """Return structured requirements JSON from user text."""
        if not user_input or not user_input.strip():
            raise ValueError("Requirement text cannot be empty.")

        parsed = self._parse_with_llm(user_input) or self._heuristic_parse(user_input)
        return self._normalize_output(parsed)
