const API_BASE = 'http://localhost:8000/api';

let teachersData = [];
let classesData = [];
let timetableData = null;

// Load all data
async function loadData() {
    try {
        // Fetch timetable
        const timetableRes = await fetch(`${API_BASE}/timetables/latest`);
        if (!timetableRes.ok) throw new Error('Failed to load timetable');
        timetableData = await timetableRes.json();

        // Fetch teachers
        const teachersRes = await fetch(`${API_BASE}/teachers`);
        if (!teachersRes.ok) throw new Error('Failed to load teachers');
        const teachers = await teachersRes.json();

        // Fetch classes
        const classesRes = await fetch(`${API_BASE}/class-groups`);
        if (!classesRes.ok) throw new Error('Failed to load classes');
        const classes = await classesRes.json();

        // Fetch time slots
        const slotsRes = await fetch(`${API_BASE}/time-slots`);
        if (!slotsRes.ok) throw new Error('Failed to load time slots');
        const slots = await slotsRes.json();

        // Calculate teacher load
        teachersData = calculateTeacherLoad(teachers, timetableData.entries, slots);
        
        // Calculate class load
        classesData = calculateClassLoad(classes, timetableData.entries, slots);

        // Update UI
        updateStats();
        renderTeachers();
        renderClasses();

        // Setup filters
        setupFilters();

    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('teacherLoadContainer').innerHTML = 
            `<div class="error">Error: ${error.message}. Make sure backend is running and timetable is generated.</div>`;
        document.getElementById('classLoadContainer').innerHTML = 
            `<div class="error">Error: ${error.message}</div>`;
    }
}

function calculateTeacherLoad(teachers, entries, slots) {
    const nonBreakSlots = slots.filter(s => !s.is_break);
    const maxPeriodsPerWeek = 25; // 5 days × 5 periods
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

    return teachers.map(teacher => {
        const teacherEntries = entries.filter(e => e.teacher_id === teacher.id);
        const totalPeriods = teacherEntries.length;
        const loadPercentage = (totalPeriods / maxPeriodsPerWeek) * 100;

        // Calculate daily distribution
        const dailyLoad = {};
        days.forEach(day => {
            const dayEntries = teacherEntries.filter(e => {
                const slot = slots.find(s => s.id === e.time_slot_id);
                return slot && slot.day === day;
            });
            dailyLoad[day] = dayEntries.length;
        });

        // Calculate subject distribution
        const subjectDistribution = {};
        teacherEntries.forEach(entry => {
            const subjectId = entry.subject_id;
            subjectDistribution[subjectId] = (subjectDistribution[subjectId] || 0) + 1;
        });

        return {
            ...teacher,
            totalPeriods,
            loadPercentage: Math.round(loadPercentage),
            dailyLoad,
            subjectDistribution,
            maxHours: teacher.max_hours_per_week || 20
        };
    });
}

function calculateClassLoad(classes, entries, slots) {
    const maxPeriodsPerWeek = 25;
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

    return classes.map(classGroup => {
        const classEntries = entries.filter(e => e.class_group_id === classGroup.id);
        const totalPeriods = classEntries.length;
        const loadPercentage = (totalPeriods / maxPeriodsPerWeek) * 100;

        // Calculate daily distribution
        const dailyLoad = {};
        days.forEach(day => {
            const dayEntries = classEntries.filter(e => {
                const slot = slots.find(s => s.id === e.time_slot_id);
                return slot && slot.day === day;
            });
            dailyLoad[day] = dayEntries.length;
        });

        // Calculate subject distribution
        const subjectDistribution = {};
        classEntries.forEach(entry => {
            const subjectId = entry.subject_id;
            subjectDistribution[subjectId] = (subjectDistribution[subjectId] || 0) + 1;
        });

        return {
            ...classGroup,
            totalPeriods,
            loadPercentage: Math.round(loadPercentage),
            dailyLoad,
            subjectDistribution
        };
    });
}

