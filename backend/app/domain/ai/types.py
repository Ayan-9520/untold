"""AI job request/result types — vendor-neutral."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIJobRequest:
    module: str
    prompt: str
    parameters: dict[str, Any] = field(default_factory=dict)
    project_id: int | None = None


@dataclass
class AIJobResult:
    output_text: str
    result_url: str | None = None
    r2_key: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)
    provider: str = "demo"
