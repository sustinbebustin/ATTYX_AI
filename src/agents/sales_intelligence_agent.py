from typing import Dict, Any, List
from datetime import datetime, timedelta
from pydantic_ai import Agent, RunContext
from ..models.base import BaseResponse, AgentContext
from ..services.database_service import DatabaseService
from ..services.analytics_service import AnalyticsService

class SalesIntelligenceAgent:
    def __init__(self, model: str = "openai:gpt-4"):
        self.agent = Agent(
            model,
            system_prompt="You are a sales intelligence agent focused on analyzing patterns, providing insights, and optimizing sales strategies.",
            deps_type=Dict[str, Any],
            result_type=BaseResponse
        )
        self.db_service = DatabaseService()
        self.analytics_service = AnalyticsService()
        self._setup_tools()

    def _setup_tools(self):
        @self.agent.tool
        async def analyze_conversation(
            ctx: RunContext[Dict[str, Any]],
            conversation_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Analyze sales conversations for insights"""
            analysis_prompt = f"""
            Analyze this sales conversation:
            {conversation_data['transcript']}
            
            Identify:
            1. Key objections and how they were handled
            2. Customer pain points
            3. Buying signals
            4. Areas for improvement
            5. Follow-up opportunities
            """
            
            analysis = await ctx.run(analysis_prompt)
            return analysis.data

        @self.agent.tool
        async def predict_close_probability(
            ctx: RunContext[Dict[str, Any]],
            lead_data: Dict[str, Any]
        ) -> float:
            """Predict probability of closing a deal"""
            key_factors = {
                'budget_match': lead_data.get('budget_sufficient', False) * 0.3,
                'decision_maker': lead_data.get('is_decision_maker', False) * 0.2,
                'timeline_match': lead_data.get('timeline_match', False) * 0.15,
                'engagement_score': min(lead_data.get('engagement_score', 0) / 100, 1) * 0.2,
                'objections_handled': min(lead_data.get('resolved_objections', 0) / lead_data.get('total_objections', 1), 1) * 0.15
            }
            
            return sum(key_factors.values())

        @self.agent.tool
        async def generate_sales_insights(
            ctx: RunContext[Dict[str, Any]],
            timeframe: str
        ) -> Dict[str, Any]:
            """Generate sales insights for a given timeframe"""
            # Get sales data
            sales_data = await self.analytics_service.get_sales_metrics(timeframe)
            
            analysis_prompt = f"""
            Based on these sales metrics:
            {sales_data}
            
            Provide insights on:
            1. Trending products/services
            2. Successful sales strategies
            3. Common objections and effective responses
            4. Opportunities for improvement
            """
            
            insights = await ctx.run(analysis_prompt)
            return insights.data

    async def get_lead_insights(
        self,
        lead_id: str,
        context: AgentContext
    ) -> BaseResponse:
        """Get comprehensive insights for a specific lead"""
        try:
            # Gather lead data
            lead_data = await self.db_service.get_lead(lead_id)
            conversations = await self.db_service.get_lead_conversations(lead_id)
            
            # Analyze conversations
            conversation_insights = await self.analyze_conversation({
                'transcript': conversations[-1]['transcript'] if conversations else ""
            })
            
            # Predict close probability
            close_probability = await self.predict_close_probability(lead_data)
            
            # Get similar closed deals
            similar_deals = await self.db_service.get_similar_deals(
                lead_data.get('product_interest'),
                lead_data.get('budget_range')
            )
            
            return BaseResponse(
                success=True,
                data={
                    'lead_id': lead_id,
                    'close_probability': close_probability,
                    'conversation_insights': conversation_insights,
                    'similar_deals': similar_deals,
                    'recommended_actions': conversation_insights.get('follow_up_opportunities', [])
                }
            )
            
        except Exception as e:
            return BaseResponse(
                success=False,
                message=f"Error getting lead insights: {str(e)}",
                errors=[str(e)]
            )

    async def get_sales_performance(
        self,
        timeframe: str = "7d",
        context: AgentContext
    ) -> BaseResponse:
        """Get sales performance analysis"""
        try:
            insights = await self.generate_sales_insights(timeframe)
            metrics = await self.analytics_service.get_performance_metrics(timeframe)
            
            return BaseResponse(
                success=True,
                data={
                    'timeframe': timeframe,
                    'insights': insights,
                    'metrics': metrics
                }
            )
            
        except Exception as e:
            return BaseResponse(
                success=False,
                message=f"Error analyzing sales performance: {str(e)}",
                errors=[str(e)]
            )