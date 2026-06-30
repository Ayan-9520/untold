"""Enterprise Collaboration — realtime docs, presence, comments, files, conflicts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.domain.collaboration.helpers import (
    compute_etag,
    parse_mentions,
    presence_color,
    room_key,
)
from app.domain.studio.enums import ApprovalStatus, TaskStatus
from app.models import User
from app.models.studio import Production
from app.models.studio_platform import (
    CollabComment,
    CollabConflict,
    CollabDocument,
    CollabDocumentVersion,
    CollabPresence,
    CollabSharedFile,
    StudioActivityLog,
    StudioApproval,
    StudioNotification,
    StudioTask,
)
from app.schemas.collaboration import (
    CollabCommentCreate,
    CollabConflictResolve,
    CollabDocumentSave,
    CollabPresenceUpdate,
    CollabSharedFileCreate,
)
from app.services.studio_platform_service import StudioPlatformService


def _notify_collaboration(project_id: int, event: str, payload: dict) -> None:
    try:
        import asyncio

        from app.websocket.studio import manager

        asyncio.run(
            manager.broadcast_room(
                room_key(project_id, payload.get("resource_type", "project"), payload.get("resource_id")),
                {"type": "collaboration_event", "event": event, "project_id": project_id, **payload},
            )
        )
    except Exception:
        pass


class EnterpriseCollaborationService:
    @staticmethod
    def _document_dict(doc: CollabDocument, author: str | None = None) -> dict:
        return {
            "id": doc.id,
            "project_id": doc.project_id,
            "resource_type": doc.resource_type,
            "resource_id": doc.resource_id,
            "title": doc.title,
            "content": doc.content or {},
            "version": doc.version,
            "etag": doc.etag,
            "updated_by_id": doc.updated_by_id,
            "updated_by_name": author,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
        }

    @staticmethod
    def overview(db: Session, user: User, project_id: int) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        project = db.query(Production).filter(Production.id == project_id).first()
        if not project:
            raise NotFoundError("Project")

        cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
        presence_rows = (
            db.query(CollabPresence, User)
            .join(User, User.id == CollabPresence.user_id)
            .filter(CollabPresence.project_id == project_id, CollabPresence.last_heartbeat >= cutoff)
            .all()
        )
        presence = [
            {
                "user_id": p.user_id,
                "name": u.full_name or u.email,
                "status": p.status,
                "resource_type": p.resource_type,
                "resource_id": p.resource_id,
                "cursor": p.cursor,
                "color": p.color or presence_color(p.user_id),
                "last_heartbeat": p.last_heartbeat,
            }
            for p, u in presence_rows
        ]

        pending_tasks = (
            db.query(func.count(StudioTask.id))
            .filter(StudioTask.project_id == project_id, StudioTask.status != TaskStatus.DONE)
            .scalar()
            or 0
        )
        pending_approvals = (
            db.query(func.count(StudioApproval.id))
            .filter(StudioApproval.project_id == project_id, StudioApproval.status == ApprovalStatus.PENDING)
            .scalar()
            or 0
        )
        unread = (
            db.query(func.count(StudioNotification.id))
            .filter(StudioNotification.user_id == user.id, StudioNotification.is_read.is_(False))
            .scalar()
            or 0
        )

        activity = (
            db.query(StudioActivityLog, User)
            .join(User, User.id == StudioActivityLog.user_id)
            .filter(StudioActivityLog.project_id == project_id)
            .order_by(StudioActivityLog.created_at.desc())
            .limit(30)
            .all()
        )
        recent_activity = [
            {
                "id": a.id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "meta": a.meta,
                "user_name": u.full_name,
                "created_at": a.created_at,
            }
            for a, u in activity
        ]

        docs = (
            db.query(CollabDocument)
            .filter(CollabDocument.project_id == project_id)
            .order_by(CollabDocument.updated_at.desc())
            .all()
        )

        return {
            "project_id": project_id,
            "presence": presence,
            "pending_tasks": pending_tasks,
            "pending_approvals": pending_approvals,
            "unread_notifications": unread,
            "recent_activity": recent_activity,
            "documents": [EnterpriseCollaborationService._document_dict(d) for d in docs],
        }

    @staticmethod
    def get_or_create_document(
        db: Session,
        user: User,
        project_id: int,
        *,
        resource_type: str,
        resource_id: int | None,
        title: str,
        initial_content: dict | None = None,
    ) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "project.update")
        doc = (
            db.query(CollabDocument)
            .filter(
                CollabDocument.project_id == project_id,
                CollabDocument.resource_type == resource_type,
                CollabDocument.resource_id == resource_id,
            )
            .first()
        )
        if not doc:
            content = initial_content or {"text": ""}
            doc = CollabDocument(
                project_id=project_id,
                resource_type=resource_type,
                resource_id=resource_id,
                title=title,
                content=content,
                version=1,
                etag=compute_etag(content, 1),
                created_by_id=user.id,
                updated_by_id=user.id,
            )
            db.add(doc)
            db.flush()
            db.add(
                CollabDocumentVersion(
                    document_id=doc.id,
                    version=1,
                    content=content,
                    changelog="Initial version",
                    created_by_id=user.id,
                )
            )
            db.commit()
            db.refresh(doc)
        return EnterpriseCollaborationService._document_dict(doc, user.full_name)

    @staticmethod
    def get_document(db: Session, user: User, document_id: int) -> dict:
        doc = db.query(CollabDocument).filter(CollabDocument.id == document_id).first()
        if not doc:
            raise NotFoundError("Document")
        StudioPlatformService.require_permission(db, user, doc.project_id, "project.read")
        updater = db.query(User).filter(User.id == doc.updated_by_id).first() if doc.updated_by_id else None
        return EnterpriseCollaborationService._document_dict(doc, updater.full_name if updater else None)

    @staticmethod
    def save_document(db: Session, user: User, document_id: int, data: CollabDocumentSave) -> dict:
        doc = db.query(CollabDocument).filter(CollabDocument.id == document_id).first()
        if not doc:
            raise NotFoundError("Document")
        StudioPlatformService.require_permission(db, user, doc.project_id, "project.update")

        if doc.version != data.expected_version:
            conflict = CollabConflict(
                document_id=doc.id,
                base_version=data.expected_version,
                client_version=data.expected_version,
                server_version=doc.version,
                client_content=data.content,
                server_content=doc.content,
            )
            db.add(conflict)
            db.commit()
            db.refresh(conflict)
            return {
                "conflict": True,
                "conflict_id": conflict.id,
                "server_version": doc.version,
                "server_content": doc.content,
                "etag": doc.etag,
            }

        doc.version += 1
        doc.content = data.content
        doc.etag = compute_etag(data.content, doc.version)
        doc.updated_by_id = user.id
        doc.updated_at = datetime.now(timezone.utc)
        db.add(
            CollabDocumentVersion(
                document_id=doc.id,
                version=doc.version,
                content=data.content,
                changelog=data.changelog,
                created_by_id=user.id,
            )
        )
        StudioPlatformService.log_activity(
            db, user.id, "collab.document_saved", doc.project_id, "collab_document", doc.id,
            metadata={"version": doc.version},
        )
        db.commit()
        db.refresh(doc)
        result = EnterpriseCollaborationService._document_dict(doc, user.full_name)
        _notify_collaboration(
            doc.project_id,
            "document_saved",
            {"document_id": doc.id, "resource_type": doc.resource_type, "resource_id": doc.resource_id, "version": doc.version},
        )
        return result

    @staticmethod
    def resolve_conflict(db: Session, user: User, conflict_id: int, data: CollabConflictResolve) -> dict:
        conflict = db.query(CollabConflict).filter(CollabConflict.id == conflict_id).first()
        if not conflict:
            raise NotFoundError("Conflict")
        doc = db.query(CollabDocument).filter(CollabDocument.id == conflict.document_id).first()
        if not doc:
            raise NotFoundError("Document")
        StudioPlatformService.require_permission(db, user, doc.project_id, "project.update")

        if data.resolution == "accept_server":
            content = conflict.server_content or doc.content
        elif data.resolution == "accept_client":
            content = conflict.client_content or doc.content
        else:
            content = data.merged_content or conflict.client_content or doc.content

        doc.version += 1
        doc.content = content
        doc.etag = compute_etag(content, doc.version)
        doc.updated_by_id = user.id
        conflict.resolution = data.resolution
        conflict.resolved_content = content
        conflict.resolved_by_id = user.id
        conflict.resolved_at = datetime.now(timezone.utc)
        db.add(
            CollabDocumentVersion(
                document_id=doc.id,
                version=doc.version,
                content=content,
                changelog=f"Conflict resolved: {data.resolution}",
                created_by_id=user.id,
            )
        )
        StudioPlatformService.log_activity(
            db, user.id, "collab.conflict_resolved", doc.project_id, "collab_conflict", conflict.id
        )
        db.commit()
        return EnterpriseCollaborationService._document_dict(doc, user.full_name)

    @staticmethod
    def list_versions(db: Session, user: User, document_id: int) -> list[dict]:
        doc = db.query(CollabDocument).filter(CollabDocument.id == document_id).first()
        if not doc:
            raise NotFoundError("Document")
        StudioPlatformService.require_permission(db, user, doc.project_id, "project.read")
        rows = (
            db.query(CollabDocumentVersion, User)
            .outerjoin(User, User.id == CollabDocumentVersion.created_by_id)
            .filter(CollabDocumentVersion.document_id == document_id)
            .order_by(CollabDocumentVersion.version.desc())
            .all()
        )
        return [
            {
                "id": v.id,
                "version": v.version,
                "changelog": v.changelog,
                "created_by_name": u.full_name if u else None,
                "created_at": v.created_at,
            }
            for v, u in rows
        ]

    @staticmethod
    def restore_version(db: Session, user: User, document_id: int, version: int) -> dict:
        doc = db.query(CollabDocument).filter(CollabDocument.id == document_id).first()
        if not doc:
            raise NotFoundError("Document")
        StudioPlatformService.require_permission(db, user, doc.project_id, "project.update")
        snap = (
            db.query(CollabDocumentVersion)
            .filter(CollabDocumentVersion.document_id == document_id, CollabDocumentVersion.version == version)
            .first()
        )
        if not snap:
            raise NotFoundError("Version")
        return EnterpriseCollaborationService.save_document(
            db,
            user,
            document_id,
            CollabDocumentSave(content=snap.content, expected_version=doc.version, changelog=f"Restored v{version}"),
        )

    @staticmethod
    def heartbeat_presence(db: Session, user: User, project_id: int, data: CollabPresenceUpdate) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        row = (
            db.query(CollabPresence)
            .filter(
                CollabPresence.user_id == user.id,
                CollabPresence.project_id == project_id,
                CollabPresence.resource_type == data.resource_type,
                CollabPresence.resource_id == data.resource_id,
            )
            .first()
        )
        now = datetime.now(timezone.utc)
        color = presence_color(user.id)
        if not row:
            row = CollabPresence(
                user_id=user.id,
                project_id=project_id,
                resource_type=data.resource_type,
                resource_id=data.resource_id,
                status=data.status,
                cursor=data.cursor,
                color=color,
                last_heartbeat=now,
            )
            db.add(row)
        else:
            row.status = data.status
            row.cursor = data.cursor
            row.last_heartbeat = now
        db.commit()

        payload = {
            "user_id": user.id,
            "name": user.full_name or user.email,
            "status": data.status,
            "resource_type": data.resource_type,
            "resource_id": data.resource_id,
            "cursor": data.cursor,
            "color": color,
        }
        _notify_collaboration(project_id, "presence", payload)
        return payload

    @staticmethod
    def list_presence(db: Session, user: User, project_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=2)
        rows = (
            db.query(CollabPresence, User)
            .join(User, User.id == CollabPresence.user_id)
            .filter(CollabPresence.project_id == project_id, CollabPresence.last_heartbeat >= cutoff)
            .all()
        )
        return [
            {
                "user_id": p.user_id,
                "name": u.full_name or u.email,
                "status": p.status,
                "resource_type": p.resource_type,
                "resource_id": p.resource_id,
                "cursor": p.cursor,
                "color": p.color or presence_color(p.user_id),
            }
            for p, u in rows
        ]

    @staticmethod
    def list_comments(
        db: Session,
        user: User,
        project_id: int,
        *,
        resource_type: str | None = None,
        resource_id: int | None = None,
    ) -> list[dict]:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        q = db.query(CollabComment, User).join(User, User.id == CollabComment.user_id).filter(
            CollabComment.project_id == project_id
        )
        if resource_type:
            q = q.filter(CollabComment.resource_type == resource_type)
        if resource_id is not None:
            q = q.filter(CollabComment.resource_id == resource_id)
        rows = q.order_by(CollabComment.created_at.asc()).limit(200).all()
        return [
            {
                "id": c.id,
                "project_id": c.project_id,
                "resource_type": c.resource_type,
                "resource_id": c.resource_id,
                "parent_id": c.parent_id,
                "user_id": c.user_id,
                "author_name": u.full_name,
                "content": c.content,
                "mentions": c.mentions or [],
                "anchor": c.anchor,
                "resolved": c.resolved,
                "created_at": c.created_at,
            }
            for c, u in rows
        ]

    @staticmethod
    def add_comment(db: Session, user: User, project_id: int, data: CollabCommentCreate) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "project.update")
        mentions = parse_mentions(data.content)
        comment = CollabComment(
            project_id=project_id,
            resource_type=data.resource_type,
            resource_id=data.resource_id,
            parent_id=data.parent_id,
            user_id=user.id,
            content=data.content,
            mentions=mentions,
            anchor=data.anchor,
        )
        db.add(comment)
        db.flush()

        for uid in mentions:
            if uid != user.id:
                StudioPlatformService.notify(
                    db,
                    uid,
                    "mention",
                    f"{user.full_name} mentioned you",
                    data.content[:200],
                    {"project_id": project_id, "comment_id": comment.id},
                )

        StudioPlatformService.log_activity(
            db, user.id, "collab.comment_added", project_id, "collab_comment", comment.id
        )
        db.commit()
        db.refresh(comment)
        try:
            from app.domain.plugins.registry import PluginEventBus

            PluginEventBus.emit(
                db,
                "collab.comment.created",
                {"comment_id": comment.id, "project_id": project_id, "author_id": user.id},
                user_id=user.id,
                commit=True,
            )
        except Exception:
            pass
        result = {
            "id": comment.id,
            "project_id": comment.project_id,
            "resource_type": comment.resource_type,
            "resource_id": comment.resource_id,
            "parent_id": comment.parent_id,
            "user_id": comment.user_id,
            "author_name": user.full_name,
            "content": comment.content,
            "mentions": mentions,
            "anchor": comment.anchor,
            "resolved": comment.resolved,
            "created_at": comment.created_at,
        }
        _notify_collaboration(
            project_id,
            "comment_added",
            {"comment_id": comment.id, "resource_type": data.resource_type, "resource_id": data.resource_id},
        )
        return result

    @staticmethod
    def resolve_comment(db: Session, user: User, comment_id: int) -> dict:
        comment = db.query(CollabComment).filter(CollabComment.id == comment_id).first()
        if not comment:
            raise NotFoundError("Comment")
        StudioPlatformService.require_permission(db, user, comment.project_id, "project.update")
        comment.resolved = True
        db.commit()
        return {"id": comment.id, "resolved": True}

    @staticmethod
    def list_shared_files(db: Session, user: User, project_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        rows = (
            db.query(CollabSharedFile, User)
            .join(User, User.id == CollabSharedFile.shared_by_id)
            .filter(CollabSharedFile.project_id == project_id)
            .order_by(CollabSharedFile.created_at.desc())
            .all()
        )
        return [
            {
                "id": f.id,
                "name": f.name,
                "url": f.url,
                "mime_type": f.mime_type,
                "size_bytes": f.size_bytes,
                "version": f.version,
                "permissions": f.permissions,
                "shared_by_name": u.full_name,
                "created_at": f.created_at,
            }
            for f, u in rows
        ]

    @staticmethod
    def share_file(db: Session, user: User, project_id: int, data: CollabSharedFileCreate) -> dict:
        StudioPlatformService.require_permission(db, user, project_id, "asset.upload")
        f = CollabSharedFile(
            project_id=project_id,
            name=data.name,
            url=data.url,
            r2_key=data.r2_key,
            mime_type=data.mime_type,
            size_bytes=data.size_bytes,
            permissions=data.permissions or {"view": True, "download": True},
            shared_by_id=user.id,
        )
        db.add(f)
        StudioPlatformService.log_activity(db, user.id, "collab.file_shared", project_id, "collab_file", f.id)
        db.flush()
        db.commit()
        db.refresh(f)
        result = {
            "id": f.id,
            "name": f.name,
            "url": f.url,
            "version": f.version,
            "created_at": f.created_at,
        }
        _notify_collaboration(project_id, "file_shared", {"file_id": f.id, "name": f.name})
        return result

    @staticmethod
    def list_tasks(db: Session, user: User, project_id: int) -> list[dict]:
        tasks = StudioPlatformService.list_project_tasks(db, user, project_id)
        return [
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "status": t.status.value if hasattr(t.status, "value") else str(t.status),
                "priority": t.priority.value if hasattr(t.priority, "value") else str(t.priority),
                "assignee_id": t.assignee_id,
                "due_date": t.due_date,
                "created_at": t.created_at,
            }
            for t in tasks
        ]

    @staticmethod
    def list_approvals(db: Session, user: User, project_id: int) -> list[dict]:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        rows = (
            db.query(StudioApproval, User)
            .join(User, User.id == StudioApproval.requested_by_id)
            .filter(StudioApproval.project_id == project_id)
            .order_by(StudioApproval.created_at.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "id": a.id,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "status": a.status.value if hasattr(a.status, "value") else str(a.status),
                "notes": a.notes,
                "requested_by_name": u.full_name,
                "created_at": a.created_at,
                "resolved_at": a.resolved_at,
            }
            for a, u in rows
        ]

    @staticmethod
    def activity_feed(db: Session, user: User, project_id: int, limit: int = 50) -> list[dict]:
        StudioPlatformService.require_permission(db, user, project_id, "project.read")
        rows = (
            db.query(StudioActivityLog, User)
            .join(User, User.id == StudioActivityLog.user_id)
            .filter(StudioActivityLog.project_id == project_id)
            .order_by(StudioActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": a.id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "meta": a.meta,
                "user_name": u.full_name,
                "created_at": a.created_at,
            }
            for a, u in rows
        ]

    @staticmethod
    def list_notifications(db: Session, user: User, limit: int = 30) -> list[dict]:
        rows = (
            db.query(StudioNotification)
            .filter(StudioNotification.user_id == user.id)
            .order_by(StudioNotification.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": n.id,
                "notification_type": n.notification_type,
                "title": n.title,
                "body": n.body,
                "is_read": n.is_read,
                "data": n.data,
                "created_at": n.created_at,
            }
            for n in rows
        ]

    @staticmethod
    def mark_notification_read(db: Session, user: User, notification_id: int) -> dict:
        note = (
            db.query(StudioNotification)
            .filter(StudioNotification.id == notification_id, StudioNotification.user_id == user.id)
            .first()
        )
        if not note:
            raise NotFoundError("Notification")
        note.is_read = True
        db.commit()
        return {"id": note.id, "is_read": True}
