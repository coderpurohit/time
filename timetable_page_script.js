// Timetable Page JavaScript - Backend Integration

// Use the same origin the page was served from so API calls are same-origin
// (prevents CORS issues when the page is served from 127.0.0.1 but JS used "localhost").
const API_BASE_URL = (typeof window !== 'undefined' && window.location && window.location.origin) ? window.location.origin : 'http://localhost:8000';

// Subject color mapping
const SUBJECT_COLORS = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
];

// Global state
let currentTimetable = null;
let subjectColorMap = {};
let cachedTimeSlots = null;
let cachedScheduleConfig = null;

/**
 * Show status message to user
 */
function showStatus(message, type = 'info') {
    const statusElement = document.getElementById('statusMessage');
    statusElement.textContent = message;
    statusElement.className = `status-message ${type}`;
    statusElement.style.display = 'flex';

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
    if (!button) {
        console.warn(`Button with id '${buttonId}' not found`);
        return;
    }
    
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
 * Fetch and update ALL schedule settings UI from backend config
 */
async function loadScheduleConfigUI() {
    try {
        const resp = await fetch(`${API_BASE_URL}/api/operational/schedule-config`).catch(() => null);
        if (!resp || !resp.ok) return;

        const cfg = await resp.json();

        // Update teaching hours (backend may provide working_minutes_per_day)
        const teachingHrsInput = document.getElementById('teachingHours');
        if (teachingHrsInput) {
            if (cfg.working_minutes_per_day) teachingHrsInput.value = Math.round(cfg.working_minutes_per_day / 60);
            else if (cfg.day_start_time && cfg.day_end_time) {
                const [sh, sm] = cfg.day_start_time.split(':').map(Number);
                const [eh, em] = cfg.day_end_time.split(':').map(Number);
                let start = sh * 60 + sm; let end = eh * 60 + em;
                if (end < start) end += 24 * 60;
                teachingHrsInput.value = Math.round((end - start) / 60);
            }
        }

        // Update lunch break times
        const lunchStartInput = document.getElementById('lunchStart');
        const lunchEndInput = document.getElementById('lunchEnd');
        if (lunchStartInput) lunchStartInput.value = cfg.lunch_break_start || cfg.lunchBreakStart || '';
        if (lunchEndInput) lunchEndInput.value = cfg.lunch_break_end || cfg.lunchBreakEnd || '';

        // Update schedule day checkboxes
        const dayCheckboxes = document.querySelectorAll('.scheduleDay');
        dayCheckboxes.forEach(cb => {
            cb.checked = (cfg.schedule_days || []).includes(cb.value);
        });

        // Update period inputs if provided
        const periodCountInput = document.getElementById('periodCount');
        const periodDurationInput = document.getElementById('periodDuration');
        const periodStartHourInput = document.getElementById('periodStartHour');
        if (periodCountInput && cfg.number_of_periods) periodCountInput.value = cfg.number_of_periods;
        if (periodDurationInput && cfg.period_duration_minutes) periodDurationInput.value = cfg.period_duration_minutes;
        if (periodStartHourInput && cfg.day_start_time) periodStartHourInput.value = parseInt((cfg.day_start_time || '09:00').split(':')[0], 10);

        // Update info card display
        const infoTeachingHours = document.getElementById('infoTeachingHours');
        if (infoTeachingHours) infoTeachingHours.textContent = `${teachingHrsInput ? teachingHrsInput.value : '-'} hours/day`;

        const infoLunchBreak = document.getElementById('infoLunchBreak');
        if (infoLunchBreak) infoLunchBreak.textContent = `${lunchStartInput ? lunchStartInput.value : ''} - ${lunchEndInput ? lunchEndInput.value : ''}`;

        const infoScheduleDays = document.getElementById('infoScheduleDays');
        if (infoScheduleDays) infoScheduleDays.textContent = (cfg.schedule_days || []).join(', ');

        console.log('Loaded schedule config:', cfg);
    } catch (err) {
        console.log('Could not load schedule config:', err);
    }
}

/**
 * Apply all schedule configuration (teaching hours, lunch, days, periods)
 */
async function applyAllSettings() {
    try {
        const teachingHours = parseInt(document.getElementById('teachingHours')?.value || '6', 10);
        const lunchStart = document.getElementById('lunchStart')?.value || '12:00';
        const lunchEnd = document.getElementById('lunchEnd')?.value || '13:00';
        const periodCount = parseInt(document.getElementById('periodCount')?.value || '7', 10);
        const periodDuration = parseInt(document.getElementById('periodDuration')?.value || '60', 10);
        const periodStartHour = parseInt(document.getElementById('periodStartHour')?.value || '9', 10);

        // Collect selected schedule days
        const scheduleDays = [];
        document.querySelectorAll('.scheduleDay:checked').forEach(cb => {
            scheduleDays.push(cb.value);
        });

        if (!teachingHours || teachingHours < 1) {
            showStatus('Invalid teaching hours', 'error');
            return;
        }
        if (!periodCount || periodCount < 1) {
            showStatus('Invalid period count', 'error');
            return;
        }
        if (!periodDuration || periodDuration < 10) {
            showStatus('Invalid period duration', 'error');
            return;
        }
        if (scheduleDays.length === 0) {
            showStatus('Select at least one schedule day', 'error');
            return;
        }

        setButtonLoading('applySettingsBtn', true);
        showStatus('Applying all settings...', 'info');

        const cfgBody = {
            day_start_time: `${String(periodStartHour).padStart(2, '0')}:00`,
            day_end_time: null,
            working_minutes_per_day: teachingHours ? teachingHours * 60 : null,
            number_of_periods: periodCount,
            period_duration_minutes: periodDuration,
            breaks: [],
            lunch_break_start: lunchStart,
            lunch_break_end: lunchEnd,
            schedule_days: scheduleDays
        };

        // Call apply-config endpoint which validates, recreates slots, clears old timetable and regenerates
        const cfgResp = await fetch(`${API_BASE_URL}/api/operational/apply-config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cfgBody)
        });

        if (!cfgResp.ok) {
            const err = await cfgResp.json().catch(() => ({}));
            throw new Error(err.detail || `Config apply failed: ${cfgResp.status}`);
        }

        const result = await cfgResp.json();
        console.log('Apply-config result:', result);

        // Clear cache and refresh timetable automatically
        clearCache();
        showStatus('Configuration applied successfully! Loading timetable...', 'success');
        
        // Wait a moment for the backend to finish, then load
        setTimeout(async () => {
            await loadTimetable();
        }, 1000);

    } catch (err) {
        console.error('Apply settings error:', err);
        showStatus(`Failed: ${err.message}`, 'error');
    } finally {
        setButtonLoading('applySettingsBtn', false);
    }
}

/**
 * Fetch and update period settings UI from current database time slots
 */
async function updatePeriodSettingsUI() {
    try {
        const resp = await fetch(`${API_BASE_URL}/api/operational/time-slots`).catch(() => null);
        if (!resp || !resp.ok) return; // Endpoint may not exist, skip silently

        const slots = await resp.json();
        if (!slots || slots.length === 0) return;

        // Calculate values from time slots (first non-break slot is period 1)
        const mondaySlots = slots.filter(s => s.day === 'Monday').sort((a, b) => {
            const ta = a.start_time.split(':').map(Number); const tb = b.start_time.split(':').map(Number);
            return (ta[0] * 60 + ta[1]) - (tb[0] * 60 + tb[1]);
        });
        if (mondaySlots.length === 0) return;

        // filter out breaks
        const periods = mondaySlots.filter(s => !s.is_break && s.period && s.period > 0);
        if (periods.length === 0) return;

        const periodCount = periods.length;
        const firstSlot = periods[0];
        const [sHour, sMin] = firstSlot.start_time.split(':').map(Number);
        const [eHour, eMin] = firstSlot.end_time.split(':').map(Number);
        const durationMins = (eHour * 60 + eMin) - (sHour * 60 + sMin);

        // Update UI inputs
        const periodCountInput = document.getElementById('periodCount');
        const periodDurationInput = document.getElementById('periodDuration');
        const periodStartHourInput = document.getElementById('periodStartHour');

        if (periodCountInput) periodCountInput.value = periodCount;
        if (periodDurationInput) periodDurationInput.value = durationMins;
        if (periodStartHourInput) periodStartHourInput.value = sHour;

        console.log(`Updated period settings: ${periodCount} periods, ${durationMins} min each, start at ${sHour}:00`);
    } catch (err) {
        console.log('Could not update period settings UI:', err);
    }
}

/**
 * Fetch time slots from backend (cached)
 */
async function fetchTimeSlots() {
    if (cachedTimeSlots) return cachedTimeSlots;
    try {
        const resp = await fetch(`${API_BASE_URL}/api/operational/time-slots`);
        if (resp.ok) {
            cachedTimeSlots = await resp.json();
            return cachedTimeSlots;
        }
    } catch (e) {
        console.error('Failed to fetch time slots:', e);
    }
    return [];
}

/**
 * Fetch schedule config from backend (cached)
 */
async function fetchScheduleConfig() {
    if (cachedScheduleConfig) return cachedScheduleConfig;
    try {
        const resp = await fetch(`${API_BASE_URL}/api/operational/schedule-config`);
        if (resp.ok) {
            cachedScheduleConfig = await resp.json();
            return cachedScheduleConfig;
        }
    } catch (e) {
        console.error('Failed to fetch schedule config:', e);
    }
    return null;
}

/**
 * Clear cached data (call after config changes)
 */
function clearCache() {
    cachedTimeSlots = null;
    cachedScheduleConfig = null;
}

/**
 * Fetch latest timetable from backend
 */
async function loadTimetable() {
    setButtonLoading('loadBtn', true);
    showStatus('Fetching latest timetable...', 'info');

    try {
        // Fetch time slots and config first for dynamic rendering
        clearCache(); // Clear cache to get fresh data
        const [timeSlots, scheduleConfig] = await Promise.all([
            fetchTimeSlots(),
            fetchScheduleConfig()
        ]);

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

        if (data.status === 'failed' || data.status === 'error') {
            showStatus('Last generation failed. Please generate a new schedule.', 'error');
            renderTimetable(data, timeSlots, scheduleConfig);
            return;
        }

        if (data.status === 'processing') {
            showStatus('Timetable generation is in progress...', 'info');
            renderTimetable(data, timeSlots, scheduleConfig);
            setTimeout(() => loadTimetable(), 2000);
            return;
        }

        if (!data.entries || data.entries.length === 0) {
            showStatus('Timetable is empty. Please generate a new schedule.', 'warning');
            renderTimetable(data, timeSlots, scheduleConfig);
            return;
        }

        renderTimetable(data, timeSlots, scheduleConfig);
        await fetchAndDisplayStats();

        // Populate group filter
        updateGroupFilter(data);

        // Update period settings UI from current time slots and config
        await updatePeriodSettingsUI();
        await loadScheduleConfigUI();
        
        // Display all time slots
        await displayTimeSlots();

        showStatus('Timetable loaded successfully!', 'success');

    } catch (error) {
        console.error('Error loading timetable:', error);
        showStatus(`Error loading timetable: ${error.message}. Make sure backend is running on port 8000.`, 'error');
    } finally {
        setButtonLoading('loadBtn', false);
    }
}

/**
 * Generate new timetable using CSP algorithm
 */
async function generateNewTimetable() {
    setButtonLoading('generateBtn', true);
    showStatus('Generating new timetable (this may take a moment)...', 'info');

    try {
        // Use selected algorithm and include optional name
        const payload = { method: 'csp', name: 'Demo Schedule ' + new Date().toISOString().split('T')[0] };
        // Use URL-encoded form data to avoid CORS preflight caused by JSON content-type
        const params = new URLSearchParams(payload);
        const response = await fetch(`${API_BASE_URL}/api/solvers/generate`, {
            method: 'POST',
            body: params
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
        // Fetch counts from various endpoints
        const [teachersRes, roomsRes, subjectsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/api/teachers/`),
            fetch(`${API_BASE_URL}/api/rooms/`),
            fetch(`${API_BASE_URL}/api/subjects/`)
        ]);

        const teachers = await teachersRes.json();
        const rooms = await roomsRes.json();
        const subjects = await subjectsRes.json();

        // Get unique class groups from timetable
        const classGroups = new Set();
        if (currentTimetable && currentTimetable.entries) {
            currentTimetable.entries.forEach(slot => {
                if (slot.class_group && slot.class_group.name) {
                    classGroups.add(slot.class_group.name);
                }
            });
        }

        // Update stats
        document.getElementById('teacherCount').textContent = teachers.length || 0;
        document.getElementById('roomCount').textContent = rooms.length || 0;
        document.getElementById('subjectCount').textContent = subjects.length || 0;
        document.getElementById('classCount').textContent = classGroups.size || 0;

        // Show stats section
        document.getElementById('statsSection').style.display = 'block';

        // Create subject legend
        createLegend(subjects);

    } catch (error) {
        console.error('Error fetching stats:', error);
    }
}

