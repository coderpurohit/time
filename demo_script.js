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
let classGroups = [];
let cachedTimeSlots = null;
let activeDivisionId = null;

// Config state
let breakRowCount = 0;

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

        await renderDivisionSwitcher();
        await renderTimetableForDivision(activeDivisionId);
        
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
 * Time Slots and Divisions
 */
async function fetchTimeSlots() {
    if (cachedTimeSlots) return cachedTimeSlots;
    try {
        const res = await fetch(`${API_BASE_URL}/api/operational/time-slots`);
        cachedTimeSlots = await res.json();
    } catch (e) { cachedTimeSlots = []; }
    return cachedTimeSlots;
}

async function loadClassGroups() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/operational/class-groups`);
        classGroups = await res.json();
        if (classGroups.length > 0 && !activeDivisionId) {
            activeDivisionId = classGroups[0].id;
        }
    } catch (err) {
        console.error('Failed to load class groups');
    }
}

async function renderDivisionSwitcher() {
    if (classGroups.length === 0) await loadClassGroups();
    
    const container = document.getElementById('divisionTabsContainer');
    if (!container) return;

    if (classGroups.length === 0) {
        container.innerHTML = '<span>No class groups found.</span>';
        return;
    }

    container.innerHTML = classGroups.map(g => `
        <button id="div-btn-${g.id}" class="btn ${g.id === activeDivisionId ? 'btn-primary' : 'btn-secondary'}"
            style="padding:0.5rem 1rem; border-radius:8px;" onclick="selectDivision(${g.id})">${g.name}</button>
    `).join('');
}

async function selectDivision(groupId) {
    activeDivisionId = groupId;
    
    // Update active button styles
    classGroups.forEach(g => {
        const btn = document.getElementById(`div-btn-${g.id}`);
        if (btn) btn.className = `btn ${g.id === groupId ? 'btn-primary' : 'btn-secondary'}`;
    });

    if (currentTimetable) {
        await renderTimetableForDivision(groupId);
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
 * Render timetable grid for a specific division
 */
async function renderTimetableForDivision(classGroupId) {
    const gridElement = document.getElementById('timetableGrid');

    if (!currentTimetable || !currentTimetable.entries || currentTimetable.entries.length === 0) {
        gridElement.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📅</div>
                <h3>No Schedule Data</h3>
                <p>The timetable is empty or could not be loaded.</p>
            </div>
        `;
        return;
    }

    // Filter entries for the selected class group
    const entries = currentTimetable.entries.filter(e => e.class_group_id == classGroupId);
    const groupName = (classGroups.find(g => g.id == classGroupId) || {}).name || classGroupId;

    if (entries.length === 0) {
        gridElement.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📅</div>
                <h3>No Schedule Data for ${groupName}</h3>
                <p>There are no classes scheduled for this division.</p>
            </div>
        `;
        return;
    }

    const slots = await fetchTimeSlots();
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        .filter(d => slots.some(s => s.day === d));
    if (!days.length) days.push('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday');

    // Get ordered time slots for a single day (e.g., Monday) to build headers
    const daySlots = slots.filter(s => s.day === days[0])
        .sort((a,b) => a.start_time.localeCompare(b.start_time) || a.period - b.period);

    // Build schedule dictionary
    const schedule = {};
    days.forEach(day => { schedule[day] = {}; });
    entries.forEach(e => {
        if (e && e.time_slot) {
            const d = e.time_slot.day, p = e.time_slot.period;
            if (!schedule[d]) schedule[d] = {};
            schedule[d][p] = e;
        }
    });

    // Build table HTML
    const table = document.createElement('table');
    table.className = 'timetable-table';

    // Header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    let headerHTML = `<th>Time / Day</th>`;
    days.forEach(day => {
        headerHTML += `<th>${day}</th>`;
    });
    headerRow.innerHTML = headerHTML;
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body rows
    const tbody = document.createElement('tbody');

    daySlots.forEach(s => {
        const row = document.createElement('tr');
        
        // Time cell
        const timeCell = document.createElement('td');
        timeCell.className = 'time-cell';
        timeCell.innerHTML = `<strong>${s.start_time} - ${s.end_time}</strong>`;
        row.appendChild(timeCell);

        if (s.is_break) {
            // Break row spans across all days
            const cell = document.createElement('td');
            cell.className = 'schedule-cell break';
            cell.colSpan = days.length;
            cell.innerHTML = '🍽️ BREAK';
            cell.style.background = '#fef3c7';
            cell.style.color = '#92400e';
            cell.style.fontWeight = 'bold';
            cell.style.textAlign = 'center';
            row.appendChild(cell);
        } else {
            // Normal class row
            days.forEach(day => {
                const cell = document.createElement('td');
                const entry = schedule[day] ? schedule[day][s.period] : null;
                
                if (entry) {
                    cell.appendChild(createScheduleCell([entry]));
                } else {
                    const empty = document.createElement('div');
                    empty.className = 'schedule-cell empty';
                    empty.textContent = '—';
                    cell.appendChild(empty);
                }
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
 * Schedule Configuration Modal Logic
 */
function openConfigModal() {
    document.getElementById('configModal').style.display = 'flex';
    loadScheduleConfig();
}

function closeConfigModal() {
    document.getElementById('configModal').style.display = 'none';
}

function addBreakRow(position = '', duration = 15) {
    breakRowCount++;
    const id = breakRowCount;
    const container = document.getElementById('breaksContainer');
    container.insertAdjacentHTML('beforeend',
        `<div id="break-row-${id}" style="display:flex;gap:0.75rem;align-items:center;margin-bottom:0.5rem;">
            <label style="font-size:0.85rem;min-width:130px;">After Period #</label>
            <input type="number" min="1" max="20" value="${position}" style="width:80px;min-width:unset;" class="break-position" data-id="${id}">
            <label style="font-size:0.85rem;min-width:80px;">Duration (min)</label>
            <input type="number" min="5" max="120" value="${duration}" style="width:80px;min-width:unset;" class="break-duration" data-id="${id}">
            <button class="btn btn-secondary" style="padding:0.3rem 0.75rem;font-size:0.8rem;"
                onclick="document.getElementById('break-row-${id}').remove()">✕</button>
        </div>`
    );
}

async function loadScheduleConfig() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/operational/schedule-config`);
        const cfg = await res.json();
        document.getElementById('cfg_institution').value = cfg.institution || '';
        document.getElementById('cfg_start').value = cfg.day_start_time || '09:00';
        document.getElementById('cfg_periods').value = cfg.number_of_periods || 7;
        document.getElementById('cfg_period_dur').value = cfg.period_duration_minutes || 60;
        document.getElementById('cfg_lunch_start').value = cfg.lunch_break_start || '12:00';
        document.getElementById('cfg_lunch_end').value = cfg.lunch_break_end || '13:00';
        
        const savedDays = cfg.schedule_days || ['Monday','Tuesday','Wednesday','Thursday','Friday'];
        document.querySelectorAll('.cfg-day').forEach(cb => { 
            cb.checked = savedDays.includes(cb.value); 
        });
        
        document.getElementById('breaksContainer').innerHTML = '';
        breakRowCount = 0;
        (cfg.breaks || []).forEach(b => addBreakRow(b.position, b.duration));
        
        const statusEl = document.getElementById('configStatus');
        statusEl.innerHTML = '<div class="alert alert-info">Config loaded from server.</div>';
        setTimeout(() => { statusEl.innerHTML = ''; }, 2500);
    } catch (e) {
        document.getElementById('configStatus').innerHTML = '<div class="alert alert-error">Failed to load config: ' + e.message + '</div>';
    }
}

