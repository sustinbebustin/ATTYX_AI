from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4

class LeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    OPPORTUNITY = "opportunity"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class LeadSource(str, Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_CALL = "cold_call"
    SOCIAL = "social"
    OTHER = "other"

class CallAttempt(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    outcome: str
    notes: Optional[str] = None
    next_attempt_scheduled: Optional[datetime] = None

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Contact Information
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    
    # Lead Details
    status: LeadStatus = Field(default=LeadStatus.NEW)
    source: LeadSource
    interest_level: int = Field(ge=1, le=5)
    estimated_value: Optional[float] = None
    
    # Tracking
    call_attempts: List[CallAttempt] = Field(default_factory=list)
    last_contact: Optional[datetime] = None
    next_follow_up: Optional[datetime] = None
    assigned_agent_id: Optional[str] = None
    
    # Qualification Criteria
    budget_confirmed: bool = False
    authority_confirmed: bool = False
    need_confirmed: bool = False
    timeline_confirmed: bool = False
    
    # Custom Fields
    metadata: dict = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    def add_call_attempt(self, outcome: str, notes: Optional[str] = None, 
                        next_attempt: Optional[datetime] = None):
        attempt = CallAttempt(
            outcome=outcome,
            notes=notes,
            next_attempt_scheduled=next_attempt
        )
        self.call_attempts.append(attempt)
        self.last_contact = attempt.timestamp
        self.next_follow_up = next_attempt
        self.updated_at = datetime.utcnow()
        
    def update_status(self, new_status: LeadStatus):
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
    def is_qualified(self) -> bool:
        return all([
            self.budget_confirmed,
            self.authority_confirmed,
            self.need_confirmed,
            self.timeline_confirmed
        ])