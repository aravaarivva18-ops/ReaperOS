# -*- coding: utf-8 -*-
"""
Natural Language Cron Scheduler for ReaperOS.
Parses natural language scheduling strings into standard cron expressions.
"""

import re

class ScheduleParseError(Exception):
    pass

def parse_natural_language_schedule(text: str) -> str:
    """
    Parses common natural language schedule descriptions into standard 5-field cron strings.
    """
    clean_text = text.lower().strip()
    
    if clean_text == "every minute":
        return "* * * * *"
        
    if clean_text == "every hour":
        return "0 * * * *"

    # Match: "every day at hh:mm"
    match_daily = re.match(r"^every day at (\d{1,2}):(\d{2})$", clean_text)
    if match_daily:
        hours = int(match_daily.group(1))
        minutes = int(match_daily.group(2))
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise ScheduleParseError("Invalid daily time range")
        return f"{minutes} {hours} * * *"

    # Match: "every wednesday at hh:mm" (or any other weekday name)
    match_weekly = re.match(r"^every (monday|tuesday|wednesday|thursday|friday|saturday|sunday) at (\d{1,2}):(\d{2})$", clean_text)
    if match_weekly:
        day_map = {
            "sunday": "0", "monday": "1", "tuesday": "2",
            "wednesday": "3", "thursday": "4", "friday": "5", "saturday": "6"
        }
        day_name = match_weekly.group(1)
        hours = int(match_weekly.group(2))
        minutes = int(match_weekly.group(3))
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise ScheduleParseError("Invalid weekly time range")
        return f"{minutes} {hours} * * {day_map[day_name]}"

    raise ScheduleParseError(f"Unsupported natural language schedule format: '{text}'")
