from typing import Dict, Any, Optional
from ..agents.sales_intelligence_agent import SalesIntelligenceAgent
from ..models.base import AgentContext, BaseResponse

class SalesIntelligenceWorkflow:
    def __init__(self):
        self.sales_intelligence = SalesIntelligenceAgent()

    async def get_lead_analysis(
        self,
        lead_id: str,
        context: AgentContext
    ) -> BaseResponse:
        return await self.sales_intelligence.get_lead_insights(lead_id, context)

    async def get_performance_metrics(
        self,
        timeframe: str = "7d",
        agent_id: Optional[str] = None,
        context: AgentContext
    ) -> BaseResponse:
        return await self.sales_intelligence.get_sales_performance(timeframe, context)

    async def analyze_conversation(
        self,
        conversation_data: Dict[str, Any],
        context: AgentContext
    ) -> BaseResponse:
        return await self.sales_intelligence.analyze_conversation(conversation_data, context)