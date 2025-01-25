from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import AbstractAsyncContextManager
import pytest
from unittest.mock import AsyncMock, MagicMock
from models.lead import LeadStatus, Lead
from models.base import AgentContext
from services.interfaces.database import DatabaseServiceInterface
from services.interfaces.notification import NotificationServiceInterface
from services.factory import ServiceFactory
from agents.lead_management_agent import LeadManagementAgent, LeadStatusUpdate
from exceptions import LeadUpdateError

class MockDatabaseService(DatabaseServiceInterface):
    """Mock database service for testing"""
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        return "test-lead-id"
        
    async def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> bool:
        return True
        
    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        return {}
        
    async def get_agent_leads(self, agent_id: str) -> List[Dict[str, Any]]:
        return []
        
    async def track_metric(self, metric_data: Dict[str, Any]) -> bool:
        return True
        
    async def transaction(self) -> AbstractAsyncContextManager:
        return AsyncMock()
        
    async def update_lead_status(self, lead_id: str, status_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return {}
        
    async def create_sale(self, sale_data: Dict[str, Any]) -> str:
        return "test-sale-id"
        
    async def log_loss_reason(
        self,
        lead_id: str,
        reason: str,
        details: Optional[str] = None,
        stage: str = "",
        time_in_pipeline: int = 0
    ) -> bool:
        return True

class MockNotificationService(NotificationServiceInterface):
    """Mock notification service for testing"""
    
    async def send_slack_message(
        self,
        channel: str,
        message: str,
        lead_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        return True
        
    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        return True
        
    async def notify_sales_team(self, message: str) -> bool:
        return True
        
    async def schedule_loss_review(
        self,
        lead_id: str,
        assigned_agent: str,
        loss_reason: str,
        estimated_value: float,
        qualification_status: bool,
        time_in_pipeline: int
    ) -> bool:
        return True

@pytest.fixture
def mock_services():
    """Fixture providing mock services"""
    db_service = MockDatabaseService()
    notification_service = MockNotificationService()
    
    # Configure ServiceFactory with mocks
    ServiceFactory.set_service_implementation(DatabaseServiceInterface, db_service)
    ServiceFactory.set_service_implementation(NotificationServiceInterface, notification_service)
    
    yield db_service, notification_service
    
    # Reset ServiceFactory after test
    ServiceFactory.reset()

@pytest.fixture
def agent(mock_services):
    """Fixture providing LeadManagementAgent instance with mock services"""
    db_service, notification_service = mock_services
    return LeadManagementAgent(db_service, notification_service)

@pytest.fixture
def sample_lead():
    """Fixture providing a sample lead for testing"""
    return Lead(
        id="test-lead-id",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        status=LeadStatus.NEW,
        assigned_agent_id="test-agent",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        estimated_value=75000.0
    )

@pytest.mark.asyncio
async def test_update_lead_status_success(agent, mock_services, sample_lead):
    """Test successful lead status update"""
    db_service, notification_service = mock_services
    
    # Configure mock responses
    db_service.get_lead.return_value = sample_lead.dict()
    db_service.update_lead_status.return_value = {"status": "updated"}
    db_service.transaction.return_value.__aenter__ = AsyncMock()
    db_service.transaction.return_value.__aexit__ = AsyncMock()
    
    # Test data
    status_update = {
        "status": LeadStatus.CONTACTED,
        "call_outcome": "Positive call",
        "call_notes": "Customer interested in product demo"
    }
    
    # Execute update
    result = await agent.update_lead_status(
        lead_id=sample_lead.id,
        status_update=status_update,
        context=AgentContext(agent_id="test-agent")
    )
    
    # Verify success
    assert result.success
    assert "updated to CONTACTED" in result.message
    
    # Verify service calls
    db_service.get_lead.assert_called_once_with(sample_lead.id)
    db_service.update_lead_status.assert_called_once()
    db_service.transaction.assert_called_once()

@pytest.mark.asyncio
async def test_handle_won_status(agent, mock_services, sample_lead):
    """Test handling won status with required fields"""
    db_service, notification_service = mock_services
    
    # Configure mock responses
    db_service.get_lead.return_value = sample_lead.dict()
    db_service.transaction.return_value.__aenter__ = AsyncMock()
    db_service.transaction.return_value.__aexit__ = AsyncMock()
    
    # Test data
    status_update = {
        "status": LeadStatus.CLOSED_WON,
        "sale_amount": 100000.0,
        "products": ["Product A", "Product B"]
    }
    
    # Execute update
    result = await agent.update_lead_status(
        lead_id=sample_lead.id,
        status_update=status_update,
        context=AgentContext(agent_id="test-agent")
    )
    
    # Verify success
    assert result.success
    
    # Verify notifications
    notification_service.send_slack_message.assert_called_once()
    assert "Deal closed!" in notification_service.send_slack_message.call_args[1]["message"]
    
    # Verify metrics and sale record
    db_service.track_metric.assert_called_once()
    db_service.create_sale.assert_called_once()

@pytest.mark.asyncio
async def test_handle_lost_status_high_value(agent, mock_services, sample_lead):
    """Test handling lost status for high-value lead"""
    db_service, notification_service = mock_services
    
    # Configure mock responses
    db_service.get_lead.return_value = sample_lead.dict()
    db_service.transaction.return_value.__aenter__ = AsyncMock()
    db_service.transaction.return_value.__aexit__ = AsyncMock()
    
    # Test data
    status_update = {
        "status": LeadStatus.CLOSED_LOST,
        "loss_reason": "Chose competitor solution",
        "loss_details": "Price point was above budget constraints"
    }
    
    # Execute update
    result = await agent.update_lead_status(
        lead_id=sample_lead.id,
        status_update=status_update,
        context=AgentContext(agent_id="test-agent")
    )
    
    # Verify success
    assert result.success
    
    # Verify high-value lead handling
    notification_service.schedule_loss_review.assert_called_once()
    db_service.log_loss_reason.assert_called_once()
    
    # Verify metrics
    db_service.track_metric.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_status_transition(agent, mock_services, sample_lead):
    """Test invalid status transition handling"""
    db_service, _ = mock_services
    
    # Configure mock response
    db_service.get_lead.return_value = sample_lead.dict()
    
    # Test invalid transition
    status_update = {
        "status": LeadStatus.OPPORTUNITY  # Cannot go from NEW to OPPORTUNITY
    }
    
    # Execute update and verify error
    result = await agent.update_lead_status(
        lead_id=sample_lead.id,
        status_update=status_update,
        context=AgentContext(agent_id="test-agent")
    )
    
    assert not result.success
    assert "Invalid Status Transition" in str(result.error)
