from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic_ai import Agent, RunContext
from ..models.base import BaseResponse, AgentContext
from ..services.database_service import DatabaseService
from ..services.notification_service import NotificationService

class CallQueueAgent:
    def __init__(self, model: str = "openai:gpt-4"):
        self.agent = Agent(
            model,
            system_prompt="""You are a call queue management agent responsible for optimizing lead processing and call scheduling. 
            Prioritize leads based on age, attempt history, and potential value. Ensure timely follow-ups and proper lead distribution.""",
            deps_type=Dict[str, Any],
            result_type=BaseResponse
        )
        self.db_service = DatabaseService()
        self.notification_service = NotificationService()
        self._setup_tools()
        
    def _setup_tools(self):
        @self.agent.tool
        async def prioritize_leads(
            ctx: RunContext[Dict[str, Any]],
            leads: List[Dict[str, Any]]
        ) -> List[Dict[str, Any]]:
            """Prioritize leads based on various factors"""
            prioritized = []
            for lead in leads:
                # Calculate priority score
                age_hours = (datetime.utcnow() - datetime.fromisoformat(lead['created_at'])).total_seconds() / 3600
                attempts = lead.get('attempt_count', 0)
                
                priority_score = (
                    (24 - min(age_hours, 24)) * 2 +  # Newer leads get higher priority
                    (3 - min(attempts, 3)) * 5       # Fewer attempts get higher priority
                )
                
                # Add estimated value factor if available
                if 'estimated_value' in lead:
                    priority_score += min(lead['estimated_value'] / 10000, 5)
                
                lead['priority_score'] = priority_score
                prioritized.append(lead)
            
            return sorted(prioritized, key=lambda x: x['priority_score'], reverse=True)

        @self.agent.tool
        async def schedule_call_attempt(
            ctx: RunContext[Dict[str, Any]],
            lead_id: str,
            attempt_number: int
        ) -> Dict[str, Any]:
            """Schedule the next call attempt"""
            delays = {
                1: timedelta(minutes=10),
                2: timedelta(minutes=30),
                3: timedelta(hours=1),
                4: timedelta(hours=4),
                5: timedelta(hours=24)
            }
            
            delay = delays.get(attempt_number, timedelta(hours=24))
            scheduled_time = datetime.utcnow() + delay
            
            return {
                'lead_id': lead_id,
                'attempt_number': attempt_number,
                'scheduled_time': scheduled_time.isoformat(),
                'status': 'scheduled'
            }

        @self.agent.tool
        async def notify_agent(
            ctx: RunContext[Dict[str, Any]],
            lead_data: Dict[str, Any],
            notification_type: str
        ) -> bool:
            """Send notifications to sales agents"""
            templates = {
                'new_lead': "New lead received: {name} - {phone}",
                'reminder': "Reminder: Follow up with {name}",
                'escalation': "Escalation: Lead {name} requires immediate attention"
            }
            
            message = templates[notification_type].format(**lead_data)
            
            # Send to both Slack and email
            await self.notification_service.send_slack_message(
                channel="sales-queue",
                message=message,
                lead_data=lead_data
            )
            
            if notification_type in ['escalation', 'new_lead']:
                await self.notification_service.send_email(
                    recipient=lead_data['assigned_agent_email'],
                    subject=f"ATTYX AI - {notification_type.replace('_', ' ').title()}",
                    body=message
                )
            
            return True

        @self.agent.tool
        async def assign_agent(
            ctx: RunContext[Dict[str, Any]],
            lead_data: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Assign the most appropriate agent to a lead"""
            # Get available agents
            agents = await self.db_service.get_available_agents()
            
            # Calculate agent scores based on various factors
            agent_scores = []
            for agent in agents:
                score = 0
                # Factor 1: Current queue load
                queue_load = len(agent.get('active_leads', []))
                score -= queue_load * 2
                
                # Factor 2: Experience with lead type
                if lead_data.get('product_interest') in agent.get('specialties', []):
                    score += 5
                    
                # Factor 3: Recent performance
                success_rate = agent.get('success_rate', 0)
                score += success_rate * 3
                
                agent_scores.append((agent, score))
            
            # Select best agent
            best_agent = max(agent_scores, key=lambda x: x[1])[0]
            
            return {
                'agent_id': best_agent['id'],
                'agent_name': best_agent['name'],
                'agent_email': best_agent['email']
            }

    async def process_lead(
        self,
        lead_data: Dict[str, Any],
        context: AgentContext
    ) -> BaseResponse:
        """Process a new lead"""
        try:
            # Prioritize the lead
            prioritized = await self.prioritize_leads([lead_data])
            lead_with_priority = prioritized[0]
            
            # Assign an agent
            agent_assignment = await self.assign_agent(lead_with_priority)
            lead_with_priority.update(agent_assignment)
            
            # Schedule first attempt
            schedule = await self.schedule_call_attempt(
                lead_with_priority['id'],
                attempt_number=1
            )
            
            # Store in database
            await self.db_service.update_lead(
                lead_id=lead_with_priority['id'],
                update_data={
                    'priority_score': lead_with_priority['priority_score'],
                    'next_attempt': schedule['scheduled_time'],
                    'attempt_count': 1,
                    'status': 'scheduled',
                    'assigned_agent_id': agent_assignment['agent_id']
                }
            )
            
            # Send notification
            await self.notify_agent(
                lead_data=lead_with_priority,
                notification_type='new_lead'
            )
            
            return BaseResponse(
                success=True,
                message="Lead processed successfully",
                data={
                    'lead_id': lead_with_priority['id'],
                    'priority_score': lead_with_priority['priority_score'],
                    'next_attempt': schedule['scheduled_time'],
                    'assigned_agent': agent_assignment
                }
            )
            
        except Exception as e:
            return BaseResponse(
                success=False,
                message=f"Error processing lead: {str(e)}",
                errors=[str(e)]
            )

    async def get_next_lead(self, agent_id: str) -> BaseResponse:
        """Get the next lead for an agent to call"""
        try:
            # Get agent's current leads
            leads = await self.db_service.get_agent_leads(agent_id)
            
            # Prioritize leads
            prioritized = await self.prioritize_leads(leads)
            
            # Get the highest priority lead that's due for contact
            next_lead = None
            for lead in prioritized:
                if datetime.fromisoformat(lead['next_attempt']) <= datetime.utcnow():
                    next_lead = lead
                    break
            
            if not next_lead:
                return BaseResponse(
                    success=True,
                    message="No leads currently ready for contact",
                    data=None
                )
            
            return BaseResponse(
                success=True,
                message="Next lead retrieved successfully",
                data=next_lead
            )
            
        except Exception as e:
            return BaseResponse(
                success=False,
                message=f"Error retrieving next lead: {str(e)}",
                errors=[str(e)]
            )
