from typing import Dict, Any, List, Optional, cast, Set, ClassVar
from datetime import datetime
import logging
from pydantic import BaseModel, Field, validator, root_validator
from pydantic_ai import Agent, RunContext
from models.base import BaseResponse, AgentContext
from models.lead import LeadStatus, Lead, CallAttempt
from services.interfaces.database import DatabaseServiceInterface
from services.interfaces.notification import NotificationServiceInterface
from services.factory import ServiceFactory
from exceptions import LeadUpdateError

class LeadStatusUpdate(BaseModel):
    """Validated schema for lead status updates
    
    Class Attributes:
        VALID_TRANSITIONS: Mapping of allowed status transitions
    
    Attributes:
        status: New status to update the lead to
        current_status: Current status of the lead
        sale_amount: Amount of the sale (required for won deals)
        products: List of products included in the deal
        follow_up_date: Next scheduled follow-up date
        loss_reason: Reason for losing the deal (required for lost deals)
        loss_details: Detailed explanation of loss reason
        call_outcome: Result of the latest call attempt
        call_notes: Notes from the latest call
        
    Raises:
        ValueError: If validation fails or data is inconsistent
    """
    
    # Class-level mapping of valid status transitions
    VALID_TRANSITIONS: ClassVar[Dict[LeadStatus, Set[LeadStatus]]] = {
        LeadStatus.NEW: {LeadStatus.CONTACTED, LeadStatus.CLOSED_LOST},
        LeadStatus.CONTACTED: {LeadStatus.QUALIFIED, LeadStatus.CLOSED_LOST},
        LeadStatus.QUALIFIED: {LeadStatus.OPPORTUNITY, LeadStatus.CLOSED_LOST},
        LeadStatus.OPPORTUNITY: {LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST},
        LeadStatus.CLOSED_WON: set(),  # Terminal state
        LeadStatus.CLOSED_LOST: set()  # Terminal state
    }
    
    # Status fields with validation
    status: LeadStatus = Field(
        ...,  # Required
        description="New status to update the lead to"
    )
    current_status: LeadStatus = Field(
        ...,  # Required
        description="Current status of the lead"
    )
    
    # Deal-related fields
    sale_amount: Optional[float] = Field(
        None,
        ge=0,
        description="Sale amount (required for won deals)"
    )
    products: List[str] = Field(
        default_factory=list,
        min_items=1,
        description="List of products included in the deal"
    )
    
    # Follow-up fields
    follow_up_date: Optional[datetime] = Field(
        None,
        description="Next scheduled follow-up date (must be in the future)"
    )
    
    # Loss-related fields
    loss_reason: Optional[str] = Field(
        None,
        min_length=10,
        description="Reason for losing the deal (required for lost deals)"
    )
    loss_details: Optional[str] = Field(
        None,
        min_length=20,
        description="Detailed explanation of loss reason"
    )
    
    # Call-related fields
    call_outcome: Optional[str] = Field(
        None,
        min_length=5,
        description="Result of the latest call attempt"
    )
    call_notes: Optional[str] = Field(
        None,
        min_length=10,
        description="Notes from the latest call"
    )

    @classmethod
    def _format_error(cls, category: str, message: str, context: Dict[str, Any], docs_url: str) -> str:
        """Format validation error messages consistently
        
        Args:
            category: Error category (e.g., "Status Validation Error")
            message: Main error message
            context: Additional context for the error
            docs_url: URL to relevant documentation
            
        Returns:
            Formatted error message with context and documentation link
        """
        context_str = "\n".join(f"- {k}: {v}" for k, v in context.items())
        return (
            f"{category}:\n"
            f"{message}\n"
            f"\nContext:\n"
            f"{context_str}\n"
            f"\nSee: {docs_url} for more details"
        )

    @root_validator(pre=True)
    def validate_status_transition(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all status-related rules and data consistency
        
        Validates:
        1. Status transition is allowed
        2. Required fields for specific statuses
        3. Business rules for status changes
        4. Data consistency across fields
        5. Temporal constraints
        6. Value constraints
        
        Args:
            values: Dict of field values
            
        Returns:
            Dict[str, Any]: Validated values
            
        Raises:
            ValueError: If validation fails or data is inconsistent
        """
        status = values.get('status')
        current_status = values.get('current_status')
        
        # Status validation
        if not (status and current_status):
            raise ValueError(cls._format_error(
                category="Status Validation Error",
                message="Both current and new status must be provided",
                context={
                    "Available Statuses": [s.value for s in LeadStatus],
                    "Example": (
                        "status_update = {\n"
                        "    'current_status': LeadStatus.NEW,\n"
                        "    'status': LeadStatus.CONTACTED\n"
                        "}"
                    )
                },
                docs_url="https://attyx-ai.docs/lead-lifecycle"
            ))
            
        # Transition validation
        if current_status == status:
            if status in {LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST}:
                raise ValueError(cls._format_error(
                    category="Terminal Status Error",
                    message="Cannot update a terminal status",
                    context={
                        "Current Status": status.value,
                        "Terminal States": ["CLOSED_WON", "CLOSED_LOST"],
                        "Note": "Terminal statuses are final and cannot be modified"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#terminal-states"
                ))
            return values
            
        valid_transitions = cls.VALID_TRANSITIONS.get(current_status, set())
        if status not in valid_transitions:
            raise ValueError(cls._format_error(
                category="Invalid Status Transition",
                message="Attempted status transition not allowed",
                context={
                    "Current Status": current_status.value,
                    "Attempted Status": status.value,
                    "Valid Transitions": [s.value for s in valid_transitions],
                    "Lead Lifecycle": "NEW -> CONTACTED -> QUALIFIED -> OPPORTUNITY -> CLOSED_WON/LOST"
                },
                docs_url="https://attyx-ai.docs/lead-states#transitions"
            ))
            
        # Temporal validation
        if values.get('follow_up_date'):
            if status in {LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST}:
                raise ValueError(cls._format_error(
                    category="Invalid Follow-up Configuration",
                    message="Cannot set follow-up date for closed leads",
                    context={
                        "Current Status": status.value,
                        "Action Required": "Remove follow-up date for closed statuses"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#follow-ups"
                ))
                
        # Value constraints
        if values.get('sale_amount'):
            if status != LeadStatus.CLOSED_WON:
                raise ValueError(cls._format_error(
                    category="Invalid Sale Amount",
                    message="Sale amount can only be set for won deals",
                    context={
                        "Current Status": status.value,
                        "Action Required": "Remove sale amount or update status to CLOSED_WON"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#won-deals"
                ))
                
        if values.get('loss_reason'):
            if status != LeadStatus.CLOSED_LOST:
                raise ValueError(cls._format_error(
                    category="Invalid Loss Reason",
                    message="Loss reason can only be set for lost deals",
                    context={
                        "Current Status": status.value,
                        "Action Required": "Remove loss reason or update status to CLOSED_LOST"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#lost-deals"
                ))
                
        # Call data validation
        if values.get('call_outcome') or values.get('call_notes'):
            if not (values.get('call_outcome') and values.get('call_notes')):
                raise ValueError(cls._format_error(
                    category="Incomplete Call Data",
                    message="Both call outcome and notes must be provided together",
                    context={
                        "Missing Fields": [
                            f for f in ['call_outcome', 'call_notes']
                            if not values.get(f)
                        ],
                        "Action Required": "Provide both fields or remove both if no call was made"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#call-tracking"
                ))
                
        # Required field validation
        if status == LeadStatus.CLOSED_WON:
            if not values.get('sale_amount'):
                raise ValueError(cls._format_error(
                    category="Missing Required Field",
                    message="Sale amount is required for won deals",
                    context={
                        "Status": status.value,
                        "Required Fields": ["sale_amount"],
                        "Action Required": "Provide sale amount for won deals"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#won-deals"
                ))
                
        if status == LeadStatus.CLOSED_LOST:
            if not values.get('loss_reason'):
                raise ValueError(cls._format_error(
                    category="Missing Required Field",
                    message="Loss reason is required for lost deals",
                    context={
                        "Status": status.value,
                        "Required Fields": ["loss_reason"],
                        "Action Required": "Provide loss reason for lost deals"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#lost-deals"
                ))
                
        if status == LeadStatus.QUALIFIED:
            if not values.get('call_outcome'):
                raise ValueError(cls._format_error(
                    category="Missing Required Field",
                    message="Call details required for qualification",
                    context={
                        "Status": status.value,
                        "Required Fields": ["call_outcome", "call_notes"],
                        "Action Required": "Record call details before qualifying"
                    },
                    docs_url="https://attyx-ai.docs/lead-states#qualification"
                ))
                
        return values

    @validator('follow_up_date')
    def validate_future_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure follow-up dates are in the future"""
        if v and v < datetime.utcnow():
            raise ValueError("Follow-up date must be in the future")
        return v

    @validator('call_outcome', 'call_notes')
    def validate_call_fields(cls, v: Optional[str], values: dict, field: str) -> Optional[str]:
        """Validate call-related fields are provided together"""
        call_fields = {'call_outcome', 'call_notes'}
        other_field = next(f for f in call_fields if f != field)
        
        if v and not values.get(other_field):
            raise ValueError("Both call outcome and notes must be provided together")
        return v

class LeadManagementAgent(Agent):
    """AI agent for managing sales leads through their lifecycle"""
    
    def __init__(
        self,
        db_service: Optional[DatabaseServiceInterface] = None,
        notification_service: Optional[NotificationServiceInterface] = None
    ) -> None:
        """Initialize the LeadManagementAgent with required services
        
        Args:
            db_service: Optional database service implementation
            notification_service: Optional notification service implementation
        """
        super().__init__()
        self.db_service = db_service or ServiceFactory.get_database_service()
        self.notification_service = notification_service or ServiceFactory.get_notification_service()
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Configure agent-specific logger"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger
        
    async def _track_metrics(
        self,
        lead: Lead,
        status: LeadStatus,
        details: Dict[str, Any]
    ) -> None:
        """Track lead status change metrics
        
        Args:
            lead: Current lead data
            status: New lead status
            details: Additional metric details
        """
        await self.db_service.track_metric({
            'timestamp': datetime.utcnow(),
            'lead_id': lead.id,
            'agent_id': lead.assigned_agent_id,
            'old_status': lead.status,
            'new_status': status,
            'time_in_status': (datetime.utcnow() - lead.updated_at).days,
            **details
        })

    async def update_lead_status(
        self,
        lead_id: str,
        status_update: Dict[str, Any],
        context: AgentContext
    ) -> BaseResponse:
        """Update lead status with validated inputs
        
        Args:
            lead_id: UUID of lead to update
            status_update: Validated status change payload
            context: Agent execution context
            
        Returns:
            BaseResponse: Standardized response with update results
            
        Raises:
            LeadUpdateError: For business logic failures
            ValidationError: For invalid input data
        """
        try:
            # Get current lead data
            lead_data = await self.db_service.get_lead(lead_id)
            if not lead_data:
                raise LeadUpdateError(f"Lead {lead_id} not found")
            
            current_lead = Lead(**lead_data)
            
            # Validate status update with current state
            update_data = {**status_update, 'current_status': current_lead.status}
            validated_update = LeadStatusUpdate(**update_data)
            
            self.logger.info(
                f"Validating status transition for lead {lead_id}: "
                f"{current_lead.status.value} -> {validated_update.status.value}"
            )
            
            async with self.db_service.transaction():
                # Update lead status
                update_result = await self.db_service.update_lead_status(
                    lead_id,
                    validated_update.dict(exclude_unset=True)
                )
                
                # Record call attempt if provided
                if validated_update.call_outcome:
                    current_lead.add_call_attempt(
                        outcome=validated_update.call_outcome,
                        notes=validated_update.call_notes,
                        next_attempt=validated_update.follow_up_date
                    )
                    await self.db_service.update_lead(lead_id, current_lead.dict())
                
                # Handle status-specific actions
                match validated_update.status:
                    case LeadStatus.CLOSED_WON:
                        await self._handle_won_status(current_lead, validated_update)
                    case LeadStatus.CLOSED_LOST:
                        await self._handle_lost_status(current_lead, validated_update)
                    case LeadStatus.QUALIFIED:
                        await self.notification_service.notify_sales_team(
                            f"New qualified lead: {current_lead.first_name} {current_lead.last_name}"
                        )

            return BaseResponse.success(
                message=f"Lead {lead_id} status updated to {validated_update.status.value}",
                data=update_result
            )
            
        except ValidationError as e:
            self.logger.warning(f"Validation failed: {e.errors()}")
            return BaseResponse.validation_error(e)
        except LeadUpdateError as e:
            self.logger.error(f"Business rule violation: {e}")
            return BaseResponse.business_error(e)
        except Exception as e:
            self.logger.exception("Critical update failure")
            return BaseResponse.system_error(
                LeadUpdateError("Lead update failed", original_error=e)
            )

    async def _handle_won_status(self, lead: Lead, update: LeadStatusUpdate) -> None:
        """Handle actions required when a lead is won
        
        Args:
            lead: Current lead data
            update: Validated status update
            
        Raises:
            LeadUpdateError: If required data is missing
        """
        if not update.sale_amount:
            raise LeadUpdateError("Sale amount is required for won deals")
            
        if not lead.assigned_agent_id:
            raise LeadUpdateError("Lead must be assigned to an agent")

        # Track comprehensive metrics
        await self._track_metrics(lead, LeadStatus.CLOSED_WON, {
            'revenue': update.sale_amount,
            'products_count': len(update.products),
            'time_to_close': (datetime.utcnow() - lead.created_at).days,
            'qualification_complete': lead.is_qualified(),
            'had_calls': bool(lead.call_attempts),
            'stage_at_close': lead.status.value,
            'deal_size': 'high' if update.sale_amount > 50000 else 'standard'
        })

        # Create sale record with enhanced tracking
        await self.db_service.create_sale({
            'lead_id': lead.id,
            'amount': update.sale_amount,
            'products': update.products,
            'close_date': datetime.utcnow(),
            'time_in_pipeline': (datetime.utcnow() - lead.created_at).days,
            'qualification_status': lead.is_qualified(),
            'total_calls': len(lead.call_attempts)
        })
        
        # Send notifications with enriched data
        await self.notification_service.send_slack_message(
            channel="sales-wins",
            message=(
                f"🎉 Deal closed! {lead.first_name} {lead.last_name}\n"
                f"Amount: ${update.sale_amount:,.2f}\n"
                f"Products: {', '.join(update.products)}\n"
                f"Time to close: {(datetime.utcnow() - lead.created_at).days} days"
            )
        )

    async def _handle_lost_status(self, lead: Lead, update: LeadStatusUpdate) -> None:
        """Handle actions required when a lead is lost
        
        Args:
            lead: Current lead data
            update: Validated status update
            
        Raises:
            LeadUpdateError: If required data is missing or invalid
        """
        if not update.loss_reason:
            raise LeadUpdateError("Loss reason is required for lost deals")
            
        if not lead.assigned_agent_id:
            raise LeadUpdateError("Lead must be assigned to an agent")
            
        if not update.loss_details and lead.estimated_value and lead.estimated_value > 50000:
            self.logger.warning(f"No detailed loss reason provided for high-value lead {lead.id}")
        
        # Track comprehensive metrics
        await self._track_metrics(lead, LeadStatus.CLOSED_LOST, {
            'loss_reason': update.loss_reason,
            'potential_revenue': lead.estimated_value,
            'time_to_loss': (datetime.utcnow() - lead.created_at).days,
            'qualification_complete': lead.is_qualified(),
            'had_calls': bool(lead.call_attempts),
            'stage_at_loss': lead.status.value
        })
        
        # Log loss details for analysis
        await self.db_service.log_loss_reason(
            lead.id,
            reason=update.loss_reason,
            details=update.loss_details,
            stage=lead.status.value,
            time_in_pipeline=(datetime.utcnow() - lead.created_at).days
        )
        
        # Schedule review for high-value opportunities
        if lead.estimated_value and lead.estimated_value > 50000:
            self.logger.info(f"Scheduling loss review for high-value lead {lead.id}")
            await self.notification_service.schedule_loss_review(
                lead_id=lead.id,
                assigned_agent=lead.assigned_agent_id,
                loss_reason=update.loss_reason,
                estimated_value=lead.estimated_value,
                qualification_status=lead.is_qualified(),
                time_in_pipeline=(datetime.utcnow() - lead.created_at).days
            )
