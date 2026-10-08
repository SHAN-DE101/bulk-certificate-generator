import os
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import CertificateItem, CertificateJob
from .schemas import CreateJobRequest, JobStatusResponse
from .service import process_bulk_certificates

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator API", version="1.0.0")


@app.post("/api/certificates/generate", response_model=JobStatusResponse, status_code=202)
def create_generation_job(
    request: CreateJobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = CertificateJob(
        event_name=request.event_name,
        issue_date=request.issue_date,
        total_count=len(request.recipients),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    for recipient in request.recipients:
        item = CertificateItem(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
        )
        db.add(item)
    db.commit()
    db.refresh(job)

    # Hand off to background worker
    background_tasks.add_task(process_bulk_certificates, job.id)

    return JobStatusResponse(
        job_id=job.id,
        event_name=job.event_name,
        issue_date=job.issue_date,
        status=job.status.value,
        total_count=job.total_count,
        success_count=job.success_count,
        failed_count=job.failed_count,
        items=job.recipients,
    )


@app.get("/api/certificates/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.id,
        event_name=job.event_name,
        issue_date=job.issue_date,
        status=job.status.value,
        total_count=job.total_count,
        success_count=job.success_count,
        failed_count=job.failed_count,
        items=job.recipients,
    )


@app.get("/api/certificates/{item_id}/download")
def download_certificate(item_id: str, db: Session = Depends(get_db)):
    item = db.query(CertificateItem).filter(CertificateItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Certificate item not found")

    file_path = os.path.join("certificates", f"{item_id}.png")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found on disk")

    return FileResponse(file_path, media_type="image/png", filename=f"certificate_{item_id}.png")
