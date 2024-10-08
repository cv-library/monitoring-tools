import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('metrics.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            app_name TEXT,
            metric_name TEXT,
            value REAL,
            schedule TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
            next_run DATETIME DEFAULT NULL,
            PRIMARY KEY (app_name, metric_name)
        )
    ''')
    conn.commit()
    conn.close()

# Function to calculate next run
def calculate_next_run(last_updated, schedule):

    
    if len(schedule) != 8:
        return None  

    minute, hour, day, month = schedule[:2], schedule[2:4], schedule[4:6], schedule[6:8]

    # (remove in case timezone .Z or add manually)
    next_run = last_updated.replace(second=0, microsecond=0)

    # formating minute, hour, day, and month according to the schedule
    if minute != "**":
        next_run = next_run.replace(minute=int(minute))
    if hour != "**":
        next_run = next_run.replace(hour=int(hour))
    if day != "**":
        next_run = next_run.replace(day=int(day))
    if month != "**":
        next_run = next_run.replace(month=int(month))

    # when next_run is in the past, increment it to the next valid time*******
    if next_run <= last_updated:
        
        if minute != "**" and hour != "**" and day == "**" and month == "**":
            next_run += timedelta(days=1)  # ****** Move to the same time next day ******
        
        elif day != "**" and month == "**":
            if next_run.day <= last_updated.day:
                # *****Move to the same day in the next month******
                next_month = next_run.month + 1 if next_run.month < 12 else 1
                next_run = next_run.replace(month=next_month)
        # If schedule is yearly
        elif month != "**":
            if next_run.month < last_updated.month or (next_run.month == last_updated.month and next_run.day <= last_updated.day):
                next_run = next_run.replace(year=next_run.year + 1)
        # If schedule is hourly (min specified, but not hour)
        elif minute != "**" and hour == "**":
            next_run += timedelta(hours=1)  # Move to the same minute next hour
        else:
            # Default: increment by one hour if nothing else matches for the next hour
            next_run += timedelta(hours=1)

    return next_run

# Insert or update a metric, calculating the next_run value
def insert_or_update_metric(app_name, metric_name, value, schedule):
    conn = sqlite3.connect('metrics.db')
    c = conn.cursor()

#    last_updated_local = datetime.utcnow()
 
    last_updated = datetime.utcnow()
    next_run = calculate_next_run(last_updated, schedule)
#    next_run_local = calculate_next_run(last_updated_local, schedule)

    # Insert or update the metric with app_name, metric_name, etc
    c.execute('''
        INSERT INTO metrics (app_name, metric_name, value, schedule, last_updated, next_run) 
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(app_name, metric_name) 
        DO UPDATE SET value=excluded.value, schedule=excluded.schedule, last_updated=CURRENT_TIMESTAMP, next_run=excluded.next_run
    ''', (app_name, metric_name, value, schedule, last_updated, next_run))
    conn.commit()
    conn.close()

# Endpoint to post a metric (PUT in case of changing response)
@app.route('/v1/post_metric', methods=['POST'])
def post_metric():
    data = request.get_json()
    
    app_name = data.get('app_name')
    metric_name = data.get('metric_name')
    value = data.get('value')
    schedule = data.get('schedule')

    # Insert or update the metric with the extracted fields
    insert_or_update_metric(app_name, metric_name, value, schedule)
    
  
    status = "success" if value == 0 else "failed"

  
    return jsonify({"app": app_name, "metric": metric_name, "status": status}), 200


@app.route('/metrics', methods=['GET'])
def metrics():
    conn = sqlite3.connect('metrics.db')
    c = conn.cursor()
    c.execute('SELECT app_name, metric_name, value, next_run FROM metrics')
    metrics = c.fetchall()
    conn.close()

    response = ""
    current_time = datetime.utcnow()
    repeat=True
    for app_name, metric_name, value, next_run_str in metrics:
        if repeat == True:
            response += f'# HELP {metric_name} ount of cronjob executions\n'
            response += f'# TYPE {metric_name} counter\n'
            repeat = False

        if next_run_str:
            next_run = datetime.strptime(next_run_str, "%Y-%m-%d %H:%M:%S")
            status = "success" if value == 0 else "failed"
            if current_time < next_run + timedelta(hours=1):






                response += f'{metric_name}{{app="{app_name}", status="{status}"}} 1\n'
            else:
                response += f'{metric_name}{{app="{app_name}", status="missing"}} 1\n'
        else:
            response += f'{metric_name}{{app="{app_name}", status="missing"}} 1\n'
    
    return response, 200, {'Content-Type': 'text/plain'}
#    return {next_run, valid_until}

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
