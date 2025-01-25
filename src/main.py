import asyncio
import logging
from typing import Optional

from fastapi import FastAPI
from config.settings import Settings
from config.logging import setup_logging
from services.database_service import DatabaseService
from services.notification_service import NotificationService
from services.api_service import APIService
from services.analytics_service import AnalyticsService

app = FastAPI(title="ATTYX AI", version="0.1.0")
settings = Settings()
logger = logging.getLogger(__name__)

async def startup():
    """Initialize services and connections"""
    setup_logging()
    logger.info("Starting ATTYX AI Platform")
    
    # Initialize services
    db = await DatabaseService.initialize(settings)
    notification = await NotificationService.initialize(settings)
    api = await APIService.initialize(settings)
    analytics = await AnalyticsService.initialize(settings)
    
    return db, notification, api, analytics

async def shutdown():
    """Cleanup and close connections"""
    logger.info("Shutting down ATTYX AI Platform")
    # Cleanup code here

def main():
    """Main entry point for the application"""
    try:
        asyncio.run(startup())
        # Additional startup code here
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    finally:
        asyncio.run(shutdown())

if __name__ == "__main__":
    main()