async function applyScheduleConfig() {
    const statusEl = document.getElementById('configStatus');
    statusEl.innerHTML = '<div class="loading"><div class="spinner"></div><p>Applying config and regenerating timetable...</p></div>';
    
    const days = [...document.querySelectorAll('.cfg-day:checked')].map(cb => cb.value);
    if (!days.length) { 
        statusEl.innerHTML = '<div class="alert alert-error">Select at least one working day.</div>'; 
        return; 
    }
    
    const breaks = [];
    document.querySelectorAll('.break-position').forEach(el => {
        const id = el.dataset.id;
        const pos = parseInt(el.value);
        const durEl = document.querySelector(`.break-duration[data-id="${id}"]`);
        const dur = durEl ? parseInt(durEl.value) : 0;
        if (pos > 0 && dur > 0) breaks.push({ position: pos, duration: dur });
    });
    
    const periods = parseInt(document.getElementById('cfg_periods').value);
    const period_dur = parseInt(document.getElementById('cfg_period_dur').value);
    
    const payload = {
        day_start_time: document.getElementById('cfg_start').value,
        number_of_periods: periods, 
        period_duration_minutes: period_dur,
        lunch_break_start: document.getElementById('cfg_lunch_start').value,
        lunch_break_end: document.getElementById('cfg_lunch_end').value,
        schedule_days: days, 
        institution: document.getElementById('cfg_institution').value,
        breaks: breaks, 
        working_minutes_per_day: periods * period_dur
    };
    
    try {
        const res = await fetch(`${API_BASE_URL}/api/operational/apply-config`, {
            method: 'POST', 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (res.ok) {
            statusEl.innerHTML = `<div class="alert alert-success">✅ Config applied successfully!</div>`;
            cachedTimeSlots = null; // Clear cache to fetch new slots
            setTimeout(() => {
                closeConfigModal();
                loadTimetable(); // Reload data
            }, 1500);
        } else {
            statusEl.innerHTML = `<div class="alert alert-error">Error: ${data.detail || JSON.stringify(data)}</div>`;
        }
    } catch (e) { 
        statusEl.innerHTML = `<div class="alert alert-error">Request failed: ${e.message}</div>`; 
    }
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Demo Timetable Viewer initialized');
    console.log('Backend API:', API_BASE_URL);

    // Load necessary data sequentially
    await loadClassGroups();
    await renderDivisionSwitcher();
    
    // Auto-load timetable on page load
    loadTimetable();
});
