from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class NotificationServiceInterface(ABC):
    """Abstract interface for notification operations"""
    
    @abstractmethod
    async def send_slack_message(
        self,
        channel: str,
        message: str,
        lead_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send a message to a Slack channel"""
        pass
        
    @abstractmethod
    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send an email notification"""
        pass
        
    @abstractmethod
    async def notify_sales_team(self, message: str) -> bool:
        """Send notification to sales team channel"""
        pass
        
    @abstractmethod
    async def schedule_loss_review(
        self,
        lead_id: str,
        assigned_agent: str,
        loss_reason: str,
        estimated_value: float,
        qualification_status: bool,
        time_in_pipeline: int
    ) -> bool:
        """Schedule a loss review meeting and notify team members"""
        pass
