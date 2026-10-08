import os
from sqlalchemy.orm import Session
from .database import SessionLocal
from .generator import generate_certificate_image
from .models import CertificateItem, CertificateJob, ItemStatus, JobStatus


def process_bulk_certificates(job_id: str):
    db: Session = SessionLocal()
    try:
        job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
        if not job:
            return

        job.status = JobStatus.PROCESSING
        job.success_count = 0
        job.failed_count = 0
        db.commit()

        for item in job.recipients:
            try:
                # Trigger isolated failure test case
                if "trigger-failure" in item.recipient_name.lower():
                    raise ValueError("Simulated failure for individual item handling.")

                file_path = generate_certificate_image(
                    item_id=item.id,
                    recipient_name=item.recipient_name,
                    event_name=job.event_name,
                    issue_date=job.issue_date,
                )

                item.certificate_url = f"/api/certificates/{item.id}/download"
                item.status = ItemStatus.SUCCESS
                job.success_count += 1
            except Exception as exc:
                item.status = ItemStatus.FAILED
                item.error_message = str(exc)
                job.failed_count += 1

            db.commit()

        job.status = JobStatus.COMPLETED
        db.commit()
    finally:
        db.close()
