from typing import Dict, Any
from datetime import datetime
from ..agents.lead_management_agent import LeadManagementAgent
from ..agents.knowledge_management_agent import KnowledgeManagementAgent
from ..agents.sales_intelligence_agent import SalesIntelligenceAgent
from ..models.base import AgentContext, BaseResponse

class LeadWorkflow:
    def __init__(self):
        self.lead_agent = LeadManagementAgent()
        self.knowledge_agent = KnowledgeManagementAgent()
        self.sales_intelligence = SalesIntelligenceAgent()

    async def process_new_lead(
        self,
        raw_data: Dict[str, Any],
        source: str,
        context: AgentContext
    ) -> BaseResponse:
        # Process lead
        lead_response = await self.lead_agent.process_new_lead(raw_data, source, context)
        if not lead_response.success:
            return lead_response

        # Get product knowledge
        if product_interest := raw_data.get('product_interest'):
            knowledge_response = await self.knowledge_agent.query(
                f"key information about {product_interest}",
                context
            )
            
            if knowledge_response.success:
                lead_response.data['product_knowledge'] = knowledge_response.data

        # Get sales insights
        insights_response = await self.sales_intelligence.get_lead_insights(
            lead_response.data['lead_id'],
            context
        )
        
        if insights_response.success:
            lead_response.data['sales_insights'] = insights_response.data

        return lead_response

    async def handle_lead_update(
        self,
        lead_id: str,
        update_data: Dict[str, Any],
        context: AgentContext
    ) -> BaseResponse:
        # Update lead status
        status_response = await self.lead_agent.update_lead_status(
            lead_id,
            update_data,
            context
        )
        
        if not status_response.success:
            return status_response

        # Get updated insights
        insights_response = await self.sales_intelligence.get_lead_insights(
            lead_id,
            context
        )
        
        if insights_response.success:
            status_response.data['updated_insights'] = insights_response.data

        return status_response