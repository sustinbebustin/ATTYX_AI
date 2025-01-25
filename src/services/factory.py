from typing import Optional, Type, TypeVar
from .interfaces.database import DatabaseServiceInterface
from .interfaces.notification import NotificationServiceInterface
from .database_service import DatabaseService
from .notification_service import NotificationService

T = TypeVar('T')

class ServiceFactory:
    """Factory for creating service instances with dependency injection support"""
    
    _database_service: Optional[DatabaseServiceInterface] = None
    _notification_service: Optional[NotificationServiceInterface] = None
    
    @classmethod
    def get_database_service(
        cls,
        implementation: Optional[Type[DatabaseServiceInterface]] = None
    ) -> DatabaseServiceInterface:
        """Get database service instance
        
        Args:
            implementation: Optional custom implementation class
            
        Returns:
            Database service instance
        """
        if not cls._database_service:
            service_class = implementation or DatabaseService
            cls._database_service = service_class()
        return cls._database_service
        
    @classmethod
    def get_notification_service(
        cls,
        implementation: Optional[Type[NotificationServiceInterface]] = None
    ) -> NotificationServiceInterface:
        """Get notification service instance
        
        Args:
            implementation: Optional custom implementation class
            
        Returns:
            Notification service instance
        """
        if not cls._notification_service:
            service_class = implementation or NotificationService
            cls._notification_service = service_class()
        return cls._notification_service
        
    @classmethod
    def set_service_implementation(cls, interface_type: Type[T], implementation: T) -> None:
        """Set a custom service implementation
        
        Args:
            interface_type: Service interface type
            implementation: Service implementation instance
        """
        if issubclass(interface_type, DatabaseServiceInterface):
            cls._database_service = implementation
        elif issubclass(interface_type, NotificationServiceInterface):
            cls._notification_service = implementation
        else:
            raise ValueError(f"Unknown service type: {interface_type}")
            
    @classmethod
    def reset(cls) -> None:
        """Reset all service instances (useful for testing)"""
        cls._database_service = None
        cls._notification_service = None
