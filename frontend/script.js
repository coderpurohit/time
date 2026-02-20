// API Base URL
const API_BASE = 'http://localhost:8000';

// Global variable to store current timetable for export
let currentTimetableData = null;

// Check backend status on load
checkBackendStatus();
loadStats();

// Check if backend is running
async function checkBackendStatus() {
    const statusIndicator = document.getElementById('backendStatus');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');

    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        if (data.status === 'healthy') {
            statusDot.style.background = '#48bb78';
            statusText.textContent = 'Backend Online ✓';
            statusText.style.color = '#22543d';
        } else {
            throw new Error('Backend unhealthy');
        }
    } catch (error) {
        statusDot.classList.add('error');
        statusDot.style.background = '#f56565';
        statusText.textContent = 'Backend Offline ✗';
        statusText.style.color = '#742a2a';
        console.error('Backend status check failed:', error);
    }
}

// Load database statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        document.getElementById('teacherCount').textContent = data.teachers || '0';
        document.getElementById('timetableCount').textContent = data.timetables || '0';

        // Fetch additional stats
        const [teachers, subjects, rooms] = await Promise.all([
            fetch(`${API_BASE}/api/teachers`).then(r => r.json()),
            fetch(`${API_BASE}/api/subjects`).then(r => r.json()),
            fetch(`${API_BASE}/api/rooms`).then(r => r.json())
        ]);

        document.getElementById('teacherCount').textContent = teachers.length || '0';
        document.getElementById('subjectCount').textContent = subjects.length || '0';
        document.getElementById('roomCount').textContent = rooms.length || '0';
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// ========== CSV IMPORT FUNCTIONALITY ==========

async function handleFileImport(input, type) {
    const file = input.files[0];
    if (!file) return;

    const statusDiv = document.getElementById('importStatus');
    statusDiv.innerHTML = '<div class="alert alert-info">📤 Uploading and processing...</div>';

    try {
        const text = await file.text();
        const rows = parseCSV(text);

        if (rows.length === 0) {
            throw new Error('CSV file is empty');
        }

        // Process based on type
        let result;
        switch (type) {
            case 'teachers':
                result = await importTeachers(rows);
                break;
            case 'subjects':
                result = await importSubjects(rows);
                break;
            case 'rooms':
                result = await importRooms(rows);
                break;
            case 'classgroups':
                result = await importClassGroups(rows);
                break;
            default:
                throw new Error('Unknown import type');
        }

        statusDiv.innerHTML = `<div class="alert alert-success">✅ Successfully imported ${result.count} ${type}!</div>`;
        loadStats(); // Reload stats

        // Clear after 5 seconds
        setTimeout(() => statusDiv.innerHTML = '', 5000);
    } catch (error) {
        statusDiv.innerHTML = `<div class="alert alert-error">❌ Import failed: ${error.message}</div>`;
        console.error('Import error:', error);
    }
}

// Simple CSV parser
function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const rows = [];

    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index] ? values[index].trim() : '';
        });
        rows.push(row);
    }

    return rows;
}

// Import teachers
async function importTeachers(rows) {
    let count = 0;
    for (const row of rows) {
        try {
            await fetch(`${API_BASE}/api/teachers`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: row.name,
                    email: row.email,
                    max_hours_per_week: parseInt(row.max_hours_per_week) || 12
                })
            });
            count++;
        } catch (error) {
            console.error(`Failed to import teacher ${row.name}:`, error);
        }
    }
    return { count };
}

