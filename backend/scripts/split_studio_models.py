"""One-time utility: split studio_platform.py into bounded-context modules."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "app/models/studio_platform.py").read_text(encoding="utf-8")
lines = src.splitlines()

classes = []
for i, line in enumerate(lines):
    m = re.match(r"^class (\w+)", line)
    if m:
        classes.append((m.group(1), i))

MODULES = {
    "project": {
        "StudioProjectMember",
        "ProjectComment",
        "StudioTask",
        "StudioApproval",
        "StudioNotification",
        "CalendarEvent",
        "StudioActivityLog",
    },
    "research": {n for n, _ in classes if n.startswith("Research")},
    "script": {n for n, _ in classes if n.startswith("Script")},
    "storyboard": {n for n, _ in classes if n.startswith("Storyboard")},
    "assets": {"StudioAsset", "AssetCollection", "AssetVersion", "AssetPermission"},
    "ai": {
        "AIGeneration",
        "AIPromptLibrary",
        "VoiceGeneration",
        "AIImageCollection",
        "AIImageCollectionItem",
        "AIImageVersion",
        "AIVideoVersion",
        "AIVoiceVersion",
        "AIMusicVersion",
        "AIShortsVersion",
        "AISEOVariant",
        "AITranslationVersion",
        "AITranslationMemory",
        "AICostBudget",
        "AICostAlert",
        "AIModelPolicy",
        "AIResponseCache",
        "AIMonthlyCostReport",
    },
    "publishing": {
        "PublishJob",
        "PublishAgentRun",
        "PublishWebhook",
        "PublishPlatformEvent",
        "ProductionPipelineRun",
    },
    "workflow": {"WorkflowDefinition", "WorkflowDefinitionVersion", "WorkflowTrigger"},
    "marketplace": {
        "MarketplaceAgent",
        "MarketplaceAgentVersion",
        "AgentInstallation",
        "AgentInstallationHistory",
    },
    "collaboration": {n for n, _ in classes if n.startswith("Collab")},
    "timeline": {n for n, _ in classes if n.startswith("Timeline")},
    "platform": {
        "StudioApiKey",
        "StudioFeatureFlag",
        "StudioSystemSetting",
        "StudioSecurityLog",
        "StudioBackup",
    },
    "plugins": {n for n, _ in classes if n.startswith("Plugin")},
    "gateway": {n for n, _ in classes if n.startswith("ApiGateway")},
    "enterprise": {n for n, _ in classes if n.startswith("Enterprise")},
}

HEADER = '''"""UNTOLD Studio — {title} models."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, StrEnum
from app.domain.studio.enums import (
    AIGenerationModule,
    AIGenerationStatus,
    ApprovalStatus,
    AssetType,
    PublishPlatform,
    PublishingStatus,
    ScriptStyle,
    StudioRole,
    TaskPriority,
    TaskStatus,
)

'''

out_dir = ROOT / "app/models/studio"
out_dir.mkdir(parents=True, exist_ok=True)

class_to_mod = {}
for mod, names in MODULES.items():
    for n in names:
        class_to_mod[n] = mod

mod_chunks: dict[str, list[str]] = {m: [] for m in MODULES}
unassigned = []
for idx, (name, start) in enumerate(classes):
    end = classes[idx + 1][1] if idx + 1 < len(classes) else len(lines)
    chunk = lines[start:end]
    mod = class_to_mod.get(name)
    if mod:
        mod_chunks[mod].extend(chunk)
        mod_chunks[mod].append("")
    else:
        unassigned.append(name)

if unassigned:
    raise SystemExit(f"Unassigned classes: {unassigned}")

TITLES = {
    "project": "project",
    "research": "research",
    "script": "script",
    "storyboard": "storyboard",
    "assets": "assets",
    "ai": "AI",
    "publishing": "publishing",
    "workflow": "workflow",
    "marketplace": "agent marketplace",
    "collaboration": "collaboration",
    "timeline": "timeline",
    "platform": "platform admin",
    "plugins": "plugins",
    "gateway": "API gateway",
    "enterprise": "enterprise security",
}

for mod, chunks in mod_chunks.items():
    if not chunks:
        continue
    body = "\n".join(chunks).rstrip() + "\n"
    path = out_dir / f"{mod}.py"
    path.write_text(HEADER.format(title=TITLES[mod]) + body, encoding="utf-8")
    print(f"Wrote {path.relative_to(ROOT)} ({body.count(chr(10))} lines)")

print("Done")
