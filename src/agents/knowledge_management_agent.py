from typing import List, Dict, Any, Optional
from pydantic_ai import Agent, RunContext
from ..models.base import KnowledgeItem, AgentContext, BaseResponse
from ..services.database_service import DatabaseService
from ..utils.helpers import compute_embeddings

class KnowledgeManagementAgent:
    def __init__(self, model: str = "openai:gpt-4"):
        self.agent = Agent(
            model,
            system_prompt="""You are a knowledge management agent responsible for retrieving and verifying information about solar, HVAC, and roofing products and services. Your responses should be accurate, relevant, and tailored to sales contexts.""",
            deps_type=Dict[str, Any],
            result_type=BaseResponse
        )
        self.db_service = DatabaseService()
        self._setup_tools()

    def _setup_tools(self):
        @self.agent.tool
        async def search_knowledge_base(
            ctx: RunContext[Dict[str, Any]], 
            query: str,
            top_k: int = 5
        ) -> List[KnowledgeItem]:
            """Search the knowledge base using semantic search"""
            # Generate query embedding
            query_embedding = await compute_embeddings(query)
            
            # Search vector database
            results = await self.db_service.similarity_search(
                collection="knowledge_base",
                query_vector=query_embedding,
                top_k=top_k
            )
            
            return [KnowledgeItem(**item) for item in results]

        @self.agent.tool
        async def verify_information(
            ctx: RunContext[Dict[str, Any]],
            statement: str,
            context: List[KnowledgeItem]
        ) -> Dict[str, Any]:
            """Verify information against the knowledge base"""
            # Use RAG to verify the statement
            verification_prompt = f"""
            Given the following statement:
            {statement}
            
            And the following context:
            {[item.content for item in context]}
            
            Verify if the statement is accurate and provide:
            1. Verification result (true/false)
            2. Confidence score (0-1)
            3. Supporting evidence or corrections
            """
            
            result = await ctx.run(verification_prompt)
            return result.data

        @self.agent.tool
        async def update_knowledge_base(
            ctx: RunContext[Dict[str, Any]],
            item: KnowledgeItem
        ) -> bool:
            """Add or update an item in the knowledge base"""
            try:
                # Generate embeddings for new content
                embedding = await compute_embeddings(item.content)
                item.embedding = embedding
                
                # Store in vector database
                await self.db_service.upsert_knowledge_item(item)
                return True
            except Exception as e:
                print(f"Error updating knowledge base: {e}")
                return False

    async def query(
        self,
        query: str,
        context: AgentContext,
        max_results: int = 5
    ) -> BaseResponse:
        """Query the knowledge base with RAG enhancement"""
        try:
            # Search knowledge base
            relevant_items = await self.search_knowledge_base(query, max_results)
            
            # Generate enhanced response using RAG
            rag_prompt = f"""
            Based on the following query: {query}
            
            And the retrieved knowledge:
            {[item.content for item in relevant_items]}
            
            Provide a comprehensive response that:
            1. Directly addresses the query
            2. Incorporates relevant product/service information
            3. Includes any necessary caveats or additional context
            4. Suggests related information that might be helpful
            """
            
            response = await self.agent.run(
                rag_prompt,
                deps={"context": context.dict()}
            )
            
            return BaseResponse(
                success=True,
                data={
                    "response": response.data,
                    "sources": [item.id for item in relevant_items]
                }
            )
            
        except Exception as e:
            return BaseResponse(
                success=False,
                message=f"Error processing query: {str(e)}",
                errors=[str(e)]
            )