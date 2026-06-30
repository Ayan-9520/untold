"""Script Studio — rich editor workspace, AI tools, approval, export."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.domain.studio.enums import ApprovalStatus, ScriptStyle
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import (
    Script,
    ScriptStudioComment,
    ScriptVersion,
    StudioApproval,
)
from app.schemas.script_studio import (
    ScriptAIRequest,
    ScriptApprovalRequest,
    ScriptCommentCreate,
    ScriptVersionSave,
    ScriptWorkspaceAutoSave,
)
from app.services.studio_platform_service import StudioPlatformService


class ScriptStudioService:
    @staticmethod
    def _get_script(db: Session, script_id: int) -> Script:
        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise NotFoundError("Script")
        return script

    @staticmethod
    def _current_version(db: Session, script: Script) -> ScriptVersion:
        if script.current_version_id:
            version = db.query(ScriptVersion).filter(ScriptVersion.id == script.current_version_id).first()
            if version:
                return version
        version = (
            db.query(ScriptVersion)
            .filter(ScriptVersion.script_id == script.id)
            .order_by(ScriptVersion.version.desc())
            .first()
        )
        if not version:
            raise NotFoundError("Script version")
        return version

    @staticmethod
    def _default_content(project_title: str, style: ScriptStyle) -> str:
        return (
            f"<h1>{html.escape(project_title)}</h1>"
            f"<p><em>Style: {style.value}</em></p>"
            "<h2>Opening</h2><p>Narrator: </p>"
            "<h2>Act I</h2><p></p>"
            "<h2>Closing</h2><p></p>"
        )

    @staticmethod
    def get_or_create_workspace(db: Session, user: User, project_id: int) -> Script:
        StudioPlatformService.require_permission(db, user, project_id, "script.edit")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")
        script = (
            db.query(Script)
            .filter(Script.project_id == project_id)
            .order_by(Script.created_at.desc())
            .first()
        )
        if not script:
            script = Script(project_id=project_id, title=project.title)
            db.add(script)
            db.flush()
            version = ScriptVersion(
                script_id=script.id,
                version=1,
                content=ScriptStudioService._default_content(project.title, ScriptStyle.DOCUMENTARY),
                style=ScriptStyle.DOCUMENTARY,
                created_by_id=user.id,
            )
            db.add(version)
            db.flush()
            script.current_version_id = version.id
            StudioPlatformService.log_activity(db, user.id, "script.created", project_id, "script", script.id)
            db.commit()
            db.refresh(script)
        return script

    @staticmethod
    def _collaborators_list(script: Script) -> list[dict]:
        raw = script.active_collaborators or []
        return raw if isinstance(raw, list) else []

    @staticmethod
    def get_full_workspace(db: Session, user: User, script_id: int) -> dict:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "project.read")
        project = db.query(Production).filter(Production.id == script.project_id).first()
        current = ScriptStudioService._current_version(db, script)
        last_editor = None
        if script.last_edited_by_id:
            last_editor = db.query(User).filter(User.id == script.last_edited_by_id).first()

        versions = (
            db.query(ScriptVersion, User)
            .join(User, User.id == ScriptVersion.created_by_id)
            .filter(ScriptVersion.script_id == script_id)
            .order_by(ScriptVersion.version.desc())
            .limit(30)
            .all()
        )
        comments = (
            db.query(ScriptStudioComment, User)
            .join(User, User.id == ScriptStudioComment.user_id)
            .filter(ScriptStudioComment.script_id == script_id)
            .order_by(ScriptStudioComment.created_at.desc())
            .all()
        )
        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "script",
                StudioApproval.entity_id == script_id,
            )
            .order_by(StudioApproval.created_at.desc())
            .first()
        )

        from app.services.script_agent_service import ScriptAgentService

        ai_history = ScriptAgentService.list_history(db, user, script_id, limit=30)
        providers = ScriptAgentService.list_providers()

        return {
            "workspace": {
                "id": script.id,
                "project_id": script.project_id,
                "project_title": project.title if project else None,
                "title": script.title,
                "status": script.status,
                "content": current.content or "",
                "style": current.style,
                "content_version": script.content_version,
                "current_version": current.version,
                "last_auto_saved_at": script.last_auto_saved_at,
                "last_edited_by_id": script.last_edited_by_id,
                "last_edited_by_name": last_editor.full_name if last_editor else None,
                "approved_at": script.approved_at,
                "active_collaborators": ScriptStudioService._collaborators_list(script),
                "created_at": script.created_at,
                "updated_at": script.updated_at,
            },
            "versions": [
                {
                    "id": v.id,
                    "version": v.version,
                    "content": v.content,
                    "style": v.style,
                    "snapshot_label": v.snapshot_label,
                    "created_by_id": v.created_by_id,
                    "author_name": u.full_name,
                    "created_at": v.created_at,
                }
                for v, u in versions
            ],
            "comments": [
                {
                    "id": c.id,
                    "user_id": c.user_id,
                    "author_name": u.full_name,
                    "content": c.content,
                    "created_at": c.created_at,
                }
                for c, u in comments
            ],
            "approval": (
                {
                    "id": approval.id,
                    "status": approval.status.value if hasattr(approval.status, "value") else str(approval.status),
                    "notes": approval.notes,
                    "requested_by_id": approval.requested_by_id,
                    "approver_id": approval.approver_id,
                    "created_at": approval.created_at,
                    "resolved_at": approval.resolved_at,
                }
                if approval
                else None
            ),
            "ai_history": ai_history,
            "providers": providers,
        }

    @staticmethod
    def _touch_collaborator(script: Script, user: User) -> None:
        now = datetime.now(timezone.utc).isoformat()
        collabs = [c for c in ScriptStudioService._collaborators_list(script) if c.get("user_id") != user.id]
        collabs.insert(
            0,
            {"user_id": user.id, "name": user.full_name, "last_seen": now},
        )
        script.active_collaborators = collabs[:12]

    @staticmethod
    def auto_save(db: Session, user: User, script_id: int, data: ScriptWorkspaceAutoSave) -> Script:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "script.edit")
        if data.expected_version is not None and data.expected_version != script.content_version:
            raise ConflictError("Script was updated by another collaborator. Refresh to merge changes.")
        current = ScriptStudioService._current_version(db, script)
        current.content = data.content
        if data.style is not None:
            current.style = data.style
        script.content_version = (script.content_version or 0) + 1
        script.last_auto_saved_at = datetime.now(timezone.utc)
        script.last_edited_by_id = user.id
        ScriptStudioService._touch_collaborator(script, user)
        db.commit()
        db.refresh(script)
        return script

    @staticmethod
    def heartbeat(db: Session, user: User, script_id: int) -> list[dict]:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "project.read")
        ScriptStudioService._touch_collaborator(script, user)
        db.commit()
        db.refresh(script)
        return ScriptStudioService._collaborators_list(script)

    @staticmethod
    def save_version(db: Session, user: User, script_id: int, data: ScriptVersionSave | None = None) -> ScriptVersion:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "script.edit")
        current = ScriptStudioService._current_version(db, script)
        latest = (
            db.query(func.max(ScriptVersion.version))
            .filter(ScriptVersion.script_id == script_id)
            .scalar()
            or 0
        )
        version = ScriptVersion(
            script_id=script_id,
            version=int(latest) + 1,
            content=current.content,
            style=current.style,
            snapshot_label=data.snapshot_label if data else None,
            created_by_id=user.id,
        )
        db.add(version)
        db.flush()
        script.current_version_id = version.id
        project = db.query(Production).filter(Production.id == script.project_id).first()
        if project:
            project.version = version.version
        StudioPlatformService.log_activity(db, user.id, "script.version_saved", script.project_id, "script", script.id)
        db.commit()
        db.refresh(version)
        return version

    @staticmethod
    def restore_version(db: Session, user: User, script_id: int, version_id: int) -> Script:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "script.edit")
        version = (
            db.query(ScriptVersion)
            .filter(ScriptVersion.id == version_id, ScriptVersion.script_id == script_id)
            .first()
        )
        if not version:
            raise NotFoundError("Version")
        current = ScriptStudioService._current_version(db, script)
        current.content = version.content
        current.style = version.style
        script.content_version = (script.content_version or 0) + 1
        script.last_auto_saved_at = datetime.now(timezone.utc)
        script.last_edited_by_id = user.id
        ScriptStudioService.save_version(db, user, script_id, ScriptVersionSave(snapshot_label=f"Restored from v{version.version}"))
        db.refresh(script)
        return script

    @staticmethod
    def add_comment(db: Session, user: User, script_id: int, data: ScriptCommentCreate) -> dict:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "script.edit")
        comment = ScriptStudioComment(script_id=script_id, user_id=user.id, content=data.content)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return {
            "id": comment.id,
            "user_id": comment.user_id,
            "author_name": user.full_name,
            "content": comment.content,
            "created_at": comment.created_at,
        }

    @staticmethod
    def request_approval(db: Session, user: User, script_id: int, data: ScriptApprovalRequest) -> StudioApproval:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "script.edit")
        script.status = "review"
        approval = StudioApproval(
            project_id=script.project_id,
            entity_type="script",
            entity_id=script.id,
            requested_by_id=user.id,
            status=ApprovalStatus.PENDING,
            notes=data.notes,
        )
        db.add(approval)
        StudioPlatformService.log_activity(db, user.id, "script.approval_requested", script.project_id, "script", script.id)
        db.commit()
        db.refresh(approval)
        return approval

    @staticmethod
    def approve_script(db: Session, user: User, script_id: int, data: ScriptApprovalRequest | None = None) -> Script:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "script.approve")
        script.status = "approved"
        script.approved_at = datetime.now(timezone.utc)
        script.approved_by_id = user.id
        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "script",
                StudioApproval.entity_id == script_id,
                StudioApproval.status == ApprovalStatus.PENDING,
            )
            .order_by(StudioApproval.created_at.desc())
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.APPROVED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)
            if data and data.notes:
                approval.notes = data.notes
        else:
            db.add(
                StudioApproval(
                    project_id=script.project_id,
                    entity_type="script",
                    entity_id=script.id,
                    requested_by_id=user.id,
                    approver_id=user.id,
                    status=ApprovalStatus.APPROVED,
                    notes=data.notes if data else None,
                    resolved_at=datetime.now(timezone.utc),
                )
            )
        StudioPlatformService.log_activity(db, user.id, "script.approved", script.project_id, "script", script.id)
        db.commit()
        db.refresh(script)
        return script

    @staticmethod
    def reject_script(db: Session, user: User, script_id: int, data: ScriptApprovalRequest | None = None) -> Script:
        script = ScriptStudioService._get_script(db, script_id)
        StudioPlatformService.require_permission(db, user, script.project_id, "script.approve")
        script.status = "draft"
        approval = (
            db.query(StudioApproval)
            .filter(
                StudioApproval.entity_type == "script",
                StudioApproval.entity_id == script_id,
                StudioApproval.status == ApprovalStatus.PENDING,
            )
            .order_by(StudioApproval.created_at.desc())
            .first()
        )
        if approval:
            approval.status = ApprovalStatus.REJECTED
            approval.approver_id = user.id
            approval.resolved_at = datetime.now(timezone.utc)
            if data and data.notes:
                approval.notes = data.notes
        StudioPlatformService.log_activity(db, user.id, "script.rejected", script.project_id, "script", script.id)
        db.commit()
        db.refresh(script)
        return script

    @staticmethod
    def _html_to_markdown(content: str) -> str:
        text = content or ""
        text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"# \1\n\n", text, flags=re.I | re.S)
        text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"## \1\n\n", text, flags=re.I | re.S)
        text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"### \1\n\n", text, flags=re.I | re.S)
        text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.I | re.S)
        text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.I | re.S)
        text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.I | re.S)
        text = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.I | re.S)
        text = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1\n", text, flags=re.I | re.S)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
        text = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", text, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", "", text)
        return html.unescape(re.sub(r"\n{3,}", "\n\n", text)).strip()

    @staticmethod
    def run_ai(db: Session, user: User, script_id: int, data: ScriptAIRequest) -> dict:
        from app.services.script_agent_service import ScriptAgentService

        return ScriptAgentService.run_agent(
            db,
            user,
            script_id,
            data.action,
            prompt=data.prompt,
            selection=data.selection,
            target_language=data.target_language,
            tone=data.tone,
            provider_id=data.provider,
            apply=data.apply,
        )

    @staticmethod
    def export_markdown(db: Session, user: User, script_id: int) -> str:
        full = ScriptStudioService.get_full_workspace(db, user, script_id)
        w = full["workspace"]
        md = ScriptStudioService._html_to_markdown(w["content"])
        lines = [
            f"# {w['title']}",
            "",
            f"*Project: {w.get('project_title', '')} · v{w['current_version']} · {w['style']}*",
            "",
            md,
            "",
        ]
        if full["comments"]:
            lines.extend(["## Comments", ""])
            for c in full["comments"]:
                lines.append(f"- **{c['author_name']}**: {c['content']}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def export_html_document(db: Session, user: User, script_id: int, title_suffix: str = "Script") -> str:
        full = ScriptStudioService.get_full_workspace(db, user, script_id)
        w = full["workspace"]
        body = w["content"] or ""
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{html.escape(w['title'])}</title>
<style>
body{{font-family:Georgia,serif;max-width:800px;margin:40px auto;padding:0 24px;line-height:1.65;color:#111}}
h1,h2,h3{{color:#1a1a1a}} em{{color:#555}}
</style></head>
<body>
<h1>{html.escape(w['title'])}</h1>
<p><em>{html.escape(w.get('project_title') or '')} · Version {w['current_version']} · {w['style']}</em></p>
{body}
</body></html>"""

    @staticmethod
    def export_word_html(db: Session, user: User, script_id: int) -> str:
        html_doc = ScriptStudioService.export_html_document(db, user, script_id)
        body_match = re.search(r"<body[^>]*>(.*)</body>", html_doc, re.S | re.I)
        body = body_match.group(1).strip() if body_match else html_doc
        return (
            '<html xmlns:o="urn:schemas-microsoft-com:office:office" '
            'xmlns:w="urn:schemas-microsoft-com:office:word">'
            "<head><meta charset='utf-8'><title>Script</title></head>"
            f"<body>{body}</body></html>"
        )
