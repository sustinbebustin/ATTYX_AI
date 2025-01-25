from typing import Dict, Any, Optional
from datetime import datetime
from ..agents.call_queue_agent import CallQueueAgent
from ..agents.knowledge_management_agent import KnowledgeManagementAgent
from ..models.base import AgentContext, BaseResponse

class CallQueueWorkflow:
    def __init__(self):
        self.queue_agent = CallQueueAgent()
        self.knowledge_agent = KnowledgeManagementAgent()

    async def get_next_call(
        self,
        agent_id: str,
        context: AgentContext
    ) -> BaseResponse:
        # Get next lead from queue
        queue_response = await self.queue_agent.get_next_lead(agent_id)
        if not queue_response.success or not queue_response.data:
            return queue_response

        # Get relevant knowledge for the lead
        lead_data = queue_response.data
        knowledge_response = await self.knowledge_agent.query(
            f"key information about {lead_data.get('product_interest')}",
            context
        )
        
        if knowledge_response.success:
            queue_response.data['knowledge_base'] = knowledge_response.data

        return queue_response

    async def handle_call_outcome(
        self,
        lead_id: str,
        outcome_data: Dict[str, Any],
        context: AgentContext
    ) -> BaseResponse:
        # Process call outcome
        return await self.queue_agent.process_call_outcome(lead_id, outcome_data, context)

    async def get_queue_status(
        self,
        agent_id: Optional[str] = None,
        context: AgentContext
    ) -> BaseResponse:
        # Get queue metrics
        return await self.queue_agent.get_queue_status(agent_id, context)