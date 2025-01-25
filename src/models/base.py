from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool = Field(default=True)
    message: str = Field(default="")
    data: Optional[Dict[str, Any]] = Field(default=None)
    errors: Optional[List[str]] = Field(default=None)

class AgentContext(BaseModel):
    """Context information for agent operations"""
    conversation_id: str = Field(...)
    user_id: str = Field(...)
    session_id: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

class KnowledgeItem(BaseModel):
    """Base model for knowledge base items"""
    id: str = Field(...)
    content: str = Field(...)
    embedding: List[float] = Field(...)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    category: str = Field(...)
    confidence: float = Field(default=1.0)

class AgentAction(BaseModel):
    """Model representing an action taken by an agent"""
    action_type: str = Field(...)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str = Field(...)
    context: AgentContext = Field(...)
    status: str = Field(default="pending")
    result: Optional[Dict[str, Any]] = Field(default=None)