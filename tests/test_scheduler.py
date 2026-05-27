import pytest
from engine.scheduler import parse_natural_language_schedule, ScheduleParseError

def test_parse_natural_language_schedule():
    assert parse_natural_language_schedule("every minute") == "* * * * *"
    assert parse_natural_language_schedule("every hour") == "0 * * * *"
    assert parse_natural_language_schedule("every day at 12:00") == "0 12 * * *"
    assert parse_natural_language_schedule("every Wednesday at 03:00") == "0 3 * * 3"
    assert parse_natural_language_schedule("every day at 23:59") == "59 23 * * *"

def test_parse_natural_language_schedule_errors():
    with pytest.raises(ScheduleParseError):
        parse_natural_language_schedule("every year at 12:00")
        
    with pytest.raises(ScheduleParseError):
        parse_natural_language_schedule("every day at 25:00")
