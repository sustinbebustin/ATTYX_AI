from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from contextlib import AbstractAsyncContextManager
from datetime import datetime

class DatabaseServiceInterface(ABC):
    """Abstract interface for database operations"""
    
    @abstractmethod
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Create a new lead record"""
        pass
        
    @abstractmethod
    async def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing lead"""
        pass
        
    @abstractmethod
    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a lead by ID"""
        pass
        
    @abstractmethod
    async def get_agent_leads(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all leads assigned to an agent"""
        pass
        
    @abstractmethod
    async def track_metric(self, metric_data: Dict[str, Any]) -> bool:
        """Track a metric event"""
        pass
        
    @abstractmethod
    async def transaction(self) -> AbstractAsyncContextManager:
        """Get a database transaction context manager"""
        pass
        
    @abstractmethod
    async def update_lead_status(self, lead_id: str, status_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update lead status"""
        pass
        
    @abstractmethod
    async def create_sale(self, sale_data: Dict[str, Any]) -> str:
        """Create a new sale record"""
        pass
        
    @abstractmethod
    async def log_loss_reason(
        self,
        lead_id: str,
        reason: str,
        details: Optional[str] = None,
        stage: str = "",
        time_in_pipeline: int = 0
    ) -> bool:
        """Log a loss reason"""
        pass
