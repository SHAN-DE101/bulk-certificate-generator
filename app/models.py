import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ItemStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class CertificateJob(Base):
    __tablename__ = "certificate_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_name = Column(String, nullable=False)
    issue_date = Column(String, nullable=False)
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipients = relationship("CertificateItem", back_populates="job", cascade="all, delete-orphan")


class CertificateItem(Base):
    __tablename__ = "certificate_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("certificate_jobs.id"), nullable=False)
    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    status = Column(Enum(ItemStatus), default=ItemStatus.PENDING)
    certificate_url = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    job = relationship("CertificateJob", back_populates="recipients")
