from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic_ai import Agent, RunContext
from ..models.base import BaseResponse, AgentContext
from ..services.database_service import DatabaseService
from ..services.notification_service import NotificationService
from ..utils.helpers import extract_lead_info

# [Previous implementation remains the same until update_lead_status method]

    async def update_lead_status(
        self,
        lead_id: str,
        status_update: Dict[str, Any],
        context: AgentContext
    ) -> BaseResponse:
        """Update lead status and trigger appropriate actions"""
        try:
            # Get current lead data
            current_lead = await self.db_service.get_lead(lead_id)
            
            # Update lead status
            await self.db_service.update_lead_status(lead_id, status_update)
            
            # Process status change
            if status_update.get('status') == 'won':
                # Create sale record
                await self.db_service.create_sale({
                    'lead_id': lead_id,
                    'amount': status_update.get('sale_amount'),
                    'products': status_update.get('products', []),
                    'agent_id': current_lead['assigned_agent_id'],
                    'close_date': datetime.utcnow()
                })
                
                # Send notifications
                await self.notification_service.send_slack_message(
                    channel="sales-wins",
                    message=f"🎉 Deal closed! {current_lead['name']} - ${status_update.get('sale_amount'):,.2f}"
                )
                
            elif status_update.get('status') == 'lost':
                # Log loss reason
                await self.db_service.log_loss_reason(
                    lead_id,
                    status_update.get('loss_reason'),
                    status_update.get('loss_details')
                )
                
                # Update agent metrics
                await self.db_service.update_agent_metrics(
                    current_lead['assigned_agent_id'],
                    {'lost_leads': 1}
                )
                
            elif status_update.get('status') == 'nurture':
                # Schedule follow-up
                await self.db_service.create_followup_task({
                    'lead_id': lead_id,
                    'due_date': status_update.get('follow_up_date'),
                    'task_type': 'nurture_followup',
                    'notes': status_update.get('nurture_notes')
                })
            
            return BaseResponse(
                success=True,
                message=f"Lead status updated to {status_update.get('status')}",
                data={
                    'lead_id': lead_id,
                    'new_status': status_update.get('status'),
                    'update_time': datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            return BaseResponse(
                success=False,
                message=f"Error updating lead status: {str(e)}",
                errors=[str(e)]
            )