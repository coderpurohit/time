// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Subject color mapping
const SUBJECT_COLORS = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
];

// Global state
let currentTimetable = null;
let subjectColorMap = {};

/**
 * Show status message to user
 */
function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('statusMessage');
    statusElement.textContent = message;
    statusElement.className = `status-message ${type}`;
    statusElement.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusElement.style.display = 'none';
    }, 5000);
}

/**
 * Toggle button loading state
 */
function setButtonLoading(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    const textSpan = button.querySelector('.btn-text');
    const spinner = button.querySelector('.spinner');

    if (isLoading) {
        button.disabled = true;
        if (textSpan) textSpan.style.display = 'none';
        if (spinner) spinner.style.display = 'inline-block';
    } else {
        button.disabled = false;
        if (textSpan) textSpan.style.display = 'inline';
        if (spinner) spinner.style.display = 'none';
    }
}

/**
 * Fetch latest timetable from backend
 */
async function loadTimetable() {
    setButtonLoading('loadBtn', true);
    showStatus('Fetching latest timetable...', 'info');

    try {
        const response = await fetch(`${API_BASE_URL}/api/timetables/latest`);

        if (!response.ok) {
            if (response.status === 404) {
                showStatus('No timetable found. Please generate one first.', 'error');
                return;
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentTimetable = data;

        renderTimetable(data);
        await fetchAndDisplayStats();
        showStatus('Timetable loaded successfully!', 'success');

    } catch (error) {
        console.error('Error loading timetable:', error);
        showStatus(`Error loading timetable: ${error.message}. Make sure backend is running on port 8000.`, 'error');
    } finally {
        setButtonLoading('loadBtn', false);
    }
}

/**
 * Handle File Import
 */
async function handleImport(event, dataset) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('dataset', dataset);
    formData.append('file', file);
    formData.append('force_clear_existing', 'false'); // Default to false/append/update. Replaces old 'clear_existing'

    showStatus(`Importing ${dataset}...`, 'info');

    try {
        const response = await fetch(`${API_BASE_URL}/api/import/`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || result.message || 'Import failed');
        }

        // Show detailed success message from backend
        // Backend returns: { "message": "Imported X items (updated Y)", ... }
        alert(result.message);
        showStatus(result.message, 'success');

        // Refresh stats
        await fetchAndDisplayStats();

    } catch (error) {
        console.error('Import error:', error);
        alert(`Error: ${error.message}`);
        showStatus(`Error importing ${dataset}: ${error.message}`, 'error');
    }

    // Reset file input
    event.target.value = '';
}

// Add event listeners for file inputs if they exist
document.addEventListener('DOMContentLoaded', () => {
    // ... existing initialization ...

    // Attach listeners to file inputs
    ['teachers', 'subjects', 'rooms', 'classgroups'].forEach(type => {
        const input = document.getElementById(`${type}File`);
        if (input) {
            input.addEventListener('change', (e) => handleImport(e, type));
        }
    });
});

/**
 * Generate new timetable using CSP algorithm
 */
