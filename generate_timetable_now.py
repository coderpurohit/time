#!/usr/bin/env python
"""Generate timetable using CSP solver"""
import requests
import json

API_BASE = 'http://localhost:8000/api'

print("Generating timetable using CSP solver...")
print("=" * 60)

try:
    response = requests.post(
        f'{API_BASE}/solvers/generate?method=csp',
        json={},
        timeout=60
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Timetable generated successfully!")
        print(f"  - Status: {result.get('status', 'unknown')}")
        print(f"  - Message: {result.get('message', '')}")
        print(f"  - Entries: {result.get('entry_count', 0)}")
        print(f"  - Version ID: {result.get('version_id', 'N/A')}")
        
        if result.get('conflicts'):
            print(f"\n⚠ Conflicts: {result['conflicts']}")
        
        print("\n✓ Timetable is ready!")
        print("  Open http://localhost:8000/master_timetable.html to view")
    else:
        print(f"\n✗ Error: {response.text}")
        
except requests.exceptions.Timeout:
    print("✗ Timeout: Timetable generation took too long")
except Exception as e:
    print(f"✗ Error: {e}")

print("=" * 60)
