
import requests
import json

def capture():
    try:
        r = requests.get('http://localhost:8000/api/analytics/load-factor')
        data = r.json()
        with open('load_factor_dump.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Successfully dumped load-factor to load_factor_dump.json")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    capture()
