import os
import logging
import json
from datetime import datetime
import aiohttp
from typing import Any, Optional

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.environment = os.getenv("TELEGRAM_BOT_ENVIRONMENT", "test")
        self.chat_id = -1002328089278 # MutimTemki chat
        self.thread_id = 552 # Logs thread

    async def track_event(
        self,
        user_id: str,
        action: str,
        data: Any,
        user_name: Optional[str] = None,
        source: str = '(not set)'
    ) -> None:
        """
        Track an analytics event by sending it to Telegram chat
        """
        if self.environment != "prod":
            logger.debug(f"Skipping analytics in {self.environment} environment")
            return

        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN not configured")
            return

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        message = f"""
Timestamp: {timestamp} UTC
User ID: {user_id}
Name: {user_name or '-'}
Action: {action}
Data: {json.dumps(data) if isinstance(data, (dict, list)) else str(data)}
Source: {source}
        """.strip()

        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    "chat_id": self.chat_id,
                    "message_thread_id": self.thread_id,
                    "text": message,
                    "disable_web_page_preview": True
                }
                
                async with session.post(url, json=data) as response:
                    if response.status != 200:
                        response_text = await response.text()
                        logger.error(f"Failed to send analytics event. Status: {response.status}, Response: {response_text}")
                    else:
                        logger.debug(f"Successfully sent analytics event: {action}")
                        
        except Exception as e:
            logger.error(f"Error sending analytics event: {str(e)}")

# Create a global instance
analytics = AnalyticsService() 