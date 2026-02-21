import json
from urllib.request import Request, urlopen

url = 'http://127.0.0.1:8000/api/operational/schedule-config'
payload = {
    "day_start_time": "09:00",
    "working_minutes_per_day": 360,
    "number_of_periods": 7,
    "period_duration_minutes": 60,
    "lunch_break_start": "12:00",
    "lunch_break_end": "13:00",
    "schedule_days": ["Monday","Tuesday","Wednesday","Thursday","Friday"]
}

data = json.dumps(payload).encode('utf-8')
req = Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
try:
    with urlopen(req, timeout=30) as resp:
        body = resp.read().decode('utf-8')
        print(resp.getcode())
        print(body)
except Exception as e:
    print('ERROR', e)
