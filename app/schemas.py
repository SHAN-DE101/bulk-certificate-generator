from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecipientInput(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class CreateJobRequest(BaseModel):
    event_name: str = Field(..., min_length=2, max_length=150)
    issue_date: str = Field(..., description="Format: YYYY-MM-DD")
    recipients: List[RecipientInput] = Field(..., min_length=1)


class CertificateItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    recipient_name: str
    recipient_email: str
    status: str
    certificate_url: Optional[str] = None
    error_message: Optional[str] = None


class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    event_name: str
    issue_date: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    items: List[CertificateItemResponse]
