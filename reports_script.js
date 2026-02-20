// Reports & Analytics Script
let teacherChart, roomChart;
let analyticsData = {
    teachers: [],
    classes: [],
    rooms: [],
    subjects: [],
    slots: [],
    timetable: []
};

// Initialize reports
async function initReports() {
    await loadAllData();
    updateStatCards();
    updateInsights();
    createCharts();
    populateTeacherTable();
}

// Load all data from APIs
async function loadAllData() {
    try {
        // Load teachers
        const teachersRes = await fetch('http://localhost:8000/api/teachers/');
        if (teachersRes.ok) analyticsData.teachers = await teachersRes.json();

        // Load classes
        const classesRes = await fetch('http://localhost:8000/api/class-groups/');
        if (classesRes.ok) analyticsData.classes = await classesRes.json();

        // Load rooms
        const roomsRes = await fetch('http://localhost:8000/api/rooms/');
        if (roomsRes.ok) analyticsData.rooms = await roomsRes.json();

        // Load subjects
        const subjectsRes = await fetch('http://localhost:8000/api/subjects/');
        if (subjectsRes.ok) analyticsData.subjects = await subjectsRes.json();

        // Load time slots
        const slotsRes = await fetch('http://localhost:8000/api/time-slots/');
        if (slotsRes.ok) analyticsData.slots = await slotsRes.json();

        // Load timetable
        const timetableRes = await fetch('http://localhost:8000/api/timetables/latest');
        if (timetableRes.ok) {
            const data = await timetableRes.json();
            analyticsData.timetable = data.entries || [];
        }

        console.log('Analytics data loaded:', analyticsData);
    } catch (error) {
        console.error('Error loading analytics data:', error);
    }
}

// Update stat cards
function updateStatCards() {
    document.getElementById('totalTeachers').textContent = analyticsData.teachers.length;
    document.getElementById('totalClasses').textContent = analyticsData.classes.length;
    document.getElementById('totalRooms').textContent = analyticsData.rooms.length;
    document.getElementById('totalSubjects').textContent = analyticsData.subjects.length;
    document.getElementById('totalSlots').textContent = analyticsData.slots.length;

    // Calculate overall utilization
    const totalPossibleSlots = analyticsData.classes.length * analyticsData.slots.length;
    const utilization = totalPossibleSlots > 0 
        ? ((analyticsData.timetable.length / totalPossibleSlots) * 100).toFixed(0)
        : 0;
    document.getElementById('overallUtilization').textContent = utilization + '%';
}

// Update insights
function updateInsights() {
    // Find busiest teacher
    const teacherLoad = {};
    analyticsData.timetable.forEach(entry => {
        if (entry.teacher) {
            teacherLoad[entry.teacher.id] = (teacherLoad[entry.teacher.id] || 0) + 1;
        }
    });

    let busiestTeacher = 'N/A';
    let maxLoad = 0;
    for (const [teacherId, load] of Object.entries(teacherLoad)) {
        if (load > maxLoad) {
            maxLoad = load;
            const teacher = analyticsData.teachers.find(t => t.id == teacherId);
            busiestTeacher = teacher ? teacher.name : 'Unknown';
        }
    }
    document.getElementById('busiestTeacher').textContent = busiestTeacher;

    // Find most used room
    const roomUsage = {};
    analyticsData.timetable.forEach(entry => {
        if (entry.room) {
            roomUsage[entry.room.id] = (roomUsage[entry.room.id] || 0) + 1;
        }
    });

    let mostUsedRoom = 'N/A';
    let maxUsage = 0;
    for (const [roomId, usage] of Object.entries(roomUsage)) {
        if (usage > maxUsage) {
            maxUsage = usage;
            const room = analyticsData.rooms.find(r => r.id == roomId);
            mostUsedRoom = room ? room.name : 'Unknown';
        }
    }
    document.getElementById('mostUsedRoom').textContent = mostUsedRoom;

    // Find most popular subject
    const subjectCount = {};
    analyticsData.timetable.forEach(entry => {
        if (entry.subject) {
            subjectCount[entry.subject.id] = (subjectCount[entry.subject.id] || 0) + 1;
        }
    });

    let popularSubject = 'N/A';
    let maxCount = 0;
    for (const [subjectId, count] of Object.entries(subjectCount)) {
        if (count > maxCount) {
            maxCount = count;
            const subject = analyticsData.subjects.find(s => s.id == subjectId);
            popularSubject = subject ? subject.name : 'Unknown';
        }
    }
    document.getElementById('popularSubject').textContent = popularSubject;
}

// Create charts
function createCharts() {
    createTeacherChart();
    createRoomChart();
}

