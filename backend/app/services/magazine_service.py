"""UNTOLD E-Magazine — Magazine Editor AI Agent
Flow: Sports Data + News + UNTOLD Content → Editorial → Design → Publish
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger("untold")

WORKFLOW_STEPS = [
    {"id": "collecting", "label": "Collecting Data", "agent": "Data Collection Agent"},
    {"id": "writing", "label": "Writing", "agent": "Editorial AI Agent"},
    {"id": "designing", "label": "Designing", "agent": "Design AI Agent"},
    {"id": "publishing", "label": "Publishing", "agent": "Publishing Agent"},
    {"id": "ready", "label": "Ready", "agent": "Editor-in-Chief Approval"},
]

MOCK_ISSUES = [
    {
        "id": "uq-2026-q1",
        "title": "The Dhoni Era",
        "quarter": "Q1",
        "year": 2026,
        "theme": "IPL Special",
        "access": "free",
        "sample": True,
        "page_count": 52,
    }
]

MOCK_JOBS: list[dict] = []


class MagazineAgentService:
    @staticmethod
    def list_issues() -> list[dict]:
        return MOCK_ISSUES

    @staticmethod
    def get_issue(issue_id: str) -> dict | None:
        return next((i for i in MOCK_ISSUES if i["id"] == issue_id), None)

    @staticmethod
    def list_jobs() -> list[dict]:
        return MOCK_JOBS

    @staticmethod
    def generate_issue(theme: str, quarter: str, year: int) -> dict:
        job = {
            "id": f"job-{int(datetime.now(timezone.utc).timestamp())}",
            "theme": theme,
            "quarter": quarter,
            "year": year,
            "status": "collecting",
            "progress": 10,
            "steps": [{**s, "status": "pending"} for s in WORKFLOW_STEPS],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        job["steps"][0]["status"] = "processing"
        MOCK_JOBS.insert(0, job)
        logger.info("Magazine AI job started: %s %s %s — %s", quarter, year, theme, job["id"])
        return job

    @staticmethod
    def advance_job(job_id: str) -> dict | None:
        job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
        if not job:
            return None
        progress_map = {"collecting": 25, "writing": 50, "designing": 75, "publishing": 90, "ready": 100}
        order = ["collecting", "writing", "designing", "publishing", "ready"]
        idx = order.index(job["status"]) if job["status"] in order else 0
        if idx < len(order) - 1:
            job["status"] = order[idx + 1]
        job["progress"] = progress_map.get(job["status"], job["progress"])
        for i, step in enumerate(job["steps"]):
            if i < idx + 1:
                step["status"] = "completed"
            elif i == idx + 1:
                step["status"] = "processing"
            else:
                step["status"] = "pending"
        return job

    @staticmethod
    def approve_and_publish(job_id: str) -> dict | None:
        job = next((j for j in MOCK_JOBS if j["id"] == job_id), None)
        if not job:
            return None
        job["status"] = "ready"
        job["progress"] = 100
        for step in job["steps"]:
            step["status"] = "completed"
        issue = {
            "id": f"uq-{job['year']}-{job['quarter'].lower()}",
            "title": f"{job['theme']} — {job['quarter']} {job['year']}",
            "quarter": job["quarter"],
            "year": job["year"],
            "theme": job["theme"],
            "access": "paid",
            "page_count": 48,
        }
        MOCK_ISSUES.insert(0, issue)
        logger.info("Magazine published: %s", issue["id"])
        return {"job": job, "issue": issue}