/**
 * Apply period configuration by calling backend endpoint to recreate time slots
 */
async function applyPeriodSettings() {
    const count = parseInt(document.getElementById('periodCount').value || '7', 10);
    const duration = parseInt(document.getElementById('periodDuration').value || '60', 10);
    const startHour = parseInt(document.getElementById('periodStartHour').value || '9', 10);

    if (!count || count < 1) { showStatus('Invalid period count', 'error'); return; }
    if (!duration || duration < 10) { showStatus('Invalid period duration', 'error'); return; }

    setButtonLoading('applyPeriodsBtn', true);
    showStatus('Applying period settings...', 'info');

    try {
        const resp = await fetch(`${API_BASE_URL}/api/operational/time-slots/configure?number_of_periods=${count}&period_length_minutes=${duration}&start_hour=${startHour}`, {
            method: 'POST'
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.detail || `HTTP ${resp.status}`);
        }

        const data = await resp.json();
        showStatus(data.message || 'Periods updated', 'success');

    } catch (err) {
        console.error('Apply periods error', err);
        showStatus(`Failed to apply periods: ${err.message}`, 'error');
    } finally {
        setButtonLoading('applyPeriodsBtn', false);
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
                <div class="legend-code">${subject.code || 'N/A'}</div>
            </div>
        `;
        legendGrid.appendChild(legendItem);
    });

    document.getElementById('legendSection').style.display = 'block';
}

/**
 * Update Group Filter Dropdown
 */
function updateGroupFilter(data) {
    const groupFilter = document.getElementById('groupFilter');
    if (!groupFilter) return;

    // Extract unique groups
    const groups = new Map();
    if (data && data.entries) {
        data.entries.forEach(entry => {
            if (entry.class_group) {
                groups.set(entry.class_group.id, entry.class_group.name);
            }
        });
    }

    // Sort groups by name
    const sortedGroups = Array.from(groups.entries()).sort((a, b) => a[1].localeCompare(b[1]));

    // Save current selection
    const currentSelection = groupFilter.value;

    // Clear and repopulate
    groupFilter.innerHTML = '<option value="">All Groups</option>';

    sortedGroups.forEach(([id, name]) => {
        const option = document.createElement('option');
        option.value = id;
        option.textContent = name;
        groupFilter.appendChild(option);
    });

    // Restore selection or default to first group if "All Groups" was not explicitly selected
    if (currentSelection && groups.has(parseInt(currentSelection))) {
        groupFilter.value = currentSelection;
    } else if (sortedGroups.length > 0) {
        // Default to the first group so the view is clean by default
        groupFilter.value = sortedGroups[0][0];
        // Re-render with this default
        renderTimetable(data, cachedTimeSlots, cachedScheduleConfig);
    }

    groupFilter.style.display = 'inline-block';
}

/**
 * Display all time slots in the review section
 */
async function displayTimeSlots() {
    const displayElement = document.getElementById('timeSlotsDisplay');
    const totalSlotsElement = document.getElementById('infoTotalSlots');
    
    if (!displayElement) return;

    try {
        const timeSlots = await fetchTimeSlots();
        
        if (!timeSlots || timeSlots.length === 0) {
            displayElement.innerHTML = '<p style="color: #999;">No time slots configured yet.</p>';
            if (totalSlotsElement) totalSlotsElement.textContent = '0 slots';
            return;
        }

        // Group slots by day
        const slotsByDay = {};
        let nonBreakCount = 0;
        
        timeSlots.forEach(slot => {
            if (!slotsByDay[slot.day]) {
                slotsByDay[slot.day] = [];
            }
            slotsByDay[slot.day].push(slot);
            if (!slot.is_break) {
                nonBreakCount++;
            }
        });

        // Build HTML
        let html = '<div style="display: grid; gap: 1rem;">';
        
        const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        dayOrder.forEach(day => {
            if (slotsByDay[day]) {
                const slots = slotsByDay[day].sort((a, b) => a.period - b.period);
                html += `
                    <div style="border-left: 3px solid #4f46e5; padding-left: 1rem;">
                        <div style="font-weight: 600; color: #4f46e5; margin-bottom: 0.5rem;">${day}</div>
                        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                `;
                
                slots.forEach(slot => {
                    const bgColor = slot.is_break ? '#fef3c7' : '#e0e7ff';
                    const textColor = slot.is_break ? '#92400e' : '#3730a3';
                    const icon = slot.is_break ? '☕' : '📚';
                    
                    html += `
                        <div style="background: ${bgColor}; color: ${textColor}; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 12px; display: flex; align-items: center; gap: 0.25rem;">
                            <span>${icon}</span>
                            <span>P${slot.period}: ${slot.start_time}-${slot.end_time}</span>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
        });
        
        html += '</div>';
        displayElement.innerHTML = html;
        
        // Update total slots count
        if (totalSlotsElement) {
            totalSlotsElement.textContent = `${nonBreakCount} slots (${timeSlots.length} total)`;
        }
        
    } catch (error) {
        console.error('Error displaying time slots:', error);
        displayElement.innerHTML = '<p style="color: #ef4444;">Error loading time slots</p>';
    }
}