// Create teacher workload chart
function createTeacherChart() {
    const ctx = document.getElementById('teacherChart').getContext('2d');

    // Calculate teacher workload
    const teacherLoad = {};
    analyticsData.timetable.forEach(entry => {
        if (entry.teacher) {
            teacherLoad[entry.teacher.id] = (teacherLoad[entry.teacher.id] || 0) + 1;
        }
    });

    const labels = [];
    const data = [];
    const colors = [];

    analyticsData.teachers.forEach(teacher => {
        const load = teacherLoad[teacher.id] || 0;
        const maxHours = teacher.max_hours_per_week || 20;
        const percentage = (load / maxHours * 100).toFixed(0);

        labels.push(teacher.name.split(' ')[0]); // First name only
        data.push(percentage);

        // Color based on load
        if (percentage >= 80) colors.push('#dc2626'); // Red
        else if (percentage >= 60) colors.push('#f59e0b'); // Orange
        else colors.push('#10b981'); // Green
    });

    if (teacherChart) teacherChart.destroy();

    teacherChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Workload %',
                data: data,
                backgroundColor: colors,
                borderRadius: 8,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Workload: ' + context.parsed.y + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Create room utilization chart
function createRoomChart() {
    const ctx = document.getElementById('roomChart').getContext('2d');

    // Calculate room usage
    const roomUsage = {};
    analyticsData.timetable.forEach(entry => {
        if (entry.room) {
            roomUsage[entry.room.id] = (roomUsage[entry.room.id] || 0) + 1;
        }
    });

    const labels = [];
    const data = [];

    analyticsData.rooms.forEach(room => {
        const usage = roomUsage[room.id] || 0;
        labels.push(room.name);
        data.push(usage);
    });

    if (roomChart) roomChart.destroy();

    roomChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b',
                    '#fa709a',
                    '#fee140',
                    '#30cfd0',
                    '#a8edea',
                    '#fed6e3'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return context.label + ': ' + context.parsed + ' periods (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Populate teacher table
function populateTeacherTable() {
    const tbody = document.getElementById('teacherTableBody');
    tbody.innerHTML = '';

    // Calculate teacher workload
    const teacherLoad = {};
    analyticsData.timetable.forEach(entry => {
        if (entry.teacher) {
            teacherLoad[entry.teacher.id] = (teacherLoad[entry.teacher.id] || 0) + 1;
        }
    });

    analyticsData.teachers.forEach(teacher => {
        const assigned = teacherLoad[teacher.id] || 0;
        const maxHours = teacher.max_hours_per_week || 20;
        const percentage = ((assigned / maxHours) * 100).toFixed(0);

        let statusClass = 'low';
        let statusText = 'Normal';
        if (percentage >= 80) {
            statusClass = 'high';
            statusText = 'Overloaded';
        } else if (percentage >= 60) {
            statusClass = 'medium';
            statusText = 'Busy';
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${teacher.name}</strong></td>
            <td>${assigned} periods</td>
            <td>${maxHours} periods</td>
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="progress-bar" style="flex: 1;">
                        <div class="progress-fill ${statusClass}" style="width: ${percentage}%"></div>
                    </div>
                    <span style="min-width: 45px; text-align: right;">${percentage}%</span>
                </div>
            </td>
            <td>
                <span style="padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; 
                      background: ${statusClass === 'high' ? '#fee2e2' : statusClass === 'medium' ? '#fef3c7' : '#d1fae5'};
                      color: ${statusClass === 'high' ? '#991b1b' : statusClass === 'medium' ? '#92400e' : '#065f46'};">
                    ${statusText}
                </span>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Refresh chart
function refreshChart(chartName) {
    if (chartName === 'teacherChart') {
        createTeacherChart();
    } else if (chartName === 'roomChart') {
        createRoomChart();
    }
}

// Export to PDF
function exportToPDF() {
    alert('PDF export functionality will be implemented with a library like jsPDF.\n\nFor now, you can use the Print button to save as PDF from your browser.');
}

// Export to Excel
function exportToExcel() {
    // Create CSV data
    let csv = 'Teacher Name,Assigned Periods,Max Capacity,Workload %,Status\n';
    
    const teacherLoad = {};
    analyticsData.timetable.forEach(entry => {
        if (entry.teacher) {
            teacherLoad[entry.teacher.id] = (teacherLoad[entry.teacher.id] || 0) + 1;
        }
    });

    analyticsData.teachers.forEach(teacher => {
        const assigned = teacherLoad[teacher.id] || 0;
        const maxHours = teacher.max_hours_per_week || 20;
        const percentage = ((assigned / maxHours) * 100).toFixed(0);
        let status = percentage >= 80 ? 'Overloaded' : percentage >= 60 ? 'Busy' : 'Normal';
        
        csv += `"${teacher.name}",${assigned},${maxHours},${percentage}%,${status}\n`;
    });

    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'timetable_report_' + new Date().toISOString().split('T')[0] + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initReports);