async function generateNewTimetable() {
    setButtonLoading('generateBtn', true);
    showStatus('Generating new timetable (this may take a moment)...', 'info');

    try {
        const response = await fetch(`${API_BASE_URL}/api/solvers/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                algorithm: 'csp',
                name: 'Demo Schedule ' + new Date().toISOString().split('T')[0]
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        showStatus('Timetable generated successfully! Loading...', 'success');

        // Wait a moment then load the new timetable
        setTimeout(() => loadTimetable(), 1000);

    } catch (error) {
        console.error('Error generating timetable:', error);
        showStatus(`Error generating timetable: ${error.message}`, 'error');
    } finally {
        setButtonLoading('generateBtn', false);
    }
}

/**
 * Fetch and display statistics
 */
async function fetchAndDisplayStats() {
    try {
        // Fetch centralized stats from backend
        const response = await fetch(`${API_BASE_URL}/api/analytics/stats`);
        if (!response.ok) throw new Error("Failed to fetch stats");

        const stats = await response.json();

        // Update stats UI
        document.getElementById('teacherCount').textContent = stats.teachers || 0;
        document.getElementById('roomCount').textContent = stats.rooms || 0;
        document.getElementById('subjectCount').textContent = stats.subjects || 0;
        document.getElementById('classCount').textContent = stats.class_groups || 0;

        // Show stats section
        document.getElementById('statsSection').style.display = 'block';

        // Fetch subjects for legend (separate call needed for details)
        const subjectsRes = await fetch(`${API_BASE_URL}/api/subjects/`);
        const subjects = await subjectsRes.json();
        createLegend(subjects);

    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

/**
 * Create subject legend
 */
function createLegend(subjects) {
    const legendGrid = document.getElementById('legendGrid');
    legendGrid.innerHTML = '';

    subjects.forEach((subject, index) => {
        const color = SUBJECT_COLORS[index % SUBJECT_COLORS.length];
        subjectColorMap[subject.id] = color;

        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.innerHTML = `
            <div class="legend-color" style="background: ${color}"></div>
            <div class="legend-details">
                <div class="legend-subject">${subject.name}</div>
                <div class="legend-code">${subject.code}</div>
            </div>
        `;
        legendGrid.appendChild(legendItem);
    });

    document.getElementById('legendSection').style.display = 'block';
}

/**
 * Render timetable grid
 */
function renderTimetable(timetableData) {
    const gridElement = document.getElementById('timetableGrid');

    if (!timetableData || !timetableData.entries || timetableData.entries.length === 0) {
        gridElement.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📅</div>
                <h3>No Schedule Data</h3>
                <p>The timetable is empty or could not be loaded.</p>
            </div>
        `;
        return;
    }

    // Organize slots by day and period
    const schedule = organizeSchedule(timetableData.entries);

    // Build table HTML
    const table = document.createElement('table');
    table.className = 'timetable-table';

    // Header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headerRow.innerHTML = `
        <th>Time</th>
        <th>Monday</th>
        <th>Tuesday</th>
        <th>Wednesday</th>
        <th>Thursday</th>
        <th>Friday</th>
    `;
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body rows
    const tbody = document.createElement('tbody');
    const periods = [
        { period: 1, time: '9:00 - 10:00' },
        { period: 2, time: '10:00 - 11:00' },
        { period: 3, time: '11:00 - 12:00' },
        { period: 4, time: '12:00 - 13:00', isBreak: true },
        { period: 5, time: '13:00 - 14:00' },
        { period: 6, time: '14:00 - 15:00' },
        { period: 7, time: '15:00 - 16:00' },
    ];

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

    periods.forEach(({ period, time, isBreak }) => {
        const row = document.createElement('tr');

        // Time cell
        const timeCell = document.createElement('td');
        timeCell.className = 'time-cell';
        timeCell.textContent = time;
        row.appendChild(timeCell);

        if (isBreak) {
            const cell = document.createElement('td');
            cell.className = 'schedule-cell break';
            cell.colSpan = days.length;
            cell.innerHTML = '🍽️ LUNCH BREAK';
            row.appendChild(cell);
        } else {
            // Day cells
            days.forEach(day => {
                const cell = document.createElement('td');
                const slots = schedule[day]?.[period] || [];
                cell.appendChild(createScheduleCell(slots));
                row.appendChild(cell);
            });
        }

        tbody.appendChild(row);
    });

    table.appendChild(tbody);

    // Replace content
    gridElement.innerHTML = '';
    gridElement.appendChild(table);
}

/**
 * Organize schedule data by day and period
 */
function organizeSchedule(slots) {
    const schedule = {};

    slots.forEach(slot => {
        if (!slot.time_slot) return;

        const day = slot.time_slot.day;
        const period = slot.time_slot.period;

        if (!schedule[day]) {
            schedule[day] = {};
        }
        if (!schedule[day][period]) {
            schedule[day][period] = [];
        }

        schedule[day][period].push(slot);
    });

    return schedule;
}

/**
 * Create schedule cell content
 */
function createScheduleCell(slots) {
    const cell = document.createElement('div');

    if (slots.length === 0) {
        cell.className = 'schedule-cell empty';
        cell.textContent = 'Free';
        return cell;
    }

    // For now, just show the first slot if there are multiple
    const slot = slots[0];
    cell.className = 'schedule-cell has-class';

    // Apply subject color
    if (slot.subject && slot.subject.id && subjectColorMap[slot.subject.id]) {
        cell.style.background = subjectColorMap[slot.subject.id];
    }

    // Build content
    const classInfo = document.createElement('div');
    classInfo.className = 'class-info';

    classInfo.innerHTML = `
        <div class="subject-name">${slot.subject?.name || 'Unknown Subject'}</div>
        <div class="teacher-name">${slot.teacher?.name || 'TBA'}</div>
        <div class="room-name">${slot.room?.name || 'TBA'}</div>
        <div class="class-name">${slot.class_group?.name || 'All'}</div>
    `;

    cell.appendChild(classInfo);
    return cell;
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Demo Timetable Viewer initialized');
    console.log('Backend API:', API_BASE_URL);

    // Optionally auto-load timetable on page load
    // loadTimetable();
});
