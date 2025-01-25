from typing import Dict, Any, List
from ..agents.knowledge_management_agent import KnowledgeManagementAgent
from ..models.base import AgentContext, BaseResponse, KnowledgeItem

class KnowledgeManagementWorkflow:
    def __init__(self):
        self.knowledge_agent = KnowledgeManagementAgent()

    async def process_query(
        self,
        query: str,
        context: AgentContext,
        include_sources: bool = True
    ) -> BaseResponse:
        return await self.knowledge_agent.query(query, context)

    async def update_knowledge_base(
        self,
        items: List[KnowledgeItem],
        context: AgentContext
    ) -> BaseResponse:
        responses = []
        for item in items:
            response = await self.knowledge_agent.update_knowledge_base(item, context)
            responses.append(response)

        # Check if all updates were successful
        all_successful = all(r.success for r in responses)
        return BaseResponse(
            success=all_successful,
            message="Knowledge base updated" if all_successful else "Some updates failed",
            data={"results": [r.data for r in responses]}
        )

    async def verify_information(
        self,
        statement: str,
        context: AgentContext
    ) -> BaseResponse:
        return await self.knowledge_agent.verify_information(statement, context)