// Import subjects
async function importSubjects(rows) {
    // First get all teachers to map emails to IDs
    const teachersResp = await fetch(`${API_BASE}/api/teachers`);
    const teachers = await teachersResp.json();
    const teacherMap = {};
    teachers.forEach(t => teacherMap[t.email] = t.id);

    let count = 0;
    for (const row of rows) {
        try {
            const teacherId = teacherMap[row.teacher_email];
            await fetch(`${API_BASE}/api/subjects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: row.name,
                    code: row.code,
                    is_lab: row.is_lab === 'true' || row.is_lab === 'True',
                    credits: parseInt(row.credits),
                    required_room_type: row.required_room_type || 'LectureHall',
                    duration_slots: parseInt(row.duration_slots) || 1,
                    teacher_id: teacherId
                })
            });
            count++;
        } catch (error) {
            console.error(`Failed to import subject ${row.name}:`, error);
        }
    }
    return { count };
}

// Import rooms
async function importRooms(rows) {
    let count = 0;
    for (const row of rows) {
        try {
            const resources = row.resources ? row.resources.split(';').map(r => r.trim()) : [];
            await fetch(`${API_BASE}/api/rooms`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: row.name,
                    capacity: parseInt(row.capacity),
                    type: row.type || 'LectureHall',
                    resources: resources
                })
            });
            count++;
        } catch (error) {
            console.error(`Failed to import room ${row.name}:`, error);
        }
    }
    return { count };
}

// Import class groups
async function importClassGroups(rows) {
    let count = 0;
    for (const row of rows) {
        try {
            await fetch(`${API_BASE}/api/operational/class-groups`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: row.name,
                    student_count: parseInt(row.student_count)
                })
            });
            count++;
        } catch (error) {
            console.error(`Failed to import class group ${row.name}:`, error);
        }
    }
    return { count };
}

// ========== TIMETABLE GENERATION ==========

async function generateTimetable() {
    const generateBtn = document.getElementById('generateBtn');
    const btnText = generateBtn.querySelector('.btn-text');
    const spinner = generateBtn.querySelector('.spinner');
    const resultsCard = document.getElementById('resultsCard');
    const resultsContent = document.getElementById('resultsContent');
    const resultStatus = document.getElementById('resultStatus');

    const timetableName = document.getElementById('timetableName').value;
    const algorithm = document.getElementById('algorithm').value;

    // Disable button and show spinner
    generateBtn.disabled = true;
    btnText.textContent = 'Generating...';
    spinner.style.display = 'inline-block';

    // Show results card
    resultsCard.style.display = 'block';
    resultStatus.className = 'result-status processing';
    resultStatus.textContent = '⏳ Processing...';

    try {
        const response = await fetch(`${API_BASE}/api/solvers/generate?method=${algorithm}&name=${encodeURIComponent(timetableName)}`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Update status
        resultStatus.className = 'result-status success';
        resultStatus.textContent = '✓ Generation Started!';

        // Display results
        resultsContent.innerHTML = `
            <div class="alert alert-success">
                <span>Timetable generation initiated successfully!</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Timetable ID</span>
                <span class="result-value">#${data.id}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Name</span>
                <span class="result-value">${data.name}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Algorithm</span>
                <span class="result-value">${data.algorithm.toUpperCase()}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Status</span>
                <span class="result-value">${data.status}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Created At</span>
                <span class="result-value">${new Date(data.created_at).toLocaleString()}</span>
            </div>

            <div class="alert alert-info" style="margin-top: 1rem;">
                <span>💡 Tip: The generation is running in the background. Click "Fetch Latest Timetable" below to see the result once it's complete.</span>
            </div>

            <h4 style="margin-top: 1.5rem; margin-bottom: 0.75rem; color: #2d3748;">Raw Response:</h4>
            <div class="result-json">${JSON.stringify(data, null, 2)}</div>
        `;

        // Poll for completion
        pollTimetableStatus(data.id);

        // Reload stats
        loadStats();

    } catch (error) {
        resultStatus.className = 'result-status error';
        resultStatus.textContent = '✗ Generation Failed';

        resultsContent.innerHTML = `
            <div class="alert alert-error">
                <span>❌ Error: ${error.message}</span>
            </div>
            <p style="color: #718096; margin-top: 1rem;">Make sure your backend is running on ${API_BASE}</p>
        `;
        console.error('Generation failed:', error);
    } finally {
        // Re-enable button
        generateBtn.disabled = false;
        btnText.textContent = 'Generate Timetable';
        spinner.style.display = 'none';
    }
}

// Poll for timetable completion status
async function pollTimetableStatus(timetableId, attempts = 0) {
    if (attempts >= 20) {
        console.log('Polling timeout reached');
        return;
    }

    setTimeout(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/timetables/${timetableId}`);
            const data = await response.json();

            const resultStatus = document.getElementById('resultStatus');

            if (data.status === 'completed') {
                resultStatus.className = 'result-status success';
                resultStatus.textContent = '✓ Generation Complete!';

                // Show completion alert
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success';
                alertDiv.innerHTML = `
                    <span>🎉 Timetable generation completed! Click "Fetch Latest Timetable" to view it.</span>
                `;
                document.getElementById('resultsContent').insertBefore(
                    alertDiv,
                    document.getElementById('resultsContent').firstChild
                );
            } else if (data.status === 'failed') {
                resultStatus.className = 'result-status error';
                resultStatus.textContent = '✗ Generation Failed';
            } else {
                // Continue polling
                pollTimetableStatus(timetableId, attempts + 1);
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 2000); // Poll every 2 seconds
}

// ========== FETCH AND DISPLAY TIMETABLE ==========

async function fetchLatestTimetable() {
    const content = document.getElementById('latestTimetableContent');
    const exportButtons = document.getElementById('exportButtons');
    content.innerHTML = '<div class="alert alert-info">⏳ Fetching latest timetable...</div>';
    exportButtons.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/api/timetables/latest`);

        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('No timetables found. Generate one first!');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentTimetableData = data; // Store for export

        // Show export buttons
        exportButtons.style.display = 'flex';

        // Display timetable info
        let html = `
            <div class="alert alert-success">
                <span>✓ Latest timetable loaded successfully!</span>
            </div>

            <div class="result-item">
                <span class="result-label">Timetable ID</span>
                <span class="result-value">#${data.id}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Name</span>
                <span class="result-value">${data.name}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Algorithm</span>
                <span class="result-value">${data.algorithm.toUpperCase()}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Status</span>
                <span class="result-value">${data.status}</span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Total Classes</span>
                <span class="result-value">${data.entries.length}</span>
            </div>
        `;

        // Display timetable calendar
        if (data.entries && data.entries.length > 0) {
            html += displayTimetableCalendar(data.entries);
        } else {
            html += '<div class="alert alert-info">No classes scheduled yet.</div>';
        }

        content.innerHTML = html;

    } catch (error) {
        content.innerHTML = `
            <div class="alert alert-error">
                <span>❌ Error: ${error.message}</span>
            </div>
        `;
        console.error('Fetch failed:', error);
    }
}

// Display timetable in academic calendar format
function displayTimetableCalendar(entries) {
    // Group entries by class group first
    const classGroups = {};
    entries.forEach(entry => {
        const groupName = entry.class_group.name;
        if (!classGroups[groupName]) {
            classGroups[groupName] = [];
        }
        classGroups[groupName].push(entry);
    });

    let html = '';

    // Create a table for each class group
    Object.keys(classGroups).sort().forEach(groupName => {
        const groupEntries = classGroups[groupName];

        // Get a sample teacher name (you could aggregate or pick most common)
        const sampleTeacher = groupEntries.length > 0 ? groupEntries[0].teacher.name : 'TBA';
        const currentDate = new Date().toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).replace(/\//g, '/');

        // Academic Header
        html += `
            <div class="timetable-header">
                <div class="timetable-header-row">
                    <div><strong>Class:</strong> ${groupName}</div>
                    <div><strong>Div:</strong> C</div>
                    <div><strong>w.e.f - ${currentDate}</strong></div>
                </div>
                <div class="timetable-header-row">
                    <div><strong>Class Room No:</strong></div>
                    <div colspan="2"><strong>Name of the Class Teacher:</strong> ${sampleTeacher}</div>
                </div>
            </div>
        `;

        html += '<div class="timetable-calendar"><table class="timetable-table">';

        // Get all unique time periods and sort them
        const periods = Array.from(new Set(entries.map(e => e.time_slot.period))).sort((a, b) => a - b);
        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

        // Build a schedule grid: days x periods
        const schedule = {};
        days.forEach(day => {
            schedule[day] = {};
            periods.forEach(period => {
                schedule[day][period] = [];
            });
        });

        // Populate schedule for this class group
        groupEntries.forEach(entry => {
            const day = entry.time_slot.day;
            const period = entry.time_slot.period;
            if (schedule[day] && schedule[day][period] !== undefined) {
                schedule[day][period].push(entry);
            }
        });

        // Header row with time slots as columns
        html += '<thead><tr><th class="time-header">Day / Time</th>';
        periods.forEach(period => {
            const sampleEntry = entries.find(e => e.time_slot.period === period);
            const timeStr = sampleEntry ?
                `${formatTime(sampleEntry.time_slot.start_time)} to ${formatTime(sampleEntry.time_slot.end_time)}` :
                `Period ${period}`;
            html += `<th class="time-header">${timeStr}</th>`;
        });
        html += '</tr></thead>';

        // Data rows - each day is a row
        html += '<tbody>';
        days.forEach(day => {
            html += '<tr>';
            html += `<td class="day-cell"><strong>${day}</strong></td>`;

            periods.forEach(period => {
                const classes = schedule[day][period];
                html += '<td class="class-cell">';

                if (classes && classes.length > 0) {
                    // Check if it's a break period
                    if (classes[0].subject.name.toLowerCase().includes('break')) {
                        html += `<div class="break-cell">BREAK</div>`;
                    } else {
                        // Display multiple classes if exist
                        html += '<div class="multi-class">';
                        classes.forEach(cls => {
                            html += `
                                <div class="class-entry">
                                    <div class="subject-name">${cls.subject.code || cls.subject.name}</div>
                                    <div class="teacher-name">${cls.teacher.name}</div>
                                    <div class="room-name">${cls.room.name}</div>
                                </div>
                            `;
                        });
                        html += '</div>';
                    }
                } else {
                    html += '<div class="empty-cell">—</div>';
                }

                html += '</td>';
            });

            html += '</tr>';
        });
        html += '</tbody>';

        html += '</table></div>';
    });

    return html;
}

// Helper function to format time
function formatTime(timeStr) {
    if (!timeStr) return '';
    // Convert 24h to 12h format if needed
    const parts = timeStr.split(':');
    if (parts.length >= 2) {
        let hour = parseInt(parts[0]);
        const minute = parts[1];
        const ampm = hour >= 12 ? 'PM' : 'AM';
        hour = hour % 12 || 12;
        return `${hour}:${minute} ${ampm}`;
    }
    return timeStr;
}

// ========== EXPORT FUNCTIONALITY ==========

function exportToCSV() {
    if (!currentTimetableData || !currentTimetableData.entries) {
        alert('No timetable data to export!');
        return;
    }

    const entries = currentTimetableData.entries;

    // CSV header
    let csv = 'Day,Time,Period,Subject,Subject Code,Teacher,Room,Class Group,Is Lab\n';

    // CSV rows
    entries.forEach(entry => {
        csv += `${entry.time_slot.day},`;
        csv += `${entry.time_slot.start_time}-${entry.time_slot.end_time},`;
        csv += `${entry.time_slot.period},`;
        csv += `"${entry.subject.name}",`;
        csv += `${entry.subject.code},`;
        csv += `"${entry.teacher.name}",`;
        csv += `${entry.room.name},`;
        csv += `${entry.class_group.name},`;
        csv += `${entry.subject.is_lab}\n`;
    });

    // Download
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `timetable_${currentTimetableData.name.replace(/\s+/g, '_')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function exportToPDF() {
    if (!currentTimetableData || !currentTimetableData.entries) {
        alert('No timetable data to export!');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('l', 'mm', 'a4'); // Landscape orientation

    // Title
    doc.setFontSize(18);
    doc.text(`Timetable: ${currentTimetableData.name}`, 14, 15);

    doc.setFontSize(10);
    doc.text(`Generated using ${currentTimetableData.algorithm.toUpperCase()} algorithm`, 14, 22);

    // Prepare table data
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const entries = currentTimetableData.entries;
    const periods = Array.from(new Set(entries.map(e => e.time_slot.period))).sort((a, b) => a - b);

    const schedule = {};
    days.forEach(day => {
        schedule[day] = {};
        periods.forEach(period => schedule[day][period] = []);
    });

    entries.forEach(entry => {
        const day = entry.time_slot.day;
        const period = entry.time_slot.period;
        if (schedule[day] && schedule[day][period] !== undefined) {
            schedule[day][period].push(entry);
        }
    });

    // Build table rows
    const tableData = [];
    periods.forEach(period => {
        const sampleEntry = entries.find(e => e.time_slot.period === period);
        const timeStr = sampleEntry ? `${sampleEntry.time_slot.start_time}-${sampleEntry.time_slot.end_time}` : `P${period}`;

        const row = [timeStr];
        days.forEach(day => {
            const classes = schedule[day][period] || [];
            if (classes.length > 0) {
                const classInfo = classes.map(cls =>
                    `${cls.subject.name}\n${cls.teacher.name}\n${cls.room.name}\n${cls.class_group.name}`
                ).join('\n---\n');
                row.push(classInfo);
            } else {
                row.push('—');
            }
        });
        tableData.push(row);
    });

    // Generate table
    doc.autoTable({
        head: [['Time', ...days]],
        body: tableData,
        startY: 28,
        styles: { fontSize: 8, cellPadding: 3 },
        headStyles: { fillColor: [102, 126, 234], textColor: 255 },
        columnStyles: {
            0: { cellWidth: 25, fontStyle: 'bold' }
        },
        didParseCell: function (data) {
            if (data.row.section === 'body' && data.column.index > 0) {
                if (data.cell.text[0] === '—') {
                    data.cell.styles.fillColor = [245, 245, 245];
                    data.cell.styles.textColor = [180, 180, 180];
                }
            }
        }
    });

    // Save PDF
    doc.save(`timetable_${currentTimetableData.name.replace(/\s+/g, '_')}.pdf`);
}
