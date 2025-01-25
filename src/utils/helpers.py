from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import json
import re
from uuid import UUID

def generate_call_schedule(attempts: int = 3, 
                         initial_delay: timedelta = timedelta(minutes=10)) -> List[timedelta]:
    """Generate time delays for call attempts"""
    delays = [initial_delay]
    for i in range(1, attempts):
        delays.append(delays[-1] * 2)
    return delays

def format_phone_number(phone: str) -> str:
    """Format phone number to consistent format"""
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return phone

def safe_json_loads(data: str) -> Dict:
    """Safely load JSON data"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}

def calculate_business_hours(start_time: datetime, 
                           end_time: datetime,
                           business_start: int = 9,
                           business_end: int = 17) -> float:
    """Calculate business hours between two timestamps"""
    total_hours = 0
    current = start_time
    while current < end_time:
        if current.hour >= business_start and current.hour < business_end:
            total_hours += 1
        current += timedelta(hours=1)
    return total_hours

def serialize_uuid(obj: Any) -> Any:
    """JSON serializer for UUID objects"""
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks of specified size"""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def is_business_hours(timestamp: datetime = None,
                     start_hour: int = 9,
                     end_hour: int = 17,
                     weekend_excluded: bool = True) -> bool:
    """Check if given timestamp is within business hours"""
    if timestamp is None:
        timestamp = datetime.now()
    if weekend_excluded and timestamp.weekday() >= 5:
        return False
    return start_hour <= timestamp.hour < end_hour

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return "${:,.2f}".format(amount)

def calculate_response_time(created_at: datetime, 
                          responded_at: datetime,
                          business_hours_only: bool = True) -> float:
    """Calculate response time in hours"""
    if business_hours_only:
        return calculate_business_hours(created_at, responded_at)
    return (responded_at - created_at).total_seconds() / 3600

def mask_sensitive_data(text: str) -> str:
    """Mask sensitive data like emails and phone numbers"""
    # Mask emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, '[EMAIL]', text)
    
    # Mask phone numbers
    phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text = re.sub(phone_pattern, '[PHONE]', text)
    
    return text