"""Seed Studio productions and AI agent jobs."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.studio import AIAgentJob, Production

logger = logging.getLogger("untold")

PRODUCTIONS = [
    {
        "slug": "untold-virat-kohli",
        "title": "UNTOLD: Virat Kohli — The Untold Story",
        "stage": "research",
        "status": "active",
        "assignee": "Research Desk",
        "sources_count": 142,
        "version": 1,
    },
    {
        "slug": "untold-rise-of-mrbeast",
        "title": "UNTOLD: The Rise of MrBeast",
        "stage": "script",
        "status": "review",
        "assignee": "Writers Room",
        "sources_count": 89,
        "version": 3,
    },
    {
        "slug": "untold-steve-jobs",
        "title": "UNTOLD: Steve Jobs — Think Different",
        "stage": "script",
        "status": "draft",
        "assignee": "Writers Room",
        "sources_count": 210,
        "version": 1,
    },
    {
        "slug": "untold-ronaldo-legend",
        "title": "UNTOLD: Ronaldo — Making of a Legend",
        "stage": "editing",
        "status": "active",
        "assignee": "Post Production",
        "sources_count": 156,
        "version": 2,
    },
    {
        "slug": "untold-ai-revolution",
        "title": "UNTOLD: The AI Revolution",
        "stage": "publishing",
        "status": "scheduled",
        "assignee": "Growth Desk",
        "sources_count": 98,
        "version": 4,
    },
]

AGENT_JOB_SEEDS = [
    ("research", "Verify Kohli timeline sources", "queued"),
    ("research", "Cricket archive deep dive", "running"),
    ("fact", "Cross-check MrBeast revenue claims", "queued"),
    ("script", "Draft narration — Steve Jobs act 2", "queued"),
    ("script", "MrBeast cold open rewrite", "running"),
    ("storyboard", "Ronaldo match montage beats", "queued"),
    ("thumbnail", "A/B concepts — AI Revolution", "queued"),
    ("thumbnail", "CTR test — Kohli key art", "running"),
    ("seo", "Schema + tags — Ronaldo doc", "queued"),
    ("publishing", "Schedule YouTube premiere", "queued"),
    ("analytics", "Retention report — last 30d", "running"),
    ("voice", "Hindi narration draft — Jobs", "queued"),
    ("editing", "Pacing notes — Ronaldo cut 3", "queued"),
]


def seed_studio_data(db: Session) -> None:
    if db.query(Production).first():
        logger.info("Studio data already seeded, skipping")
        return

    logger.info("Seeding Studio productions and AI agent jobs...")
    production_map: dict[str, Production] = {}

    for p in PRODUCTIONS:
        prod = Production(**p)
        db.add(prod)
        production_map[p["slug"]] = prod
    db.flush()

    now = datetime.now(timezone.utc)
    for i, (agent_id, title, status) in enumerate(AGENT_JOB_SEEDS):
        slug_key = list(production_map.keys())[i % len(production_map)]
        job = AIAgentJob(
            agent_id=agent_id,
            production_id=production_map[slug_key].id,
            title=title,
            status=status,
            completed_at=now - timedelta(hours=i) if i % 4 == 0 else None,
        )
        if job.completed_at:
            job.status = "completed"
        db.add(job)

    # Extra completed jobs today for dashboard stats
    for agent_id, title in [
        ("research", "Completed: Messi rivalry sources"),
        ("thumbnail", "Completed: Jobs thumbnail v2"),
        ("seo", "Completed: Internal links pack"),
    ]:
        db.add(
            AIAgentJob(
                agent_id=agent_id,
                production_id=production_map["untold-steve-jobs"].id,
                title=title,
                status="completed",
                completed_at=now - timedelta(hours=2),
            )
        )

    db.commit()
    logger.info("Seeded %d productions, %d agent jobs", len(PRODUCTIONS), len(AGENT_JOB_SEEDS) + 3)
