from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_current_admin
from app.db.session import get_db
from app.models import User
from app.schemas.monetization import MagazineDownloadResponse
from app.services.magazine_monetization_service import MagazineMonetizationService
from app.services.magazine_service import MagazineAgentService

router = APIRouter(prefix="/magazine", tags=["Magazine — UNTOLD E-Magazine"])


class GenerateIssueRequest(BaseModel):
    theme: str = "General Edition"
    quarter: str = "Q1"
    year: int = 2026


@router.get("/issues")
def list_magazine_issues(db: Session = Depends(get_db)):
    items = MagazineAgentService.list_issues(db)
    return {"items": items, "total": len(items)}


@router.get("/issues/{issue_id}")
def get_magazine_issue(issue_id: str, db: Session = Depends(get_db)):
    issue = MagazineAgentService.get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.get("/featured")
def get_featured_issue(db: Session = Depends(get_db)):
    issues = MagazineAgentService.list_issues(db)
    if not issues:
        raise HTTPException(status_code=404, detail="No issues")
    featured = next((i for i in issues if i.get("sample") or i.get("featured")), issues[0])
    return featured


@router.get("/free-sample")
def get_free_sample_issue(db: Session = Depends(get_db)):
    issues = MagazineAgentService.list_issues(db)
    sample = next((i for i in issues if i.get("access") == "free" or i.get("sample")), None)
    if not sample:
        raise HTTPException(status_code=404, detail="No free sample available")
    return sample


@router.post("/issues/{issue_id}/download", response_model=MagazineDownloadResponse)
def download_magazine_issue(
    issue_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ip = request.client.host if request.client else None
    result = MagazineMonetizationService.create_download(db, current_user, issue_id, ip)
    return MagazineDownloadResponse(**result)


@router.get("/admin/jobs")
def list_magazine_jobs(db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    jobs = MagazineAgentService.list_jobs(db)
    return {"items": jobs, "total": len(jobs)}


@router.post("/admin/generate")
def generate_magazine_issue(
    data: GenerateIssueRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return MagazineAgentService.generate_issue(db, data.theme, data.quarter, data.year)


@router.post("/admin/jobs/{job_id}/advance")
def advance_magazine_job(job_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    job = MagazineAgentService.advance_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/admin/jobs/{job_id}/approve")
def approve_magazine_issue(job_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    result = MagazineAgentService.approve_and_publish(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result
