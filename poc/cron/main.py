import aiosqlite
import asyncio
from quart import Quart, request, jsonify
from datetime import datetime, timedelta

app = Quart(__name__)


async def init_db():
    async with aiosqlite.connect('metrics.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                app_name TEXT,
                metric_name TEXT,
                value REAL,
                schedule TEXT,
                host TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                next_run DATETIME DEFAULT NULL,
                PRIMARY KEY (app_name, metric_name)
            )
        ''')
        await db.commit()

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
    last_updated = datetime.utcnow()
    next_run = calculate_next_run(last_updated, schedule)

    async with aiosqlite.connect('metrics.db') as db:
        await db.execute('''
            INSERT INTO metrics (app_name, metric_name, value, schedule, host, last_updated, next_run) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(app_name, metric_name) 
            DO UPDATE SET value=excluded.value, schedule=excluded.schedule, host=excluded.host, 
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
    repeat = True

    async with aiosqlite.connect('metrics.db') as db:
        async with db.execute('SELECT app_name, metric_name, value, host, next_run FROM metrics') as cursor:
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

    return response, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    asyncio.run(init_db())  
    app.run(host='0.0.0.0', port=5002, debug=True)