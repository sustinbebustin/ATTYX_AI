from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from supabase import create_client, Client
from ..config.settings import SUPABASE_URL, SUPABASE_KEY
from ..models.base import KnowledgeItem

class DatabaseService:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        result = await self.client.table('leads').insert(lead_data).execute()
        return result.data[0]['id']

    async def update_lead(self, lead_id: str, update_data: Dict[str, Any]) -> bool:
        await self.client.table('leads').update(update_data).eq('id', lead_id).execute()
        return True

    async def get_lead(self, lead_id: str) -> Dict[str, Any]:
        result = await self.client.table('leads').select('*').eq('id', lead_id).execute()
        return result.data[0] if result.data else None

    async def get_agent_leads(self, agent_id: str) -> List[Dict[str, Any]]:
        result = await self.client.table('leads').select('*').eq('assigned_agent_id', agent_id).execute()
        return result.data

    async def similarity_search(
        self,
        collection: str,
        query_vector: List[float],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        # Using pgvector for similarity search
        query = f"""
        SELECT *, (embedding <=> '{json.dumps(query_vector)}') as distance
        FROM {collection}
        ORDER BY distance
        LIMIT {top_k}
        """
        result = await self.client.rpc('similarity_search', {
            'query_embedding': query_vector,
            'match_count': top_k
        }).execute()
        return result.data

    async def upsert_knowledge_item(self, item: KnowledgeItem) -> bool:
        data = item.dict()
        await self.client.table('knowledge_base').upsert(data).execute()
        return True

    async def get_queue_metrics(self) -> Dict[str, Any]:
        result = await self.client.rpc('get_queue_metrics').execute()
        return result.data

    async def log_conversation(
        self,
        lead_id: str,
        conversation_data: Dict[str, Any]
    ) -> str:
        result = await self.client.table('conversations').insert({
            'lead_id': lead_id,
            'data': conversation_data,
            'timestamp': datetime.utcnow().isoformat()
        }).execute()
        return result.data[0]['id']

    async def get_sales_metrics(
        self,
        timeframe: str = "7d"
    ) -> Dict[str, Any]:
        result = await self.client.rpc('get_sales_metrics', {
            'timeframe': timeframe
        }).execute()
        return result.data