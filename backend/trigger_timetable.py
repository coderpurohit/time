import requests
import time

API_BASE = "http://localhost:8000/api"

print("Waiting for server to start...")
time.sleep(2) # Give server time to spin up

def generate():
    print("Triggering generation...")
    try:
        req = requests.post(f"{API_BASE}/solvers/generate", data={"method": "csp", "name": "Test Gen"})
        print(f"Status: {req.status_code}")
        print(f"Response: {req.json()}")
    except Exception as e:
        print(f"Generation failed: {e}")

if __name__ == "__main__":
    generate()
