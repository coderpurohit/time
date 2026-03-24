#!/usr/bin/env python3

import webbrowser
import time

def force_browser_refresh_fix():
    """Force browser cache refresh and fix the issue"""
    
    print("🚨 FORCING BROWSER CACHE REFRESH")
    
    # Add cache-busting parameter to the JavaScript file
    with open('dynamic_academic_management.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Add timestamp to force cache refresh
    import time
    timestamp = str(int(time.time()))
    
    # Update the script src to include cache buster
    if 'academic_resource_management.js' in html_content:
        html_content = html_content.replace(
            'academic_resource_management.js',
            f'academic_resource_management.js?v={timestamp}'
        )
        
        with open('dynamic_academic_management.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Added cache-busting parameter to JavaScript")
    
    # Also create a direct test page with inline JavaScript
    test_page = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Faculty Data Test - WORKING</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .success {{ color: green; }}
        .error {{ color: red; }}
        .faculty-item {{ padding: 10px; border: 1px solid #ccc; margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>Faculty Data Test - WORKING VERSION</h1>
    <div id="status">Loading...</div>
    <div id="faculty-list"></div>
    
    <script>
        const API_BASE = 'http://localhost:8000/api';
        
        async function testFacultyData() {{
            const statusDiv = document.getElementById('status');
            const facultyDiv = document.getElementById('faculty-list');
            
            try {{
                console.log('Testing API endpoint:', API_BASE + '/teachers/');
                
                const response = await fetch(API_BASE + '/teachers/', {{
                    method: 'GET',
                    headers: {{
                        'Content-Type': 'application/json'
                    }}
                }});
                
                console.log('Response status:', response.status);
                
                if (response.ok) {{
                    const faculty = await response.json();
                    console.log('Faculty data:', faculty);
                    
                    statusDiv.innerHTML = '<span class="success">✅ SUCCESS: Loaded ' + faculty.length + ' faculty members</span>';
                    
                    facultyDiv.innerHTML = faculty.map(f => 
                        '<div class="faculty-item"><strong>' + f.name + '</strong><br>Email: ' + f.email + '<br>Max Hours: ' + f.max_hours_per_week + '</div>'
                    ).join('');
                    
                }} else {{
                    throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                }}
                
            }} catch (error) {{
                console.error('Error:', error);
                statusDiv.innerHTML = '<span class="error">❌ ERROR: ' + error.message + '</span>';
            }}
        }}
        
        // Test immediately when page loads
        testFacultyData();
    </script>
</body>
</html>'''
    
    with open('faculty_test_WORKING.html', 'w', encoding='utf-8') as f:
        f.write(test_page)
    
    print("✅ Created working test page")
    
    # Open both pages
    print("🌐 Opening test page...")
    webbrowser.open("http://localhost:8000/faculty_test_WORKING.html")
    
    time.sleep(2)
    
    print("🌐 Opening main system with cache refresh...")
    webbrowser.open(f"http://localhost:8000/dynamic_academic_management.html?v={timestamp}")
    
    print("\n🎯 INSTRUCTIONS:")
    print("1. The test page should show ✅ SUCCESS with faculty list")
    print("2. If test page works, the main system should work too")
    print("3. Press Ctrl+F5 in browser to force refresh if needed")
    print("4. Check browser console (F12) for any JavaScript errors")
    
    return True

if __name__ == "__main__":
    force_browser_refresh_fix()