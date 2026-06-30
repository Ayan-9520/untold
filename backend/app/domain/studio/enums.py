"""UNTOLD Studio — domain enumerations."""

import enum


class StudioRole(str, enum.Enum):
    ADMIN = "admin"
    PRODUCER = "producer"
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"
    DESIGNER = "designer"
    PUBLISHER = "publisher"
    VIEWER = "viewer"


class ProjectStage(str, enum.Enum):
    RESEARCH = "research"
    SCRIPT = "script"
    IMAGE = "image"
    VIDEO = "video"
    STORYBOARD = "storyboard"
    EDITING = "editing"
    REVIEW = "review"
    PUBLISHING = "publishing"
    COMPLETED = "completed"


from app.domain.workflow.steps import WORKFLOW_AGENT_IDS

PRODUCTION_PIPELINE_STEPS = WORKFLOW_AGENT_IDS


PROJECT_STAGES = [s.value for s in ProjectStage]


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    RESEARCH = "research"
    SCRIPTING = "scripting"
    STORYBOARD = "storyboard"
    PRODUCTION = "production"
    REVIEW = "review"
    PUBLISH = "publish"
    ARCHIVED = "archived"


class PublishingStatus(str, enum.Enum):
    UNPUBLISHED = "unpublished"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AIGenerationModule(str, enum.Enum):
    RESEARCH = "research"
    SCRIPT = "script"
    STORYBOARD = "storyboard"
    IMAGE = "image"
    VIDEO = "video"
    VOICE = "voice"
    MUSIC = "music"
    THUMBNAIL = "thumbnail"
    SEO = "seo"
    TRANSLATION = "translation"
    SHORTS = "shorts"


class AIGenerationStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AssetType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    FONT = "font"
    THUMBNAIL = "thumbnail"
    POSTER = "poster"


ASSET_FOLDERS = ("images", "videos", "audio", "documents", "thumbnails", "posters")


class ScriptStyle(str, enum.Enum):
    NETFLIX = "netflix"
    BBC = "bbc"
    ESPN = "espn"
    DOCUMENTARY = "documentary"


class PublishPlatform(str, enum.Enum):
    ORIGINALS = "originals"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    X = "x"
    THREADS = "threads"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    REALTIME = "realtime"