function updateStats() {
    document.getElementById('totalTeachers').textContent = teachersData.length;
    document.getElementById('totalClasses').textContent = classesData.length;
    document.getElementById('totalPeriods').textContent = timetableData.entries.length;
    
    const avgLoad = teachersData.reduce((sum, t) => sum + t.totalPeriods, 0) / teachersData.length;
    document.getElementById('avgTeacherLoad').textContent = Math.round(avgLoad);
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

function renderTeachers() {
    const container = document.getElementById('teacherLoadContainer');
    
    if (teachersData.length === 0) {
        container.innerHTML = '<div class="loading">No teacher data available</div>';
        return;
    }

    container.innerHTML = teachersData.map(teacher => `
        <div class="teacher-card">
            <div class="card-header">
                <div class="card-title">${teacher.name}</div>
                <div class="load-badge ${getLoadClass(teacher.loadPercentage)}">
                    ${getLoadLabel(teacher.loadPercentage)}
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${teacher.loadPercentage}%">
                    ${teacher.totalPeriods}/${teacher.maxHours} periods (${teacher.loadPercentage}%)
                </div>
            </div>

            <div class="details-grid">
                <div class="detail-item">
                    <div class="detail-value">${teacher.totalPeriods}</div>
                    <div class="detail-label">Total Periods</div>
                </div>
                <div class="detail-item">
                    <div class="detail-value">${teacher.loadPercentage}%</div>
                    <div class="detail-label">Load Factor</div>
                </div>
                <div class="detail-item">
                    <div class="detail-value">${Math.round(teacher.totalPeriods / 5)}</div>
                    <div class="detail-label">Avg Per Day</div>
                </div>
                <div class="detail-item">
                    <div class="detail-value">${Object.keys(teacher.subjectDistribution).length}</div>
                    <div class="detail-label">Subjects</div>
                </div>
            </div>

            <div style="margin-top: 15px;">
                <strong>Daily Distribution:</strong>
                <div class="day-distribution">
                    ${Object.entries(teacher.dailyLoad).map(([day, count]) => 
                        `<div class="day-chip">${day.substring(0, 3)}: ${count} periods</div>`
                    ).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function renderClasses() {
    const container = document.getElementById('classLoadContainer');
    
    if (classesData.length === 0) {
        container.innerHTML = '<div class="loading">No class data available</div>';
        return;
    }

    container.innerHTML = classesData.map(classGroup => `
        <div class="class-card">
            <div class="card-header">
                <div class="card-title">${classGroup.name}</div>
                <div class="load-badge ${getLoadClass(classGroup.loadPercentage)}">
                    ${classGroup.totalPeriods}/25 periods
                </div>
            </div>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${classGroup.loadPercentage}%">
                    ${classGroup.totalPeriods}/25 periods (${classGroup.loadPercentage}%)
                </div>
            </div>

            <div class="details-grid">
                <div class="detail-item">
                    <div class="detail-value">${classGroup.totalPeriods}</div>
                    <div class="detail-label">Total Periods</div>
                </div>
                <div class="detail-item">
                    <div class="detail-value">${classGroup.loadPercentage}%</div>
                    <div class="detail-label">Utilization</div>
                </div>
                <div class="detail-item">
                    <div class="detail-value">${classGroup.student_count}</div>
                    <div class="detail-label">Students</div>
                </div>
                <div class="detail-item">
                    <div class="detail-value">${Object.keys(classGroup.subjectDistribution).length}</div>
                    <div class="detail-label">Subjects</div>
                </div>
            </div>

            <div style="margin-top: 15px;">
                <strong>Daily Distribution:</strong>
                <div class="day-distribution">
                    ${Object.entries(classGroup.dailyLoad).map(([day, count]) => 
                        `<div class="day-chip">${day.substring(0, 3)}: ${count} periods</div>`
                    ).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function setupFilters() {
    // Teacher sort
    document.getElementById('teacherSort').addEventListener('change', (e) => {
        const sortBy = e.target.value;
        if (sortBy === 'load-desc') {
            teachersData.sort((a, b) => b.loadPercentage - a.loadPercentage);
        } else if (sortBy === 'load-asc') {
            teachersData.sort((a, b) => a.loadPercentage - b.loadPercentage);
        } else if (sortBy === 'name') {
            teachersData.sort((a, b) => a.name.localeCompare(b.name));
        }
        renderTeachers();
    });

    // Teacher filter
    document.getElementById('teacherFilter').addEventListener('change', (e) => {
        const filter = e.target.value;
        const container = document.getElementById('teacherLoadContainer');
        
        let filtered = teachersData;
        if (filter === 'high') {
            filtered = teachersData.filter(t => t.loadPercentage >= 80);
        } else if (filter === 'medium') {
            filtered = teachersData.filter(t => t.loadPercentage >= 50 && t.loadPercentage < 80);
        } else if (filter === 'low') {
            filtered = teachersData.filter(t => t.loadPercentage < 50);
        }

        if (filtered.length === 0) {
            container.innerHTML = '<div class="loading">No teachers match this filter</div>';
        } else {
            const temp = teachersData;
            teachersData = filtered;
            renderTeachers();
            teachersData = temp;
        }
    });

    // Class sort
    document.getElementById('classSort').addEventListener('change', (e) => {
        const sortBy = e.target.value;
        if (sortBy === 'periods-desc') {
            classesData.sort((a, b) => b.totalPeriods - a.totalPeriods);
        } else if (sortBy === 'periods-asc') {
            classesData.sort((a, b) => a.totalPeriods - b.totalPeriods);
        } else if (sortBy === 'name') {
            classesData.sort((a, b) => a.name.localeCompare(b.name));
        }
        renderClasses();
    });
}

// Load data on page load
loadData();
