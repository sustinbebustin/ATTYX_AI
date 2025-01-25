from typing import Dict, Any, Optional
from slack_sdk.web.async_client import AsyncWebClient
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config.settings import SLACK_TOKEN, SENDGRID_API_KEY
from .interfaces.notification import NotificationServiceInterface

class NotificationService(NotificationServiceInterface):
    def __init__(self):
        self.slack_client = AsyncWebClient(token=SLACK_TOKEN)
        self.sendgrid_client = SendGridAPIClient(SENDGRID_API_KEY)

    async def send_slack_message(
        self,
        channel: str,
        message: str,
        lead_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": message}}]
            
            if lead_data:
                blocks.append({
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Lead:* {lead_data.get('name')}"},
                        {"type": "mrkdwn", "text": f"*Phone:* {lead_data.get('phone')}"},
                        {"type": "mrkdwn", "text": f"*Product:* {lead_data.get('product_interest')}"},
                        {"type": "mrkdwn", "text": f"*Score:* {lead_data.get('qualification_score', 0):.1f}"}
                    ]
                })

            await self.slack_client.chat_postMessage(
                channel=channel,
                text=message,
                blocks=blocks
            )
            return True
            
        except Exception as e:
            print(f"Error sending Slack message: {e}")
            return False

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            message = Mail(
                from_email='noreply@attyxai.com',
                to_emails=recipient,
                subject=subject,
                html_content=body
            )
            
            if template_id:
                message.template_id = template_id
                if template_data:
                    message.dynamic_template_data = template_data

            response = await self.sendgrid_client.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def send_mobile_notification(
        self,
        user_id: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        # Implement mobile push notifications when needed
        pass

    async def notify_sales_team(self, message: str) -> bool:
        """Send notification to sales team channel"""
        return await self.send_slack_message(
            channel="sales-team",
            message=message
        )

    async def schedule_loss_review(
        self,
        lead_id: str,
        assigned_agent: str,
        loss_reason: str,
        estimated_value: float,
        qualification_status: bool,
        time_in_pipeline: int
    ) -> bool:
        """Schedule a loss review meeting and notify relevant team members"""
        message = (
            f"🔍 *High-Value Lead Loss Review Required*\n"
            f"Lead ID: {lead_id}\n"
            f"Agent: <@{assigned_agent}>\n"
            f"Loss Reason: {loss_reason}\n"
            f"Estimated Value: ${estimated_value:,.2f}\n"
            f"Qualification Status: {'✅ Complete' if qualification_status else '❌ Incomplete'}\n"
            f"Time in Pipeline: {time_in_pipeline} days"
        )
        
        # Send to dedicated loss review channel
        await self.send_slack_message(
            channel="loss-reviews",
            message=message
        )
        
        # Send email to sales manager
        await self.send_email(
            recipient="sales.manager@attyxai.com",
            subject=f"High-Value Lead Loss Review - ${estimated_value:,.2f}",
            body=message.replace('*', '').replace('\n', '<br>')
        )
        
        return True
