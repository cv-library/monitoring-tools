
import aiosqlite
import asyncio
from quart import Quart, request, jsonify
from datetime import datetime, timedelta

app = Quart(__name__)
#                 last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,


async def init_db():
    async with aiosqlite.connect('metrics.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                app_name TEXT,
                metric_name TEXT,
                value REAL,
                schedule TEXT,
                host TEXT,
                last_updated DATETIME DEFAULT NULL,
                next_run DATETIME DEFAULT NULL,
                PRIMARY KEY (app_name, metric_name, host)
            )
        ''')
        await db.commit()


def datetime_to_timestamp(datetime_input):
    # Check if the input is already a datetime object
    if isinstance(datetime_input, datetime):
        return datetime_input.timestamp()
    else:
        # If it's a string, convert it to a datetime object first
        datetime_obj = datetime.strptime(datetime_input, "%Y-%m-%d %H:%M:%S")
        return datetime_obj.timestamp()



def calculate_next_run(last_updated, schedule):
    if len(schedule) != 8:
        return None

    minute, hour, day, month = schedule[:2], schedule[2:4], schedule[4:6], schedule[6:8]
    next_run = last_updated.replace(second=0, microsecond=0)

    if minute != "**":
        next_run = next_run.replace(minute=int(minute))
    if hour != "**":
        next_run = next_run.replace(hour=int(hour))
    if day != "**":
        next_run = next_run.replace(day=int(day))
    if month != "**":
        next_run = next_run.replace(month=int(month))

    if next_run <= last_updated:
        if minute != "**" and hour != "**" and day == "**" and month == "**":
            next_run += timedelta(days=1)
        elif day != "**" and month == "**":
            next_month = next_run.month + 1 if next_run.month < 12 else 1
            next_run = next_run.replace(month=next_month)
        elif month != "**":
            next_run = next_run.replace(year=next_run.year + 1)
        elif minute != "**" and hour == "**":
            next_run += timedelta(hours=1)
        else:
            next_run += timedelta(hours=1)

    return next_run

async def insert_or_update_metric(app_name, metric_name, value, schedule, host):
    last_updated = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    next_run = calculate_next_run(last_updated, schedule)

    async with aiosqlite.connect('metrics.db') as db:
        await db.execute('''
            INSERT INTO metrics (app_name, metric_name, value, schedule, host, last_updated, next_run) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(app_name, metric_name, host) 
            DO UPDATE SET value=excluded.value, schedule=excluded.schedule, 
            last_updated=CURRENT_TIMESTAMP, next_run=excluded.next_run
        ''', (app_name, metric_name, value, schedule, host, last_updated, next_run))
        await db.commit()

# Asynchronous endpoint to post a metric
@app.route('/v1/post_metric', methods=['POST'])
async def post_metric():
    data = await request.get_json()

    app_name = data.get('app_name')
    metric_name = data.get('metric_name')
    value = data.get('value')
    schedule = data.get('schedule')
    host = data.get('host')

    await insert_or_update_metric(app_name, metric_name, value, schedule, host)

    status = "success" if value == 0 else "failed"
    return jsonify({"app": app_name, "metric": metric_name, "status": status, "host": host}), 200

@app.route('/metrics', methods=['GET'])
async def metrics():
    response = ""
    current_time = datetime.utcnow()
    

    async with aiosqlite.connect('metrics.db') as db:
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
                    if current_time < next_run + timedelta(hours=1):
                        response += f'{metric_name}{{app="{app_name}", status="{status}", host="{host}"}} 1\n'
                    else:
                        response += f'{metric_name}{{app="{app_name}", status="missing", host="{host}"}} 1\n'
                else:
                    response += f'{metric_name}{{app="{app_name}", status="missing", host="{host}"}} 1\n'

        async with db.execute('SELECT app_name, metric_name, value, host, next_run FROM metrics') as cursor1:
            repeat = True
            async for app_name, metric_name, value, host, next_run_str in cursor1:
                if repeat:
                    response += f'# HELP cron_execution_next_run Next run for cronjob executions\n'
                    response += f'# TYPE cron_execution_next_run gauge\n'
                    repeat = False

                if next_run_str:
                    next_run = datetime.strptime(next_run_str, "%Y-%m-%d %H:%M:%S")
                    timestamp = int(datetime_to_timestamp(next_run))
                    response += f'cron_execution_next_run{{app="{app_name}", host="{host}"}} {timestamp}\n'

        async with db.execute('SELECT app_name, metric_name, value, host, last_updated, next_run FROM metrics') as cursor2:
            repeat = True
            async for app_name, metric_name, value, host,last_updated, next_run_str in cursor2:
                if repeat:
                    response += f'# HELP cron_execution_last_run Last run for cronjob executions\n'
                    response += f'# TYPE cron_execution_last_run gauge\n'
                    repeat = False

                if last_updated:
                    last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                    timestamp = int(datetime_to_timestamp(last_updated))
                    response += f'cron_execution_last_run{{app="{app_name}", host="{host}"}} {timestamp}\n'


    return response, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    asyncio.run(init_db())  
    app.run(host='0.0.0.0', port=5002, debug=True)