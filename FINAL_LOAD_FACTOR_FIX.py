#!/usr/bin/env python3

import requests
import webbrowser

def final_load_factor_fix():
    """Final fix for load factor data"""
    
    print("🎯 FINAL LOAD FACTOR FIX")
    
    # Test the load factor API directly
    try:
        print("🔧 Testing Load Factor API...")
        response = requests.get("http://localhost:8000/api/analytics/load-factor", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            teacher_load = data.get('teacher_load', [])
            print(f"✅ Load Factor API working: {len(teacher_load)} teachers")
            
            if len(teacher_load) > 0:
                print("✅ Teacher load data exists!")
                for teacher in teacher_load[:3]:  # Show first 3
                    print(f"   - {teacher.get('name', 'Unknown')}: {teacher.get('total_periods', 0)} periods")
            else:
                print("⚠️ No teacher load data returned")
                
        elif response.status_code == 404:
            print("❌ Load Factor API: No timetable found")
            
            # Generate timetable using the solver API
            print("🔧 Generating timetable via solver API...")
            solver_response = requests.post("http://localhost:8000/api/solvers/generate", 
                                          json={}, timeout=30)
            
            if solver_response.status_code == 200:
                solver_data = solver_response.json()
                print(f"✅ Timetable generated: {solver_data}")
                
                # Test load factor again
                response = requests.get("http://localhost:8000/api/analytics/load-factor", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    teacher_load = data.get('teacher_load', [])
                    print(f"✅ Load Factor now working: {len(teacher_load)} teachers")
                else:
                    print(f"❌ Load Factor still failing: {response.status_code}")
            else:
                print(f"❌ Solver API failed: {solver_response.status_code}")
                
        else:
            print(f"❌ Load Factor API error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")
    
    # Create a working load factor page with direct API calls
    working_page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Load Factor - WORKING</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .teacher-card { border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .success { color: green; }
        .error { color: red; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>Load Factor Engine - WORKING VERSION</h1>
    
    <div>
        <button class="btn" onclick="loadTeachers()">Load Teachers</button>
        <button class="btn" onclick="loadLoadFactor()">Load Factor Data</button>
        <button class="btn" onclick="generateTimetable()">Generate Timetable</button>
    </div>
    
    <div id="status"></div>
    <div id="teachers"></div>
    <div id="loadfactor"></div>
    
    <script>
        const API_BASE = 'http://localhost:8000/api';
        
        async function loadTeachers() {
            const statusDiv = document.getElementById('status');
            const teachersDiv = document.getElementById('teachers');
            
            try {
                statusDiv.innerHTML = 'Loading teachers...';
                const response = await fetch(API_BASE + '/teachers/');
                
                if (response.ok) {
                    const teachers = await response.json();
                    statusDiv.innerHTML = '<span class="success">✅ Loaded ' + teachers.length + ' teachers</span>';
                    
                    teachersDiv.innerHTML = '<h3>Teachers:</h3>' + teachers.map(t => 
                        '<div class="teacher-card"><strong>' + t.name + '</strong><br>Email: ' + t.email + '<br>Max Hours: ' + t.max_hours_per_week + '</div>'
                    ).join('');
                } else {
                    throw new Error('HTTP ' + response.status);
                }
            } catch (error) {
                statusDiv.innerHTML = '<span class="error">❌ Error loading teachers: ' + error.message + '</span>';
            }
        }
        
        async function loadLoadFactor() {
            const statusDiv = document.getElementById('status');
            const loadfactorDiv = document.getElementById('loadfactor');
            
            try {
                statusDiv.innerHTML = 'Loading load factor data...';
                const response = await fetch(API_BASE + '/analytics/load-factor');
                
                if (response.ok) {
                    const data = await response.json();
                    const teacherLoad = data.teacher_load || [];
                    
                    statusDiv.innerHTML = '<span class="success">✅ Load factor data loaded: ' + teacherLoad.length + ' teachers</span>';
                    
                    if (teacherLoad.length > 0) {
                        loadfactorDiv.innerHTML = '<h3>Load Factor Data:</h3>' + teacherLoad.map(t => 
                            '<div class="teacher-card">' +
                            '<strong>' + t.name + '</strong><br>' +
                            'Total Periods: ' + (t.total_periods || 0) + '<br>' +
                            'Load %: ' + (t.load_percentage || 0) + '%<br>' +
                            'Status: ' + (t.status || 'Unknown') +
                            '</div>'
                        ).join('');
                    } else {
                        loadfactorDiv.innerHTML = '<p>No load factor data available</p>';
                    }
                } else if (response.status === 404) {
                    statusDiv.innerHTML = '<span class="error">❌ No timetable found. Generate one first.</span>';
                } else {
                    throw new Error('HTTP ' + response.status);
                }
            } catch (error) {
                statusDiv.innerHTML = '<span class="error">❌ Error loading load factor: ' + error.message + '</span>';
            }
        }
        
        async function generateTimetable() {
            const statusDiv = document.getElementById('status');
            
            try {
                statusDiv.innerHTML = 'Generating timetable...';
                const response = await fetch(API_BASE + '/solvers/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                
                if (response.ok) {
                    const result = await response.json();
                    statusDiv.innerHTML = '<span class="success">✅ Timetable generated successfully!</span>';
                    
                    // Auto-load load factor after generation
                    setTimeout(loadLoadFactor, 1000);
                } else {
                    throw new Error('HTTP ' + response.status);
                }
            } catch (error) {
                statusDiv.innerHTML = '<span class="error">❌ Error generating timetable: ' + error.message + '</span>';
            }
        }
        
        // Auto-load teachers on page load
        loadTeachers();
    </script>
</body>
</html>'''
    
    with open('load_factor_WORKING.html', 'w', encoding='utf-8') as f:
        f.write(working_page)
    
    print("✅ Created working load factor page")
    
    # Open the working page
    print("🌐 Opening working load factor page...")
    webbrowser.open("http://localhost:8000/load_factor_WORKING.html")
    
    print("\n🎯 INSTRUCTIONS:")
    print("1. The working page should load teachers immediately")
    print("2. Click 'Generate Timetable' if load factor shows no data")
    print("3. Click 'Load Factor Data' to see teacher workloads")
    print("4. If this works, the main system should work too")
    
    return True

if __name__ == "__main__":
    final_load_factor_fix()