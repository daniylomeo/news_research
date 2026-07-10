"""Versioned quality gate for world-research Evidence Audit Projects."""

from .runner import evaluate_project
from .schema import GATE_VERSION, SCHEMA_VERSION

__all__ = ["GATE_VERSION", "SCHEMA_VERSION", "evaluate_project"]
