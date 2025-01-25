import pytest
from datetime import datetime, timedelta
from src.utils.validators import (
    validate_phone_number,
    validate_email,
    validate_date_range,
    validate_numeric_range,
    validate_string_length
)
from src.utils.helpers import (
    generate_call_schedule,
    format_phone_number,
    calculate_business_hours,
    is_business_hours,
    mask_sensitive_data
)

class TestValidators:
    def test_phone_validation(self):
        assert validate_phone_number("(123) 456-7890").is_valid
        assert not validate_phone_number("123-456").is_valid
        assert validate_phone_number("+1 (123) 456-7890").is_valid

    def test_email_validation(self):
        assert validate_email("test@example.com").is_valid
        assert not validate_email("invalid.email").is_valid
        assert validate_email("user.name+tag@example.com").is_valid

    def test_date_range_validation(self):
        start = datetime.now()
        end = start + timedelta(days=1)
        assert validate_date_range(start, end).is_valid
        assert not validate_date_range(end, start).is_valid

    def test_numeric_range_validation(self):
        assert validate_numeric_range(5, min_val=0, max_val=10).is_valid
        assert not validate_numeric_range(-1, min_val=0).is_valid
        assert not validate_numeric_range(11, max_val=10).is_valid

    def test_string_length_validation(self):
        assert validate_string_length("test", min_length=2, max_length=10).is_valid
        assert not validate_string_length("a", min_length=2).is_valid
        assert not validate_string_length("toolongstring", max_length=10).is_valid

class TestHelpers:
    def test_call_schedule_generation(self):
        schedule = generate_call_schedule(3)
        assert len(schedule) == 3
        assert schedule[1] > schedule[0]
        assert schedule[2] > schedule[1]

    def test_phone_formatting(self):
        assert format_phone_number("1234567890") == "(123) 456-7890"
        assert format_phone_number("11234567890") == "(123) 456-7890"
        assert format_phone_number("123-456-7890") == "(123) 456-7890"

    def test_business_hours_calculation(self):
        start = datetime(2025, 1, 1, 9, 0)  # 9 AM
        end = datetime(2025, 1, 1, 17, 0)   # 5 PM
        hours = calculate_business_hours(start, end)
        assert hours == 8

    def test_business_hours_check(self):
        business_time = datetime(2025, 1, 1, 14, 0)  # 2 PM on Wednesday
        non_business_time = datetime(2025, 1, 1, 20, 0)  # 8 PM
        weekend_time = datetime(2025, 1, 4, 14, 0)  # 2 PM on Saturday

        assert is_business_hours(business_time)
        assert not is_business_hours(non_business_time)
        assert not is_business_hours(weekend_time)

    def test_sensitive_data_masking(self):
        text = "Contact john@example.com or call (123) 456-7890"
        masked = mask_sensitive_data(text)
        assert "[EMAIL]" in masked
        assert "[PHONE]" in masked
        assert "john@example.com" not in masked
        assert "(123) 456-7890" not in masked