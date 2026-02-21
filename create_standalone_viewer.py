import json

# Load the dataset
with open('timetable_dataset.json', 'r') as f:
    data = json.load(f)

# Create embedded HTML
html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>College Timetable - Clean View</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            padding: 2rem;
        }

        .container {
           max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 3px solid #9da3ab;
        }

        .class-selector {
            text-align: center;
            margin-bottom: 2rem;
        }

        .class-selector select {
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border: 2px solid #9da3ab;
            border-radius: 4px;
            background: white;
            cursor: pointer;
        }

        .timetable-header {
            background: #9da3ab;
            border: 2px solid #000;
            padding: 1rem;
            margin-bottom: 1.5rem;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
        }

        .timetable-header strong {
            font-weight: 700;
            color: #000;
        }

        .timetable-wrapper {
            overflow-x: auto;
            border: 2px solid #000;
        }

        .timetable-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        .timetable-table th {
            background: #9da3ab;
            color: #000;
            padding: 0.75rem;
            text-align: center;
            font-weight: 700;
            border: 1px solid #000;
            font-size: 0.85rem;
        }

        .timetable-table td {
            padding: 0.6rem;
            border: 1px solid #000;
            vertical-align: top;
            font-size: 0.75rem;
            min-height: 70px;
        }

        .day-cell {
            background: #d3d3d3;
            font-weight: 700;
            text-align: center;
            vertical-align: middle;
            color: #000;
            min-width: 100px;
        }

        .class-cell {
            background: #f9f9f9;
            min-width: 130px;
        }

        .subject-code {
            font-weight: 700;
            color: #000;
            margin-bottom: 0.2rem;
            font-size: 0.8rem;
        }

        .teacher-name, .room-name {
            color: #333;
            font-size: 0.7rem;
            margin: 0.1rem 0;
        }

        .lab-badge {
            display: inline-block;
            background: #4a5568;
            color: white;
            padding: 0.1rem 0.3rem;
            border-radius: 3px;
            font-size: 0.6rem;
            margin-top: 0.2rem;
        }

        .empty-cell {
            color: #999;
            text-align: center;
            font-style: italic;
        }

        @media print { 
            .class-selector { display: none; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 College Timetable - Academic Year 2025-26</h1>
        
        <div class="class-selector">
            <label for="classSelect"><strong>Select Class:</strong></label>
            <select id="classSelect" onchange="displayTimetable()"></select>
        </div>

        <div id="timetableContainer"></div>
    </div>

    <script>
        const TIMETABLE_DATA = ''' + json.dumps(data) + ''';

        function loadData() {
            const classSelect = document.getElementById('classSelect');
            TIMETABLE_DATA.class_groups.forEach(group => {
                const option = document.createElement('option');
                option.value = group.name;
                option.textContent = `${group.name} (${group.student_count} students)`;
                classSelect.appendChild(option);
            });
            
            // Auto-select first class
           if (TIMETABLE_DATA.class_groups.length > 0) {
                classSelect.value = TIMETABLE_DATA.class_groups[0].name;
                displayTimetable();
            }
        }

        function displayTimetable() {
            const className = document.getElementById('classSelect').value;
            if (!className) return;

            const container = document.getElementById('timetableContainer');
            const entries = TIMETABLE_DATA.timetable_entries.filter(e => e.class_group === className);
            
            if (entries.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #666;">No timetable data.</p>';
                return;
            }

            const today = new Date().toLocaleDateString('en-GB');
            const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
            const periods = [1, 2, 3, 4, 5, 6];
            const schedule = {};
            
            days.forEach(day => {
                schedule[day] = {};
                periods.forEach(period => schedule[day][period] = null);
            });

            entries.forEach(entry => {
                schedule[entry.day][entry.period] = entry;
            });

            let html = `
                <div class="timetable-header">
                    <div><strong>Class:</strong> ${className}</div>
                    <div><strong>Division:</strong> C</div>
                    <div><strong>w.e.f:</strong> ${today}</div>
                </div>
                <div class="timetable-wrapper">
                    <table class="timetable-table">
                        <thead><tr><th>Day / Time</th>`;

            periods.forEach(period => {
                const sample = entries.find(e => e.period === period);
                html += sample ? 
                    `<th>${sample.start_time}<br>to<br>${sample.end_time}</th>` : 
                    `<th>Period ${period}</th>`;
            });

            html += '</tr></thead><tbody>';

            days.forEach(day => {
                html += `<tr><td class="day-cell"><strong>${day}</strong></td>`;
                periods.forEach(period => {
                    const entry = schedule[day][period];
                    if (entry) {
                        html += `
                            <td class="class-cell">
                                <div class="subject-code">${entry.subject_code}</div>
                                <div class="teacher-name">${entry.teacher_name}</div>
                                <div class="room-name">${entry.room_name}</div>
                                ${entry.is_lab ? '<span class="lab-badge">LAB</span>' : ''}
                            </td>`;
                    } else {
                        html += '<td class="class-cell"><div class="empty-cell">—</div></td>';
                    }
                });
                html += '</tr>';
            });

            html += '</tbody></table></div>';
            container.innerHTML = html;
        }

        loadData();
    </script>
</body>
</html>'''

with open('timetable_clean.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("✅ Created timetable_clean.html with embedded data!")