/**
 * Upload dataset file to backend import endpoint
 */
async function uploadDataset() {
    const importType = document.getElementById('importType')?.value;
    const fileInput = document.getElementById('importFile');
    const file = fileInput?.files?.[0];
    const clearExisting = document.getElementById('clearExisting')?.checked || false;

    if (!importType) {
        showStatus('Please select a dataset type to import', 'warning');
        return;
    }
    if (!file) {
        showStatus('Please choose a CSV file to upload', 'warning');
        return;
    }

    const btnId = 'importBtn';
    setButtonLoading(btnId, true);
    showStatus(`Uploading ${file.name}...`, 'info');

    try {
        const formData = new FormData();
        formData.append('dataset', importType);
        formData.append('file', file, file.name);
        formData.append('clear_existing', clearExisting.toString());

        const resp = await fetch(`${API_BASE_URL}/api/import/`, {
            method: 'POST',
            body: formData
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(err.detail || `HTTP ${resp.status}`);
        }

        const data = await resp.json();
        let msg = data.message || 'Import completed';
        if (data.cleared) {
            msg += ` (cleared ${data.cleared} existing)`;
        }
        if (data.skipped > 0) {
            msg += ` (${data.skipped} duplicates skipped)`;
        }
        showStatus(msg, 'success');

        // Clear the file input for next upload
        if (fileInput) fileInput.value = '';

        // Refresh stats to reflect newly imported items
        await fetchAndDisplayStats();

    } catch (error) {
        console.error('Import error:', error);
        showStatus(`Import failed: ${error.message}`, 'error');
    } finally {
        setButtonLoading(btnId, false);
    }
}

/**
 * Build dynamic periods array from time slots
 */
function buildPeriodsFromTimeSlots(timeSlots, scheduleConfig) {
    if (!timeSlots || timeSlots.length === 0) {
        // Fallback to defaults if no time slots
        return [
            { period: 1, time: '9:00 - 10:00', isBreak: false },
            { period: 2, time: '10:00 - 11:00', isBreak: false },
            { period: 3, time: '11:00 - 12:00', isBreak: false },
            { period: 4, time: '12:00 - 13:00', isBreak: true },
            { period: 5, time: '13:00 - 14:00', isBreak: false },
            { period: 6, time: '14:00 - 15:00', isBreak: false },
            { period: 7, time: '15:00 - 16:00', isBreak: false },
        ];
    }

    // Get unique periods from Monday (or first available day) sorted by start_time
    const firstDay = timeSlots.find(s => s.day)?.day || 'Monday';
    const daySlots = timeSlots
        .filter(s => s.day === firstDay)
        .sort((a, b) => {
            const timeA = a.start_time.split(':').map(Number);
            const timeB = b.start_time.split(':').map(Number);
            return (timeA[0] * 60 + timeA[1]) - (timeB[0] * 60 + timeB[1]);
        });

    const periods = [];
    const seenPeriods = new Set();

    // Also check for lunch break from config
    let lunchStart = null, lunchEnd = null;
    if (scheduleConfig && scheduleConfig.lunch_break_start && scheduleConfig.lunch_break_end) {
        lunchStart = scheduleConfig.lunch_break_start;
        lunchEnd = scheduleConfig.lunch_break_end;
    }

    daySlots.forEach(slot => {
        // Check if we need to insert lunch break before this slot
        if (lunchStart && !seenPeriods.has('lunch')) {
            const slotStartMins = parseInt(slot.start_time.split(':')[0]) * 60 + parseInt(slot.start_time.split(':')[1]);
            const lunchStartMins = parseInt(lunchStart.split(':')[0]) * 60 + parseInt(lunchStart.split(':')[1]);

            if (slotStartMins >= lunchStartMins && periods.length > 0) {
                // Insert lunch break
                periods.push({
                    period: 0,
                    time: `${lunchStart} - ${lunchEnd}`,
                    isBreak: true,
                    isLunch: true
                });
                seenPeriods.add('lunch');
            }
        }

        if (slot.is_break) {
            // Add break slot
            periods.push({
                period: slot.period || 0,
                time: `${slot.start_time} - ${slot.end_time}`,
                isBreak: true
            });
        } else if (!seenPeriods.has(slot.period)) {
            periods.push({
                period: slot.period,
                time: `${slot.start_time} - ${slot.end_time}`,
                isBreak: false
            });
            seenPeriods.add(slot.period);
        }
    });

    // If lunch wasn't inserted yet (e.g., it comes after all periods), add it
    if (lunchStart && !seenPeriods.has('lunch') && periods.length > 0) {
        // Find appropriate position based on time
        const lunchStartMins = parseInt(lunchStart.split(':')[0]) * 60 + parseInt(lunchStart.split(':')[1]);
        let insertIdx = periods.length;
        for (let i = 0; i < periods.length; i++) {
            const pTime = periods[i].time.split(' - ')[0];
            const pMins = parseInt(pTime.split(':')[0]) * 60 + parseInt(pTime.split(':')[1]);
            if (pMins >= lunchStartMins) {
                insertIdx = i;
                break;
            }
        }
        periods.splice(insertIdx, 0, {
            period: 0,
            time: `${lunchStart} - ${lunchEnd}`,
            isBreak: true,
            isLunch: true
        });
    }

    return periods;
}

/**
 * Get days from schedule config or default
 */
function getDaysFromConfig(scheduleConfig) {
    if (scheduleConfig && scheduleConfig.schedule_days && scheduleConfig.schedule_days.length > 0) {
        return scheduleConfig.schedule_days;
    }
    return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
}

/**
 * Render timetable grid
 */
function renderTimetable(timetableData, timeSlots = null, scheduleConfig = null) {
    const gridElement = document.getElementById('timetableGrid');
    const groupFilter = document.getElementById('groupFilter');
    const selectedGroupId = groupFilter ? groupFilter.value : null;

    // Use cached values if not provided
    timeSlots = timeSlots || cachedTimeSlots || [];
    scheduleConfig = scheduleConfig || cachedScheduleConfig || null;

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

    // Filter entries if a group is selected
    let entriesToRender = timetableData.entries;
    if (selectedGroupId) {
        entriesToRender = timetableData.entries.filter(entry =>
            entry.class_group && entry.class_group.id.toString() === selectedGroupId
        );

        if (entriesToRender.length === 0) {
            gridElement.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">👥</div>
                    <h3>No Classes Found</h3>
                    <p>No classes scheduled for the selected group.</p>
                </div>
            `;
            return;
        }
    }

    // Organize slots by day and period
    const schedule = organizeSchedule(entriesToRender);

    // Build dynamic periods and days from config
    const periods = buildPeriodsFromTimeSlots(timeSlots, scheduleConfig);
    const days = getDaysFromConfig(scheduleConfig);

    // Build table HTML
    const table = document.createElement('table');
    table.className = 'timetable-table';

    // Header row - dynamic based on schedule_days
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    let headerHTML = '<th>Time</th>';
    days.forEach(day => {
        headerHTML += `<th>${day}</th>`;
    });
    headerRow.innerHTML = headerHTML;
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Body rows
    const tbody = document.createElement('tbody');
    const skippedCells = new Set(); // Track cells that are covered by rowSpan

    periods.forEach(({ period, time, isBreak, isLunch }) => {
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
            cell.innerHTML = isLunch ? '🍽️ LUNCH BREAK' : '☕ BREAK';
            row.appendChild(cell);
        } else {
            // Day cells
            days.forEach(day => {
                const cellKey = `${day}-${period}`;

                // If this cell is covered by a previous rowSpan, skip creating it
                if (skippedCells.has(cellKey)) {
                    return;
                }

                const cell = document.createElement('td');
                const slots = schedule[day]?.[period] || [];

                // Check for merge possibility (vertical)
                let rowSpan = 1;
                if (slots.length > 0) {
                    const currentSlot = slots[0];
                    const nextPeriodObj = periods.find(p => p.period === period + 1 && !p.isBreak);
                    if (nextPeriodObj) {
                        const nextPeriod = nextPeriodObj.period;
                        const nextSlots = schedule[day]?.[nextPeriod] || [];

                        if (nextSlots.length > 0) {
                            const nextSlot = nextSlots[0];
                            // Check if same subject and same group
                            if (currentSlot.subject && nextSlot.subject &&
                                currentSlot.subject.id === nextSlot.subject.id &&
                                currentSlot.class_group.id === nextSlot.class_group.id) {

                                // Merge!
                                rowSpan = 2;
                                cell.rowSpan = 2;
                                skippedCells.add(`${day}-${nextPeriod}`);

                                // Adjust cell style to look centered/merged
                                cell.style.verticalAlign = 'middle';
                            }
                        }
                    }
                }

                cell.appendChild(createScheduleCell(slots, rowSpan > 1));
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
function createScheduleCell(slots, isMerged = false) {
    const cell = document.createElement('div');

    if (slots.length === 0) {
        cell.className = 'schedule-cell empty';
        cell.textContent = 'Free';
        return cell;
    }

    // For now, just show the first slot if there are multiple
    const slot = slots[0];
    cell.className = 'schedule-cell has-class';
    if (isMerged) {
        cell.classList.add('merged-cell');
        cell.style.height = '100%'; // Ensure it fills the rowspan
        cell.style.display = 'flex';
        cell.style.flexDirection = 'column';
        cell.style.justifyContent = 'center';
    }

    // Apply subject color
    if (slot.subject && slot.subject.id && subjectColorMap[slot.subject.id]) {
        cell.style.background = subjectColorMap[slot.subject.id];
    } else {
        // Fallback color if subject not in map
        const fallbackColor = SUBJECT_COLORS[0];
        cell.style.background = fallbackColor;
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

// ==================== LOAD FACTOR ANALYSIS ====================
// Define these functions BEFORE initWizard() so they're available when tabs are clicked

let lfTeachersData = [];
let lfClassesData = [];
let lfSummary = {};

async function loadLoadFactorData() {
    console.log('loadLoadFactorData called');
    try {
        // Show loading state
        document.getElementById('lf-teacherLoadContainer').innerHTML = 
            '<div style="text-align: center; padding: 30px; color: #667eea;"><i class="fas fa-spinner fa-spin"></i> Loading teacher data...</div>';
        document.getElementById('lf-classLoadContainer').innerHTML = 
            '<div style="text-align: center; padding: 30px; color: #667eea;"><i class="fas fa-spinner fa-spin"></i> Loading class data...</div>';

        console.log('Fetching from:', `${API_BASE_URL}/api/analytics/load-factor`);
        
        const response = await fetch(`${API_BASE_URL}/api/analytics/load-factor`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to load load factor data');
        }

        const data = await response.json();
        console.log('Data received:', data);
        
        lfSummary = data.summary;
        lfTeachersData = data.teacher_load;
        lfClassesData = data.class_load;

        console.log('Teachers:', lfTeachersData.length, 'Classes:', lfClassesData.length);

        updateLoadFactorStats();
        renderTeacherLoad();
        renderClassLoad();
        setupLoadFactorFilters();

        console.log('Load factor data loaded successfully');

    } catch (error) {
        console.error('Error loading load factor data:', error);
        const errorMsg = `<div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; margin: 20px;">
            <strong>Error:</strong> ${error.message}<br><br>
            <small>Make sure you have generated a timetable first.</small>
        </div>`;
        document.getElementById('lf-teacherLoadContainer').innerHTML = errorMsg;
        document.getElementById('lf-classLoadContainer').innerHTML = errorMsg;
    }
}

function updateLoadFactorStats() {
    document.getElementById('lf-totalTeachers').textContent = lfSummary.total_teachers || 0;
    document.getElementById('lf-totalClasses').textContent = lfSummary.total_classes || 0;
    document.getElementById('lf-totalPeriods').textContent = lfSummary.total_periods || 0;
    document.getElementById('lf-avgTeacherLoad').textContent = lfSummary.avg_teacher_load || 0;
}

function getLoadClass(percentage) {
    if (percentage >= 80) return 'load-high';
    if (percentage >= 50) return 'load-medium';
    return 'load-low';
}

function getLoadLabel(percentage) {
    if (percentage >= 80) return 'High Load';
    if (percentage >= 50) return 'Medium Load';
    return 'Low Load';
}

function getLoadColor(percentage) {
    if (percentage >= 80) return '#f8d7da';
    if (percentage >= 50) return '#fff3cd';
    return '#d4edda';
}

function getLoadTextColor(percentage) {
    if (percentage >= 80) return '#721c24';
    if (percentage >= 50) return '#856404';
    return '#155724';
}

function renderTeacherLoad() {
    const container = document.getElementById('lf-teacherLoadContainer');
    
    if (lfTeachersData.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 30px; color: #666;">No teacher data available</div>';
        return;
    }

    container.innerHTML = lfTeachersData.map(teacher => `
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #667eea;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div style="font-size: 1.2em; font-weight: bold; color: #333;">${teacher.name}</div>
                <div style="padding: 6px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85em; background: ${getLoadColor(teacher.load_percentage)}; color: ${getLoadTextColor(teacher.load_percentage)};">
                    ${getLoadLabel(teacher.load_percentage)}
                </div>
            </div>
            
            <div style="width: 100%; height: 25px; background: #e9ecef; border-radius: 12px; overflow: hidden; margin: 10px 0;">
                <div style="height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); width: ${teacher.load_percentage}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.85em;">
                    ${teacher.total_periods}/${teacher.max_hours} (${teacher.load_percentage}%)
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 15px;">
                <div style="background: white; padding: 12px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">${teacher.total_periods}</div>
                    <div style="color: #666; font-size: 0.85em;">Total Periods</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">${teacher.load_percentage}%</div>
                    <div style="color: #666; font-size: 0.85em;">Load Factor</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">${teacher.avg_per_day}</div>
                    <div style="color: #666; font-size: 0.85em;">Avg Per Day</div>
                </div>
            </div>

            <div style="margin-top: 12px;">
                <strong style="color: #333;">Daily Distribution:</strong>
                <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                    ${Object.entries(teacher.daily_load).map(([day, count]) => 
                        `<div style="background: white; padding: 6px 12px; border-radius: 15px; font-size: 0.85em; border: 2px solid #667eea;">
                            ${day.substring(0, 3)}: ${count}
                        </div>`
                    ).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function renderClassLoad() {
    const container = document.getElementById('lf-classLoadContainer');
    
    if (lfClassesData.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 30px; color: #666;">No class data available</div>';
        return;
    }

    container.innerHTML = lfClassesData.map(classGroup => `
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #667eea;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <div style="font-size: 1.2em; font-weight: bold; color: #333;">${classGroup.name}</div>
                <div style="padding: 6px 12px; border-radius: 15px; font-weight: bold; font-size: 0.85em; background: ${getLoadColor(classGroup.load_percentage)}; color: ${getLoadTextColor(classGroup.load_percentage)};">
                    ${classGroup.total_periods}/25 periods
                </div>
            </div>
            
            <div style="width: 100%; height: 25px; background: #e9ecef; border-radius: 12px; overflow: hidden; margin: 10px 0;">
                <div style="height: 100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); width: ${classGroup.load_percentage}%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.85em;">
                    ${classGroup.total_periods}/25 (${classGroup.load_percentage}%)
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-top: 15px;">
                <div style="background: white; padding: 12px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">${classGroup.total_periods}</div>
                    <div style="color: #666; font-size: 0.85em;">Total Periods</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">${classGroup.load_percentage}%</div>
                    <div style="color: #666; font-size: 0.85em;">Utilization</div>
                </div>
                <div style="background: white; padding: 12px; border-radius: 6px; text-align: center;">
                    <div style="font-size: 1.5em; font-weight: bold; color: #667eea;">${classGroup.student_count}</div>
                    <div style="color: #666; font-size: 0.85em;">Students</div>
                </div>
            </div>

            <div style="margin-top: 12px;">
                <strong style="color: #333;">Daily Distribution:</strong>
                <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                    ${Object.entries(classGroup.daily_load).map(([day, count]) => 
                        `<div style="background: white; padding: 6px 12px; border-radius: 15px; font-size: 0.85em; border: 2px solid #667eea;">
                            ${day.substring(0, 3)}: ${count}
                        </div>`
                    ).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function setupLoadFactorFilters() {
    const teacherSort = document.getElementById('lf-teacherSort');
    const teacherFilter = document.getElementById('lf-teacherFilter');
    const classSort = document.getElementById('lf-classSort');
    
    if (!teacherSort || !teacherFilter || !classSort) {
        console.error('Filter elements not found');
        return;
    }

    let allTeachersData = [...lfTeachersData];
    
    teacherSort.addEventListener('change', (e) => {
        const sortBy = e.target.value;
        if (sortBy === 'load-desc') {
            lfTeachersData.sort((a, b) => b.load_percentage - a.load_percentage);
        } else if (sortBy === 'load-asc') {
            lfTeachersData.sort((a, b) => a.load_percentage - b.load_percentage);
        } else if (sortBy === 'name') {
            lfTeachersData.sort((a, b) => a.name.localeCompare(b.name));
        }
        renderTeacherLoad();
    });

    teacherFilter.addEventListener('change', (e) => {
        const filter = e.target.value;
        
        if (filter === 'high') {
            lfTeachersData = allTeachersData.filter(t => t.load_percentage >= 80);
        } else if (filter === 'medium') {
            lfTeachersData = allTeachersData.filter(t => t.load_percentage >= 50 && t.load_percentage < 80);
        } else if (filter === 'low') {
            lfTeachersData = allTeachersData.filter(t => t.load_percentage < 50);
        } else {
            lfTeachersData = [...allTeachersData];
        }

        renderTeacherLoad();
    });

    classSort.addEventListener('change', (e) => {
        const sortBy = e.target.value;
        if (sortBy === 'periods-desc') {
            lfClassesData.sort((a, b) => b.total_periods - a.total_periods);
        } else if (sortBy === 'periods-asc') {
            lfClassesData.sort((a, b) => a.total_periods - b.total_periods);
        } else if (sortBy === 'name') {
            lfClassesData.sort((a, b) => a.name.localeCompare(b.name));
        }
        renderClassLoad();
    });
}

// END LOAD FACTOR ANALYSIS


/**
 * Initialize Wizard Navigation and Progress Tracking
 */
function initWizard() {
    const tabs = document.querySelectorAll('.wizard-tab');
    const contents = document.querySelectorAll('.wizard-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const step = tab.getAttribute('data-step');

            // Update tabs
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update content view
            contents.forEach(c => c.classList.remove('active'));
            const content = document.getElementById(`step-${step}`);
            if (content) content.classList.add('active');

            // Trigger specific page logic
            if (step === 'lessons' && typeof loadLessons === 'function') {
                loadLessons();
            }
            
            // Load teachers when teachers tab is clicked
            if (step === 'teachers' && typeof loadTeachersInPage === 'function') {
                loadTeachersInPage();
            }
            
            if (step === 'loadfactor') {
                // Load factor analysis
                console.log('Load Factor tab clicked');
                setTimeout(() => {
                    console.log('Calling loadLoadFactorData');
                    if (typeof loadLoadFactorData === 'function') {
                        loadLoadFactorData();
                    } else {
                        console.error('loadLoadFactorData is not defined');
                    }
                }, 100);
            }
            if (step === 'review') {
                loadTimetable();
                displayTimeSlots();
            }
        });
    });

    // Initial progress check
    updateProgressCheckmarks();
}

/**
 * Update wizard progress checkmarks based on data availability
 */
async function updateProgressCheckmarks() {
    try {
        const [teachers, rooms, subjects, classes, lessons] = await Promise.all([
            fetch(`${API_BASE_URL}/api/teachers/`).then(r => r.json()).catch(() => []),
            fetch(`${API_BASE_URL}/api/rooms/`).then(r => r.json()).catch(() => []),
            fetch(`${API_BASE_URL}/api/subjects/`).then(r => r.json()).catch(() => []),
            fetch(`${API_BASE_URL}/api/operational/class-groups`).then(r => r.json()).catch(() => []),
            fetch(`${API_BASE_URL}/api/lessons/`).then(r => r.json()).catch(() => [])
        ]);

        const progress = {
            subjects: subjects.length > 0,
            teachers: teachers.length > 0,
            classes: classes.length > 0,
            rooms: rooms.length > 0,
            lessons: lessons.length > 0
        };

        Object.keys(progress).forEach(step => {
            const tab = document.querySelector(`.wizard-tab[data-step="${step}"]`);
            if (tab) {
                tab.classList.toggle('completed', progress[step]);
            }
        });
    } catch (error) {
        console.error('Error updating progress checkmarks:', error);
    }
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    initWizard();

    // Load config on page init
    loadScheduleConfigUI();
    updatePeriodSettingsUI();

    // Load lessons if on lessons tab
    if (typeof loadLessons === 'function') {
        const activeTab = document.querySelector('.wizard-tab.active');
        if (activeTab && activeTab.getAttribute('data-step') === 'lessons') {
            loadLessons();
        }
    }

    // Attach event listeners
    document.getElementById('generateBtn')?.addEventListener('click', generateNewTimetable);
    document.getElementById('loadLatestBtn')?.addEventListener('click', loadTimetable);
    document.getElementById('applySettingsBtn')?.addEventListener('click', applyAllSettings);

    // Auto-refresh when group filter changes (if it exists)
    document.getElementById('groupFilter')?.addEventListener('change', () => {
        if (currentTimetable) {
            renderTimetable(currentTimetable, cachedTimeSlots, cachedScheduleConfig);
        }
    });

    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
    
    // Desktop menu toggle (hamburger button in header)
    const desktopMenuToggle = document.getElementById('desktopMenuToggle');
    if (desktopMenuToggle && sidebar) {
        desktopMenuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }
});



// ==================== LOAD FACTOR ANALYSIS ====================


// ==================== TEACHER MANAGEMENT ====================
let allTeachersData = [];
let editingTeacherId = null;
let deletingTeacherId = null;

async function loadTeachersInPage() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/teachers/`);
        if (!response.ok) throw new Error('Failed to load teachers');
        
        allTeachersData = await response.json();
        renderTeachersInPage(allTeachersData);
    } catch (error) {
        console.error('Error loading teachers:', error);
        document.getElementById('teachersListContainer').innerHTML = 
            '<div style="text-align: center; padding: 30px; color: #dc3545;">Failed to load teachers. Make sure the backend is running.</div>';
    }
}

function renderTeachersInPage(teachers) {
    const container = document.getElementById('teachersListContainer');
    
    if (!teachers || teachers.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 30px; color: #666;">No teachers found. Click "Add New Teacher" to get started!</div>';
        return;
    }

    container.innerHTML = teachers.map(teacher => `
        <div class="teacher-card" style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <div style="font-size: 1.2em; font-weight: bold; color: #333; margin-bottom: 5px;">${teacher.name}</div>
                    <div style="color: #666; font-size: 0.9em;">📧 ${teacher.email}</div>
                </div>
            </div>
            
            <div style="background: white; padding: 12px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="color: #667eea; font-weight: bold;">Max Hours/Week:</span>
                    <span>${teacher.max_hours_per_week || 20} hours</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #667eea; font-weight: bold;">Teacher ID:</span>
                    <span>#${teacher.id}</span>
                </div>
            </div>

            <div style="display: flex; gap: 10px;">
                <button class="btn btn-primary" onclick="openEditTeacherModal(${teacher.id})" style="flex: 1; padding: 8px; font-size: 0.9em;">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn btn-danger" onclick="openDeleteTeacherModal(${teacher.id}, '${teacher.name.replace(/'/g, "\\'")}')}" style="flex: 1; padding: 8px; font-size: 0.9em; background: #dc3545;">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}

function filterTeachersInPage() {
    const searchTerm = document.getElementById('teacherSearchInput').value.toLowerCase();
    const filtered = allTeachersData.filter(teacher => 
        teacher.name.toLowerCase().includes(searchTerm) ||
        teacher.email.toLowerCase().includes(searchTerm)
    );
    renderTeachersInPage(filtered);
}

function openTeacherModal() {
    editingTeacherId = null;
    document.getElementById('teacherModalTitle').textContent = 'Add New Teacher';
    document.getElementById('teacherForm').reset();
    document.getElementById('teacherHours').value = 20;
    document.getElementById('teacherModal').style.display = 'flex';
}

function openEditTeacherModal(teacherId) {
    const teacher = allTeachersData.find(t => t.id === teacherId);
    if (!teacher) return;

    editingTeacherId = teacherId;
    document.getElementById('teacherModalTitle').textContent = 'Edit Teacher';
    document.getElementById('teacherName').value = teacher.name;
    document.getElementById('teacherEmail').value = teacher.email;
    document.getElementById('teacherHours').value = teacher.max_hours_per_week || 20;
    document.getElementById('teacherModal').style.display = 'flex';
}

function closeTeacherModal() {
    document.getElementById('teacherModal').style.display = 'none';
    editingTeacherId = null;
}

async function saveTeacher(event) {
    event.preventDefault();

    const teacherData = {
        name: document.getElementById('teacherName').value,
        email: document.getElementById('teacherEmail').value,
        max_hours_per_week: parseInt(document.getElementById('teacherHours').value),
        available_slots: []
    };

    try {
        let response;
        if (editingTeacherId) {
            response = await fetch(`${API_BASE_URL}/api/teachers/${editingTeacherId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(teacherData)
            });
        } else {
            response = await fetch(`${API_BASE_URL}/api/teachers/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(teacherData)
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save teacher');
        }

        showStatus(editingTeacherId ? 'Teacher updated successfully!' : 'Teacher added successfully!', 'success');
        closeTeacherModal();
        loadTeachersInPage();
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
}

function openDeleteTeacherModal(teacherId, teacherName) {
    deletingTeacherId = teacherId;
    document.getElementById('deleteTeacherName').textContent = teacherName;
    document.getElementById('deleteTeacherModal').style.display = 'flex';
}

function closeDeleteTeacherModal() {
    document.getElementById('deleteTeacherModal').style.display = 'none';
    deletingTeacherId = null;
}

async function confirmDeleteTeacher() {
    if (!deletingTeacherId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/teachers/${deletingTeacherId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete teacher');
        }

        showStatus('Teacher deleted successfully!', 'success');
        closeDeleteTeacherModal();
        loadTeachersInPage();
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
        closeDeleteTeacherModal();
    }
}

// Load teachers when the teachers tab is clicked - integrated into initWizard above
// Also load on page load if teachers tab is already active
document.addEventListener('DOMContentLoaded', () => {
    const activeTab = document.querySelector('.wizard-tab.active');
    if (activeTab && activeTab.getAttribute('data-step') === 'teachers') {
        setTimeout(() => loadTeachersInPage(), 500);
    }
});

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    const teacherModal = document.getElementById('teacherModal');
    const deleteModal = document.getElementById('deleteTeacherModal');
    
    if (event.target === teacherModal) {
        closeTeacherModal();
    }
    if (event.target === deleteModal) {
        closeDeleteTeacherModal();
    }
});


// ==================== EXPORT FUNCTIONS ====================

// Export timetable to PDF (using print)
function exportTimetableToPDF() {
    alert('Opening print dialog...\n\nTip: Select "Save as PDF" as your printer to save the timetable as a PDF file.');
    window.print();
}

// Export timetable to CSV
function exportTimetableToCSV() {
    if (!currentTimetable || !currentTimetable.entries || currentTimetable.entries.length === 0) {
        alert('No timetable data to export. Please load or generate a timetable first.');
        return;
    }

    // Create CSV header
    let csv = 'Day,Time,Class,Subject,Teacher,Room\n';

    // Group entries by day and time
    const entries = currentTimetable.entries;
    
    // Sort entries by day and time
    const dayOrder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    entries.sort((a, b) => {
        const dayCompare = dayOrder.indexOf(a.time_slot?.day_of_week || '') - dayOrder.indexOf(b.time_slot?.day_of_week || '');
        if (dayCompare !== 0) return dayCompare;
        return (a.time_slot?.start_time || '').localeCompare(b.time_slot?.start_time || '');
    });

    // Add data rows
    entries.forEach(entry => {
        const day = entry.time_slot?.day_of_week || 'N/A';
        const time = entry.time_slot ? `${entry.time_slot.start_time} - ${entry.time_slot.end_time}` : 'N/A';
        const className = entry.class_group?.name || 'N/A';
        const subject = entry.subject?.name || 'N/A';
        const teacher = entry.teacher?.name || 'TBA';
        const room = entry.room?.name || 'TBA';

        csv += `"${day}","${time}","${className}","${subject}","${teacher}","${room}"\n`;
    });

    // Create download link
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `timetable_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showNotification('Timetable exported to CSV successfully!', 'success');
}

// Show notification helper
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        font-weight: 500;
    `;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}
