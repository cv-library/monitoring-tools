from datetime import datetime, timedelta
from calendar import monthrange, isleap

def parse_schedule_component(component, max_value, is_day_or_month=False, is_weekday=False):
    """
    Parse a schedule component to handle individual values, ranges, and steps.
    Supports combinations like 2-59/5, 6-18/2, and more.
    `is_day_or_month`: Set True for day and month values to ensure 1-based indexing.
    `is_weekday`: Set True for weekday values to ensure 1-7 indexing for weekdays.
    """
    values = set()

    # Set 1-based index for days, months, and weekdays
    if component == "*":
        if is_day_or_month or is_weekday:
            return set(range(1, max_value + 1))  # 1-based index for days, months, and weekdays
        else:
            return set(range(max_value + 1))  # 0-based index for other fields

    # Handle comma-separated parts (e.g., 5,8,10-15,2-59/5)
    for part in component.split(','):
        if '-' in part and '/' in part:
            # Handle ranges with steps (e.g., 2-59/5)
            range_part, step_part = part.split('/')
            start, end = map(int, range_part.split('-'))
            step = int(step_part)
            values.update(range(start, end + 1, step))
        elif '/' in part:
            # Handle steps (e.g., */10)
            step = int(part.split('/')[1])
            start = 1 if is_day_or_month or is_weekday else 0
            values.update(range(start, max_value + 1, step))
        elif '-' in part:
            # Handle ranges (e.g., 10-15)
            start, end = map(int, part.split('-'))
            values.update(range(start, end + 1))
        else:
            # Handle individual values (e.g., 5,8)
            values.add(int(part))

    return values

def adjust_days_set_for_month(days_set, year, month):
    """
    Adjust the days set to only include valid days for the given month and year.
    """
    max_days = monthrange(year, month)[1]  # Get the maximum number of days in the given month
    return {day for day in days_set if day <= max_days}

def find_next_run(last_updated, minutes_set, hours_set, days_set, months_set, weekdays_set):
    """Find the next run time considering all components including weekday and day ranges."""
    year = last_updated.year
    current_month = last_updated.month
    current_day = last_updated.day
    current_hour = last_updated.hour
    current_minute = last_updated.minute

    # Iterate over months to find the next valid month
    for month in sorted(months_set):
        if month < current_month:
            continue  # Skip past months

        # Adjust days set based on the current month and year
        adjusted_days_set = adjust_days_set_for_month(days_set, year, month)

        # If month is in the future, reset days, hours, and minutes
        if month > current_month:
            current_day, current_hour, current_minute = 1, 0, 0

        # Iterate over days in the given month
        for day in sorted(adjusted_days_set):
            if day < current_day:
                continue  # Skip past days

            # Check if this day is a valid weekday (1=Monday, 7=Sunday)
            weekday = datetime(year, month, day).isoweekday()
            if weekday not in weekdays_set:
                continue

            # If day is in the future, reset hours and minutes
            if day > current_day:
                current_hour, current_minute = 0, 0

            # Iterate over hours
            for hour in sorted(hours_set):
                if hour < current_hour:
                    continue  # Skip past hours

                # If hour is in the future, reset minutes
                if hour > current_hour:
                    current_minute = 0

                # Iterate over minutes
                for minute in sorted(minutes_set):
                    if minute <= current_minute and (minute != current_minute or hour != current_hour or day != current_day or month != current_month):
                        continue  # Skip past or same minutes unless we are at a new unit

                    # Return the next valid run time
                    return datetime(year, month, day, hour, minute)

    # If no valid time found in current year, move to the next year
    return find_next_run(datetime(year + 1, 1, 1), minutes_set, hours_set, days_set, months_set, weekdays_set)

def calculate_next_run(last_updated, schedule):
    """Calculate the next run time based on the extended schedule format with ranges and steps."""
    # Split the schedule into components (minute, hour, day, month, weekday)
    minute, hour, day, month, weekday = schedule.split('|')

    # Parse each component to handle ranges, steps, and individual values
    minutes_set = parse_schedule_component(minute, 59)
    hours_set = parse_schedule_component(hour, 23)
    days_set = parse_schedule_component(day, 31, is_day_or_month=True)
    months_set = parse_schedule_component(month, 12, is_day_or_month=True)
    weekdays_set = parse_schedule_component(weekday, 7, is_weekday=True)

    # Print debug info to verify values
#    print(f"Minutes set: {sorted(minutes_set)}")
#    print(f"Hours set: {sorted(hours_set)}")
#    print(f"Days set (initial): {sorted(days_set)}")
#    print(f"Months set: {sorted(months_set)}")
#    print(f"Weekdays set: {sorted(weekdays_set)}")

    # Find the next run using component-by-component adjustment, including weekday
    next_run = find_next_run(last_updated, minutes_set, hours_set, days_set, months_set, weekdays_set)
    return next_run


#if __name__ == "__main__":
#    last_updated = datetime(2028, 2, 29, 11, 13)  # Example last updated time
#    schedule = "2-59/5|11-18/2|*|*|*"  # Every 5 minutes from 2-59, every 2 hours from 6-18, any day, any month, any weekday
#    next_run = calculate_next_run(last_updated, schedule)
#    print("Next run:", next_run)