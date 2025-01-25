from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime
from pydantic import BaseModel, ValidationError, validator
import phonenumbers

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []

def validate_phone_number(phone: str) -> ValidationResult:
    try:
        number = phonenumbers.parse(phone, "US")
        is_valid = phonenumbers.is_valid_number(number)
        return ValidationResult(
            is_valid=is_valid,
            errors=[] if is_valid else ["Invalid phone number format"]
        )
    except Exception as e:
        return ValidationResult(is_valid=False, errors=[str(e)])

def validate_email(email: str) -> ValidationResult:
    email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    is_valid = bool(email_regex.match(email))
    return ValidationResult(
        is_valid=is_valid,
        errors=[] if is_valid else ["Invalid email format"]
    )

def validate_date_range(start_date: datetime, end_date: datetime) -> ValidationResult:
    is_valid = start_date < end_date
    return ValidationResult(
        is_valid=is_valid,
        errors=[] if is_valid else ["End date must be after start date"]
    )

def validate_model_data(model_class: type, data: Dict[str, Any]) -> ValidationResult:
    try:
        model_class(**data)
        return ValidationResult(is_valid=True)
    except ValidationError as e:
        return ValidationResult(
            is_valid=False,
            errors=[str(error) for error in e.errors()]
        )

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> ValidationResult:
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    return ValidationResult(
        is_valid=len(missing_fields) == 0,
        errors=[f"Missing required field: {field}" for field in missing_fields]
    )

def validate_numeric_range(value: Union[int, float], min_val: Optional[float] = None, 
                         max_val: Optional[float] = None) -> ValidationResult:
    errors = []
    if min_val is not None and value < min_val:
        errors.append(f"Value must be greater than or equal to {min_val}")
    if max_val is not None and value > max_val:
        errors.append(f"Value must be less than or equal to {max_val}")
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)

def validate_string_length(text: str, min_length: Optional[int] = None, 
                         max_length: Optional[int] = None) -> ValidationResult:
    errors = []
    if min_length is not None and len(text) < min_length:
        errors.append(f"Text must be at least {min_length} characters long")
    if max_length is not None and len(text) > max_length:
        errors.append(f"Text must not exceed {max_length} characters")
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)

def validate_enum_value(value: str, enum_class: type) -> ValidationResult:
    try:
        enum_class(value)
        return ValidationResult(is_valid=True)
    except ValueError:
        valid_values = [e.value for e in enum_class]
        return ValidationResult(
            is_valid=False,
            errors=[f"Invalid value. Must be one of: {', '.join(valid_values)}"]
        )