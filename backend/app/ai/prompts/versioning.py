"""Prompt template versioning backed by ai_prompt_library."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.studio import AIPromptLibrary


class PromptVersionService:
    """Resolve and version prompt templates without breaking existing library rows."""

    @staticmethod
    def prompt_key(module: str, title: str) -> str:
        slug = title.lower().strip().replace(" ", "-")[:120]
        return f"{module}:{slug}"

    @staticmethod
    def get_current(db: Session, module: str, title: str) -> AIPromptLibrary | None:
        key = PromptVersionService.prompt_key(module, title)
        q = db.query(AIPromptLibrary).filter(AIPromptLibrary.module == module)
        if hasattr(AIPromptLibrary, "prompt_key"):
            q = q.filter(AIPromptLibrary.prompt_key == key)
        else:
            q = q.filter(AIPromptLibrary.title == title)
        if hasattr(AIPromptLibrary, "is_current"):
            q = q.filter(AIPromptLibrary.is_current.is_(True))
        return q.order_by(AIPromptLibrary.id.desc()).first()

    @staticmethod
    def render(template: str, variables: dict | None = None) -> str:
        out = template
        for key, value in (variables or {}).items():
            out = out.replace(f"{{{key}}}", str(value))
        return out

    @staticmethod
    def resolve_text(
        db: Session,
        module: str,
        title: str,
        *,
        variables: dict | None = None,
        fallback: str | None = None,
    ) -> tuple[str, str | None]:
        """Return (rendered_prompt, version_label)."""
        row = PromptVersionService.get_current(db, module, title)
        if not row:
            return fallback or "", None
        version_label = None
        if hasattr(row, "version"):
            version_label = f"v{row.version}"
        text = PromptVersionService.render(row.prompt_template, variables)
        return text, version_label

    @staticmethod
    def create_version(
        db: Session,
        *,
        module: str,
        title: str,
        prompt_template: str,
        description: str | None = None,
        parameters: dict | None = None,
        created_by_id: int | None = None,
        make_current: bool = True,
    ) -> AIPromptLibrary:
        key = PromptVersionService.prompt_key(module, title)
        next_version = 1
        if hasattr(AIPromptLibrary, "version"):
            latest = (
                db.query(func.max(AIPromptLibrary.version))
                .filter(AIPromptLibrary.module == module, AIPromptLibrary.prompt_key == key)
                .scalar()
            )
            next_version = int(latest or 0) + 1
            if make_current and hasattr(AIPromptLibrary, "is_current"):
                db.query(AIPromptLibrary).filter(
                    AIPromptLibrary.module == module,
                    AIPromptLibrary.prompt_key == key,
                    AIPromptLibrary.is_current.is_(True),
                ).update({"is_current": False})

        kwargs: dict = {
            "title": title,
            "module": module,
            "prompt_template": prompt_template,
            "description": description,
            "parameters": parameters,
            "created_by_id": created_by_id,
        }
        if hasattr(AIPromptLibrary, "prompt_key"):
            kwargs["prompt_key"] = key
        if hasattr(AIPromptLibrary, "version"):
            kwargs["version"] = next_version
        if hasattr(AIPromptLibrary, "is_current"):
            kwargs["is_current"] = make_current

        row = AIPromptLibrary(**kwargs)
        db.add(row)
        db.flush()
        return row

    @staticmethod
    def list_versions(db: Session, module: str, title: str) -> list[AIPromptLibrary]:
        key = PromptVersionService.prompt_key(module, title)
        q = db.query(AIPromptLibrary).filter(AIPromptLibrary.module == module)
        if hasattr(AIPromptLibrary, "prompt_key"):
            q = q.filter(AIPromptLibrary.prompt_key == key)
        else:
            q = q.filter(AIPromptLibrary.title == title)
        if hasattr(AIPromptLibrary, "version"):
            return q.order_by(AIPromptLibrary.version.desc()).all()
        return q.order_by(AIPromptLibrary.id.desc()).all()
