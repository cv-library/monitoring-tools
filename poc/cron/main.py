import aiosqlite
import asyncio
from quart import Quart, request, jsonify
from datetime import datetime, timedelta, timezone
import pytz
#import cron.nextrun as nextrun
import re
from nextrun import calculate_next_run 
import logging
app = Quart(__name__)
#                 last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,


async def init_db():
    async with aiosqlite.connect('/db/metrics.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                app_name TEXT,
                metric_name TEXT,
                value REAL,
                schedule TEXT,
                host TEXT,
                last_updated DATETIME DEFAULT NULL,
                next_run DATETIME DEFAULT NULL,
                duration_sec REAL DEFAULT 0,
                PRIMARY KEY (app_name, metric_name, host)
            )
        ''')
        await db.commit()

#def parse_mixed_datetime(datetime_str):
#    try:
#        # Try parsing with microseconds first
#        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
#    except ValueError:
#        # If microseconds are not present, parse without them
#        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def parse_mixed_datetime(datetime_str):
    # Separate microseconds and timezone offset using regex
    match = re.match(r"(?P<datetime>[\d-]+\s[\d:.]+)(?P<offset>[+-]\d{2}:\d{2})?", datetime_str)

    if not match:
        raise ValueError(f"Unrecognized datetime format: {datetime_str}")

    # Parse datetime part
    dt = datetime.strptime(match.group("datetime"), "%Y-%m-%d %H:%M:%S.%f" if "." in match.group("datetime") else "%Y-%m-%d %H:%M:%S")

    # If there's a timezone offset, apply it
    if match.group("offset"):
        offset_hours, offset_minutes = map(int, match.group("offset").split(":"))
        offset = timedelta(hours=offset_hours, minutes=offset_minutes)
        dt = dt.replace(tzinfo=timezone(offset))
    else:
        # If no offset is provided, assume UTC
        dt = dt.replace(tzinfo=timezone.utc)

    return dt

#
# def parse_mixed_datetime(datetime_str):
#
#     # Separate microseconds and timezone offset using regex
#
#     match = re.match(r"(?P<datetime>[\d-]+\s[\d:.]+)(?P<offset>[+-]\d{2}:\d{2})?", datetime_str)
#

#
#     if not match:
#
#         raise ValueError(f"Unrecognized datetime format: {datetime_str}")
#

#
#     # Parse datetime part
#
#     dt = datetime.strptime(match.group("datetime"), "%Y-%m-%d %H:%M:%S.%f" if "." in match.group("datetime") else "%Y-%m-%d %H:%M:%S")
#

#
#     # If there's a timezone offset, apply it
#
#     if match.group("offset"):
#
#         from datetime import timezone, timedelta
#
#         offset_hours, offset_minutes = map(int, match.group("offset").split(":"))
#
#         offset = timedelta(hours=offset_hours, minutes=offset_minutes)
#        dt = dt.replace(tzinfo=timezone(offset))
#
#    return dt


def datetime_to_timestamp(datetime_input):
    
    if isinstance(datetime_input, datetime):
        return datetime_input.timestamp()
    else:
    
        datetime_obj = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")
        return datetime_obj.timestamp()



###def calculate_next_run(last_updated, schedule):
###    if len(schedule) != 8:
###        return None

####    minute, hour, day, month = schedule[:2], schedule[2:4], schedule[4:6], schedule[6:8]
####    next_run = last_updated.replace(second=0, microsecond=0)
####
####    if minute != "**":
####        next_run = next_run.replace(minute=int(minute))
####    if hour != "**":
####        next_run = next_run.replace(hour=int(hour))
####    if day != "**":
####        next_run = next_run.replace(day=int(day))
####    if month != "**":
####        next_run = next_run.replace(month=int(month))
####
####    if next_run <= last_updated:
####        if minute != "**" and hour != "**" and day == "**" and month == "**":
####            next_run += timedelta(days=1)
####        elif day != "**" and month == "**":
####            next_month = next_run.month + 1 if next_run.month < 12 else 1
####            next_run = next_run.replace(month=next_month)
####        elif month != "**":
####            next_run = next_run.replace(year=next_run.year + 1)
####        elif minute != "**" and hour == "**":
####            next_run += timedelta(hours=1)
####        else:
####            next_run += timedelta(hours=1)
####
####    return next_run

async def insert_or_update_metric(app_name, metric_name, value, schedule, host, last_updated, next_run, duration_sec):
#    last_updated = datetime.utcnow()#.strftime("%Y-%m-%d %H:%M:%S")
    
#    next_run = calculate_next_run(last_updated, schedule)

    async with aiosqlite.connect('/db/metrics.db') as db:
        await db.execute('''
            INSERT INTO metrics (app_name, metric_name, value, schedule, host, last_updated, next_run, duration_sec) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(app_name, metric_name, host) 
            DO UPDATE SET value=excluded.value, schedule=excluded.schedule, 
            last_updated=excluded.last_updated, next_run=excluded.next_run, duration_sec=excluded.duration_sec
        ''', (app_name, metric_name, value, schedule, host, last_updated, next_run, duration_sec))
        await db.commit()

# Asynchronous endpoint to post a metric
@app.route('/v1/post_metric', methods=['POST'])
async def post_metric():
    bst = pytz.timezone('Europe/London')
    data = await request.get_json()

    app_name = data.get('app_name')
    metric_name = data.get('metric_name')
    value = data.get('value')
    schedule = data.get('schedule')
    duration_ts = data.get('duration_ts', 0)
    duration_sec = data.get('duration_sec', 0)

    host = data.get('host')
    last_updated = datetime.now(bst) #.strftime("%Y-%m-%d %H:%M:%S")
   
    next_run = calculate_next_run(last_updated, schedule)
    next_run_timestamp = datetime_to_timestamp(next_run)
    duration_minutes = 0
    new_next_run = next_run
    if duration_ts:
#        duration_minutes = int(next_run_timestamp - duration_ts)/60
        duration_minutes = int(duration_ts - next_run_timestamp)/60

        new_next_run_dt = next_run + timedelta(minutes=duration_minutes)
        new_next_run = new_next_run_dt.strftime("%Y-%m-%d %H:%M:%S")

    if duration_sec:
        duration_minutes = int(duration_sec / 60)

        new_next_run_dt = next_run + timedelta(minutes=duration_minutes)
        new_next_run = new_next_run_dt.strftime("%Y-%m-%d %H:%M:%S")
    

    
    await insert_or_update_metric(app_name, metric_name, value, schedule, host, last_updated, new_next_run, duration_sec)

    status = "success" if value == 0 else "failed"
    log_json = {"app": app_name, "metric": metric_name, "status": status, "host": host, "schedule": schedule, "new_next_run": new_next_run,"next_run": next_run, "duration_min": duration_minutes}
    logging.info(f"Log Data: {log_json}")

    return jsonify(log_json), 200

@app.route('/metrics', methods=['GET'])
async def metrics():
    response = ""
    bst = pytz.timezone('Europe/London')

    current_time = datetime.now(bst)
    current_time= current_time.replace(microsecond=0, tzinfo=None)

    async with aiosqlite.connect('/db/metrics.db', timeout=10) as db:
        async with db.execute('SELECT app_name, metric_name, value, host, next_run FROM metrics') as cursor:
            repeat = True
            async for app_name, metric_name, value, host, next_run_str in cursor:
                if repeat:
                    response += f'# HELP {metric_name} Count of cronjob executions\n'
                    response += f'# TYPE {metric_name} counter\n'
                    repeat = False

                if next_run_str:
                    next_run = datetime.strptime(next_run_str, "%Y-%m-%d %H:%M:%S")
                    status = "success" if value == 0 else "failed"
#                    if current_time < next_run + timedelta(hours=1):
                    #next_run = next_run.astimezone(bst)
                    if current_time < next_run:
                        response += f'{metric_name}{{app="{app_name}", status="{status}", host="{host}"}} 1\n'
                    else:
                        response += f'{metric_name}{{app="{app_name}", status="missing", host="{host}"}} 1\n'
                else:
                    response += f'{metric_name}{{app="{app_name}", status="missing", host="{host}"}} 1\n'
#
        async with db.execute('SELECT app_name, metric_name, value, host, next_run FROM metrics') as cursor1:
            repeat = True
            async for app_name, metric_name, value, host, next_run_str in cursor1:
                if repeat:
                    response += f'# HELP cron_execution_next_run Next run for cronjob executions\n'
                    response += f'# TYPE cron_execution_next_run gauge\n'
                    repeat = False
#
                if next_run_str:
                    next_run = datetime.strptime(next_run_str, "%Y-%m-%d %H:%M:%S")
                    timestamp = int(datetime_to_timestamp(next_run))
                    response += f'cron_execution_next_run{{app="{app_name}", host="{host}"}} {timestamp}\n'
#
        async with db.execute('SELECT app_name, metric_name, value, host, last_updated, next_run FROM metrics') as cursor2:
            repeat = True
            async for app_name, metric_name, value, host,last_updated, next_run_str in cursor2:
                if repeat:
                    response += f'# HELP cron_execution_last_run Last run for cronjob executions\n'
                    response += f'# TYPE cron_execution_last_run gauge\n'
                    repeat = False
#
                if last_updated:
#                    last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                   
                    timestamp = int(datetime_to_timestamp(parse_mixed_datetime(last_updated)))
#                    timestamp = 3333
                    response += f'cron_execution_last_run{{app="{app_name}", host="{host}"}} {timestamp}\n'


        async with db.execute('SELECT app_name, metric_name, value, host, last_updated, next_run, duration_sec FROM metrics') as cursor3:
            repeat = True
            async for app_name, metric_name, value, host,last_updated, next_run_str, duration_sec in cursor3:
                if repeat:
                    response += f'# HELP cron_execution_duration Duration for cronjob executions\n'
                    response += f'# TYPE cron_execution_duration gauge\n'
                    repeat = False
#
                if duration_sec:
                    response += f'cron_execution_duration{{app="{app_name}", host="{host}"}} {duration_sec}\n'



    return response, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())  
    app.run(host='0.0.0.0', port=5902, debug=True)
