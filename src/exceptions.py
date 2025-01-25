from typing import Optional, Any

class LeadUpdateError(Exception):
    """Exception raised for lead update business rule violations"""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None) -> None:
        """Initialize LeadUpdateError
        
        Args:
            message: Error message
            original_error: Optional underlying exception
        """
        super().__init__(message)
        self.original_error = original_error
        
    def __str__(self) -> str:
        """Format error message with original error if present"""
        base_msg = super().__str__()
        if self.original_error:
            return f"{base_msg} (Caused by: {self.original_error})"
        return base_msg
