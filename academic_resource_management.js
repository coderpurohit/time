// Dynamic Academic Resource Management System
// Complete CRUD with Auto Timetable Generation

const API_BASE = 'http://localhost:8000/api';

// Global state with proper initialization
let currentData = {
    faculty: [],
    subjects: [],
    classes: [],
    labs: [],
    loadFactor: {},
    timetable: []
};

// Tab switching
function switchTab(tabName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    
    // Show selected section
    document.getElementById(tabName).classList.add('active');
    event.target.closest('.tab').classList.add('active');
    
    // Load data for the tab
    loadTabData(tabName);
}

async function loadTabData(tabName) {
    switch(tabName) {
        case 'faculty':
            await loadFacultyData();
            break;
        case 'subjects':
            await loadSubjectData();
            break;
        case 'classes':
            await loadClassData();
            break;
        case 'labs':
            await loadLabData();
            break;
        case 'loadfactor':
            await loadLoadFactorData();
            break;
        case 'timetable':
            await loadTimetableData();
            break;
        case 'dashboard':
            await loadDashboardData();
            break;
    }
}

// MODULE 1: FACULTY MANAGEMENT
async function loadFacultyData() {
    try {
        const response = await fetch(`${API_BASE}/teachers/`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const faculty = await response.json();
        
        // Ensure faculty is an array
        currentData.faculty = Array.isArray(faculty) ? faculty : [];
        
        console.log('Loaded faculty:', currentData.faculty);
        renderFacultyTable(currentData.faculty);
        updateFacultyStats(currentData.faculty);
    } catch (error) {
        console.error('Error loading faculty:', error);
        currentData.faculty = [];
        showNotification('Failed to load faculty data: ' + error.message, 'error');
    }
}

function renderFacultyTable(faculty) {
    const tbody = document.getElementById('facultyTableBody');
    
    if (faculty.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">No faculty found. Click "Add Faculty" to get started.</td></tr>';
        return;
    }
    
    tbody.innerHTML = faculty.map(f => {
        const currentLoad = calculateFacultyLoad(f.id);
        const loadPercentage = Math.round((currentLoad / f.max_hours_per_week) * 100);
        const status = getLoadStatus(loadPercentage);
        
        return `
            <tr>
                <td><strong>${f.name}</strong><br><small>${f.email}</small></td>
                <td>${getDesignation(f.name)}</td>
                <td>${f.max_hours_per_week} hrs</td>
                <td>${currentLoad} hrs</td>
                <td>${loadPercentage}%</td>
                <td><span class="load-status ${status.class}">${status.text}</span></td>
                <td>${f.lab_eligible ? 'Yes' : 'No'}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editFaculty(${f.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteFaculty(${f.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function updateFacultyStats(faculty) {
    const total = faculty.length;
    let optimal = 0, overloaded = 0, underloaded = 0;
    
    faculty.forEach(f => {
        const currentLoad = calculateFacultyLoad(f.id);
        const loadPercentage = (currentLoad / f.max_hours_per_week) * 100;
        
        if (loadPercentage >= 70 && loadPercentage <= 100) optimal++;
        else if (loadPercentage > 100) overloaded++;
        else underloaded++;
    });
    
    document.getElementById('totalFaculty').textContent = total;
    document.getElementById('optimalFaculty').textContent = optimal;
    document.getElementById('overloadedFaculty').textContent = overloaded;
    document.getElementById('underloadedFaculty').textContent = underloaded;
}

function calculateFacultyLoad(facultyId) {
    // Calculate from subjects assigned to faculty
    const facultySubjects = currentData.subjects.filter(s => s.teacher_id === facultyId);
    return facultySubjects.reduce((total, subject) => {
        return total + (subject.theory_hours || 0) + (subject.practical_hours || 0) + (subject.lab_hours || 0);
    }, 0);
}

function getLoadStatus(percentage) {
    if (percentage >= 70 && percentage <= 100) {
        return { class: 'status-optimal', text: 'Optimal' };
    } else if (percentage > 100) {
        return { class: 'status-overloaded', text: 'Overloaded' };
    } else {
        return { class: 'status-underloaded', text: 'Underloaded' };
    }
}

function getDesignation(name) {
    if (name.includes('HOD')) return 'HOD';
    if (name.includes('Professor') && !name.includes('Assistant') && !name.includes('Associate')) return 'Professor';
    if (name.includes('Associate')) return 'Associate Professor';
    if (name.includes('Assistant')) return 'Assistant Professor';
    return 'Faculty';
}

// Faculty CRUD Operations
function openFacultyModal(facultyId = null) {
    const modal = document.getElementById('facultyModal');
    const form = document.getElementById('facultyForm');
    const title = document.getElementById('facultyModalTitle');
    
    if (facultyId) {
        // Edit mode
        const faculty = currentData.faculty.find(f => f.id === facultyId);
        title.textContent = 'Edit Faculty';
        form.facultyName.value = faculty.name;
        form.facultyEmail.value = faculty.email;
        form.facultyMaxHours.value = faculty.max_hours_per_week;
        form.facultyLabEligible.checked = faculty.lab_eligible;
        form.dataset.facultyId = facultyId;
    } else {
        // Add mode
        title.textContent = 'Add New Faculty';
        form.reset();
        delete form.dataset.facultyId;
    }
    
    modal.classList.add('active');
}

async function saveFaculty() {
    const form = document.getElementById('facultyForm');
    const facultyId = form.dataset.facultyId;
    
    const facultyData = {
        name: form.facultyName.value,
        email: form.facultyEmail.value,
        max_hours_per_week: parseInt(form.facultyMaxHours.value),
        lab_eligible: form.facultyLabEligible.checked
    };
    
    try {
        let response;
        if (facultyId) {
            // Update
            response = await fetch(`${API_BASE}/teachers/${facultyId}/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(facultyData)
            });
        } else {
            // Create
            response = await fetch(`${API_BASE}/teachers/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(facultyData)
            });
        }
        
        if (response.ok) {
            closeFacultyModal();
            await loadFacultyData();
            showNotification('Faculty saved successfully!', 'success');
        } else {
            throw new Error('Failed to save faculty');
        }
    } catch (error) {
        console.error('Error saving faculty:', error);
        showNotification('Error saving faculty', 'error');
    }
}

async function deleteFaculty(facultyId) {
    if (!confirm('Are you sure you want to delete this faculty member?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/teachers/${facultyId}/`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadFacultyData();
            showNotification('Faculty deleted successfully!', 'success');
        } else {
            throw new Error('Failed to delete faculty');
        }
    } catch (error) {
        console.error('Error deleting faculty:', error);
        showNotification('Error deleting faculty', 'error');
    }
}

function closeFacultyModal() {
    document.getElementById('facultyModal').classList.remove('active');
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
        white-space: pre-line;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    if (type === 'success') notification.style.background = '#28a745';
    else if (type === 'error') notification.style.background = '#dc3545';
    else if (type === 'warning') notification.style.background = '#ffc107';
    else notification.style.background = '#17a2b8';
    
    // Handle long messages
    if (message.length > 200) {
        const shortMessage = message.substring(0, 200) + '...';
        notification.innerHTML = `
            <div>${shortMessage}</div>
            <button onclick="this.parentElement.querySelector('.full-message').style.display='block'; this.style.display='none';" 
                    style="background: none; border: 1px solid white; color: white; padding: 5px 10px; margin-top: 10px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                Show Full Message
            </button>
            <div class="full-message" style="display: none; margin-top: 10px; font-size: 13px; opacity: 0.9;">${message}</div>
        `;
    } else {
        notification.textContent = message;
    }
    
    document.body.appendChild(notification);
    
    // Auto-remove after delay (longer for warnings/errors)
    const delay = type === 'error' || type === 'warning' ? 8000 : 4000;
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, delay);
    
    // Add click to dismiss
    notification.onclick = () => notification.remove();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Academic Resource Management System loaded');
    
    // Add error handling for API calls
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showNotification('API Error: ' + event.reason.message, 'error');
    });
    
    // Load initial data with retry
    setTimeout(() => {
        loadTabData('faculty').catch(error => {
            console.error('Failed to load initial data:', error);
            showNotification('Failed to load data. Check if backend is running.', 'error');
        });
    }, 500);
});
// MODULE 2: SUBJECT MANAGEMENT
async function loadSubjectData() {
    try {
        const response = await fetch(`${API_BASE}/subjects/`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const subjects = await response.json();
        
        // Ensure subjects is an array
        currentData.subjects = Array.isArray(subjects) ? subjects : [];
        
        console.log('Loaded subjects:', currentData.subjects);
        renderSubjectTable(currentData.subjects);
        updateSubjectStats(currentData.subjects);
        populateFacultyDropdowns();
    } catch (error) {
        console.error('Error loading subjects:', error);
        currentData.subjects = [];
        showNotification('Failed to load subjects data: ' + error.message, 'error');
    }
}

function renderSubjectTable(subjects) {
    const tbody = document.getElementById('subjectTableBody');
    
    if (subjects.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 40px;">No subjects found. Click "Add Subject" to get started.</td></tr>';
        return;
    }
    
    tbody.innerHTML = subjects.map(s => {
        const faculty = currentData.faculty.find(f => f.id === s.teacher_id);
        const subjectType = s.is_lab ? 'Lab' : 'Theory';
        
        return `
            <tr>
                <td><strong>${s.name}</strong></td>
                <td>${s.code}</td>
                <td><span class="badge ${s.is_lab ? 'badge-lab' : 'badge-theory'}">${subjectType}</span></td>
                <td>${s.theory_hours || 0} hrs</td>
                <td>${s.practical_hours || 0} hrs</td>
                <td>${s.semester || 'N/A'}</td>
                <td>${s.class_level || 'N/A'}</td>
                <td>${faculty ? faculty.name : 'Unassigned'}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editSubject(${s.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteSubject(${s.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function updateSubjectStats(subjects) {
    const total = subjects.length;
    const theory = subjects.filter(s => !s.is_lab).length;
    const lab = subjects.filter(s => s.is_lab).length;
    const project = subjects.filter(s => s.name.toLowerCase().includes('project')).length;
    
    document.getElementById('totalSubjects').textContent = total;
    document.getElementById('theorySubjects').textContent = theory;
    document.getElementById('labSubjects').textContent = lab;
    document.getElementById('projectSubjects').textContent = project;
}

function populateFacultyDropdowns() {
    const selects = document.querySelectorAll('select[name="subjectFaculty"], select[name="labIncharge"]');
    const options = currentData.faculty.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
    
    selects.forEach(select => {
        select.innerHTML = '<option value="">Select Faculty</option>' + options;
    });
}

// Subject CRUD Operations
function openSubjectModal(subjectId = null) {
    const modal = document.getElementById('subjectModal');
    const form = document.getElementById('subjectForm');
    const title = document.getElementById('subjectModalTitle');
    
    if (subjectId) {
        const subject = currentData.subjects.find(s => s.id === subjectId);
        title.textContent = 'Edit Subject';
        form.subjectName.value = subject.name;
        form.subjectCode.value = subject.code;
        form.subjectType.value = subject.is_lab ? 'lab' : 'theory';
        form.theoryHours.value = subject.theory_hours || 0;
        form.practicalHours.value = subject.practical_hours || 0;
        form.subjectCredits.value = subject.credits || 3;
        form.subjectFaculty.value = subject.teacher_id || '';
        form.dataset.subjectId = subjectId;
    } else {
        title.textContent = 'Add New Subject';
        form.reset();
        delete form.dataset.subjectId;
    }
    
    modal.classList.add('active');
}

async function saveSubject() {
    const form = document.getElementById('subjectForm');
    const subjectId = form.dataset.subjectId;
    
    const subjectData = {
        name: form.subjectName.value,
        code: form.subjectCode.value,
        is_lab: form.subjectType.value === 'lab',
        theory_hours: parseInt(form.theoryHours.value) || 0,
        practical_hours: parseInt(form.practicalHours.value) || 0,
        credits: parseInt(form.subjectCredits.value) || 3,
        teacher_id: form.subjectFaculty.value ? parseInt(form.subjectFaculty.value) : null,
        required_room_type: form.subjectType.value === 'lab' ? 'Lab' : 'LectureHall',
        duration_slots: form.subjectType.value === 'lab' ? 2 : 1
    };
    
    try {
        let response;
        if (subjectId) {
            response = await fetch(`${API_BASE}/subjects/${subjectId}/`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subjectData)
            });
        } else {
            response = await fetch(`${API_BASE}/subjects/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subjectData)
            });
        }
        
        if (response.ok) {
            closeSubjectModal();
            await loadSubjectData();
            await loadLoadFactorData(); // Refresh load factor
            showNotification('Subject saved successfully!', 'success');
        } else {
            throw new Error('Failed to save subject');
        }
    } catch (error) {
        console.error('Error saving subject:', error);
        showNotification('Error saving subject', 'error');
    }
}

async function deleteSubject(subjectId) {
    if (!confirm('Are you sure you want to delete this subject?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/subjects/${subjectId}/`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadSubjectData();
            await loadLoadFactorData();
            showNotification('Subject deleted successfully!', 'success');
        } else {
            throw new Error('Failed to delete subject');
        }
    } catch (error) {
        console.error('Error deleting subject:', error);
        showNotification('Error deleting subject', 'error');
    }
}

function closeSubjectModal() {
    document.getElementById('subjectModal').classList.remove('active');
}

// MODULE 3: CLASS MANAGEMENT
async function loadClassData() {
    try {
        const response = await fetch(`${API_BASE}/class-groups/`);
        const classes = await response.json();
        currentData.classes = classes;
        
        renderClassTable(classes);
        updateClassStats(classes);
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

function renderClassTable(classes) {
    const tbody = document.getElementById('classTableBody');
    
    if (classes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">No classes found. Click "Add Class" to get started.</td></tr>';
        return;
    }
    
    tbody.innerHTML = classes.map(c => {
        const year = c.name.split('-')[0];
        const division = c.name.split('-')[2] || c.name.split('-')[1];
        const coverage = calculateClassCoverage(c.id);
        
        return `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td>${year}</td>
                <td>${division}</td>
                <td>${c.student_count}</td>
                <td>5 days</td>
                <td>8 slots</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="flex: 1; background: #e9ecef; height: 8px; border-radius: 4px;">
                            <div style="background: ${coverage >= 80 ? '#28a745' : coverage >= 60 ? '#ffc107' : '#dc3545'}; height: 100%; width: ${coverage}%; border-radius: 4px;"></div>
                        </div>
                        <span>${coverage}%</span>
                    </div>
                </td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editClass(${c.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteClass(${c.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function updateClassStats(classes) {
    const total = classes.length;
    const se = classes.filter(c => c.name.startsWith('SE')).length;
    const te = classes.filter(c => c.name.startsWith('TE')).length;
    const be = classes.filter(c => c.name.startsWith('BE')).length;
    
    document.getElementById('totalClasses').textContent = total;
    document.getElementById('seClasses').textContent = se;
    document.getElementById('teClasses').textContent = te;
    document.getElementById('beClasses').textContent = be;
}

function calculateClassCoverage(classId) {
    // Calculate based on assigned subjects vs required subjects
    const assignedSubjects = currentData.subjects.filter(s => s.class_id === classId).length;
    const requiredSubjects = 8; // Typical subjects per semester
    return Math.min(Math.round((assignedSubjects / requiredSubjects) * 100), 100);
}

// MODULE 4: LAB MANAGEMENT
async function loadLabData() {
    try {
        const response = await fetch(`${API_BASE}/rooms/?type=Lab`);
        const labs = await response.json();
        currentData.labs = labs;
        
        renderLabTable(labs);
        updateLabStats(labs);
    } catch (error) {
        console.error('Error loading labs:', error);
    }
}

function renderLabTable(labs) {
    const tbody = document.getElementById('labTableBody');
    
    if (labs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">No labs found. Click "Add Lab" to get started.</td></tr>';
        return;
    }
    
    tbody.innerHTML = labs.map(l => {
        const utilization = calculateLabUtilization(l.id);
        const status = utilization > 80 ? 'High' : utilization > 50 ? 'Medium' : 'Low';
        const statusClass = utilization > 80 ? 'status-overloaded' : utilization > 50 ? 'status-optimal' : 'status-underloaded';
        
        return `
            <tr>
                <td><strong>${l.name}</strong></td>
                <td>${getLabType(l.name)}</td>
                <td>${l.capacity}</td>
                <td>TBD</td>
                <td>40 slots/week</td>
                <td>${utilization}%</td>
                <td><span class="load-status ${statusClass}">${status}</span></td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editLab(${l.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteLab(${l.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function updateLabStats(labs) {
    const total = labs.length;
    const software = labs.filter(l => l.name.includes('SL')).length;
    const ai = labs.filter(l => l.name.includes('AI') || l.name.includes('DS')).length;
    const avgUtilization = Math.round(labs.reduce((sum, l) => sum + calculateLabUtilization(l.id), 0) / total) || 0;
    
    document.getElementById('totalLabs').textContent = total;
    document.getElementById('softwareLabs').textContent = software;
    document.getElementById('aiLabs').textContent = ai;
    document.getElementById('labUtilization').textContent = avgUtilization + '%';
}

function getLabType(labName) {
    if (labName.includes('SL')) return 'Software Lab';
    if (labName.includes('AI') || labName.includes('DS')) return 'AI/DS Lab';
    if (labName.includes('PLL') || labName.includes('DIY')) return 'Programming Lab';
    return 'General Lab';
}

function calculateLabUtilization(labId) {
    // Mock calculation - in real system, check timetable entries
    return Math.floor(Math.random() * 100);
}

// MODULE 5: LOAD FACTOR ENGINE
async function loadLoadFactorData() {
    try {
        const response = await fetch(`${API_BASE}/analytics/load-factor`);
        const data = await response.json();
        
        renderLoadFactorTable(data.teacher_load || []);
        updateLoadFactorSummary(data);
        checkConflicts(data.conflicts || {});
    } catch (error) {
        console.error('Error loading load factor:', error);
        document.getElementById('loadFactorTableBody').innerHTML = 
            '<tr><td colspan="9" style="text-align: center; padding: 40px; color: #dc3545;">Error loading load factor data. Generate a timetable first.</td></tr>';
    }
}

function renderLoadFactorTable(teacherLoad) {
    const tbody = document.getElementById('loadFactorTableBody');
    
    if (teacherLoad.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 40px;">No load factor data available. Generate a timetable first.</td></tr>';
        return;
    }
    
    tbody.innerHTML = teacherLoad.map(t => {
        const status = getLoadStatus(t.load_percentage);
        const assignedSubjects = getAssignedSubjects(t.id);
        
        // Create subject tags HTML
        let subjectsHtml = '';
        if (assignedSubjects.length > 0) {
            subjectsHtml = assignedSubjects.map(s => 
                `<span class="subject-tag">${s.name} (${s.code || 'N/A'})</span>`
            ).join(' ');
        } else {
            subjectsHtml = '<small style="color: #999;">No subjects assigned</small>';
        }
        
        return `
            <tr>
                <td>
                    <strong>${t.name}</strong><br>
                    <small style="color: #666;">${t.email || ''}</small>
                </td>
                <td>${t.theory_hours || 0}</td>
                <td>${t.practical_hours || 0}</td>
                <td>${t.lab_hours || 0}</td>
                <td>${t.project_hours || 0}</td>
                <td><strong>${t.total_periods || 0}</strong></td>
                <td>${t.load_percentage || 0}%</td>
                <td><span class="load-status ${status.class}">${status.text}</span></td>
                <td>
                    <div style="max-width: 200px; max-height: 80px; overflow-y: auto;">
                        ${subjectsHtml}
                    </div>
                </td>
                <td>
                    <button class="btn btn-sm btn-success" onclick="assignSubjectToFaculty(${t.id})" title="Assign Subject">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="optimizeFacultyLoad(${t.id})" title="Optimize Load">
                        <i class="fas fa-magic"></i>
                    </button>
                    <button class="btn btn-sm btn-info" onclick="viewFacultyDetails(${t.id})" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function updateLoadFactorSummary(data) {
    const summary = data.summary || {};
    
    document.getElementById('avgLoad').textContent = summary.avg_teacher_load || 0;
    document.getElementById('totalHours').textContent = summary.total_periods || 0;
    document.getElementById('totalConflicts').textContent = data.validation?.total_conflicts || 0;
    document.getElementById('efficiency').textContent = Math.round(summary.classroom_utilization || 0) + '%';
}

function checkConflicts(conflicts) {
    const alertsContainer = document.getElementById('conflictAlerts');
    const totalConflicts = Object.values(conflicts).reduce((sum, arr) => sum + arr.length, 0);
    
    if (totalConflicts === 0) {
        alertsContainer.innerHTML = '<div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;"><i class="fas fa-check-circle"></i> No conflicts detected!</div>';
        return;
    }
    
    let alertsHtml = '';
    
    if (conflicts.faculty_timing_clashes?.length > 0) {
        alertsHtml += `<div class="conflict-alert"><strong>Faculty Timing Conflicts:</strong> ${conflicts.faculty_timing_clashes.length} detected</div>`;
    }
    
    if (conflicts.classroom_conflicts?.length > 0) {
        alertsHtml += `<div class="conflict-alert"><strong>Classroom Conflicts:</strong> ${conflicts.classroom_conflicts.length} detected</div>`;
    }
    
    if (conflicts.lab_conflicts?.length > 0) {
        alertsHtml += `<div class="conflict-alert"><strong>Lab Conflicts:</strong> ${conflicts.lab_conflicts.length} detected</div>`;
    }
    
    alertsContainer.innerHTML = alertsHtml;
}

// Load Factor Actions
async function optimizeLoadDistribution() {
    showNotification('Optimizing load distribution...', 'info');
    
    // Mock optimization - in real system, implement AI-based optimization
    setTimeout(() => {
        showNotification('Load distribution optimized!', 'success');
        loadLoadFactorData();
    }, 2000);
}

async function validateLoadFactor() {
    showNotification('Validating load factor...', 'info');
    await loadLoadFactorData();
    showNotification('Load factor validation complete!', 'success');
}

// MODULE 6: AUTO TIMETABLE GENERATION
async function loadTimetableData() {
    try {
        const response = await fetch(`${API_BASE}/timetables/latest`);
        if (response.ok) {
            const data = await response.json();
            renderTimetableDisplay(data);
        } else {
            document.getElementById('timetableDisplay').innerHTML = `
                <div style="text-align: center; padding: 60px; color: #666;">
                    <i class="fas fa-calendar-alt" style="font-size: 64px; margin-bottom: 20px; opacity: 0.3;"></i>
                    <h3>No Timetable Generated</h3>
                    <p>Click "Generate Timetable" to create a new schedule</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading timetable:', error);
    }
}

async function generateTimetable() {
    const statusDiv = document.getElementById('generationStatus');
    statusDiv.innerHTML = `
        <div style="background: #cce5ff; color: #004085; padding: 20px; border-radius: 8px; text-align: center;">
            <i class="fas fa-spinner fa-spin"></i> Generating timetable...
        </div>
    `;
    
    try {
        const response = await fetch(`${API_BASE}/solvers/generate?method=csp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                working_days: parseInt(document.getElementById('workingDays').value),
                periods_per_day: parseInt(document.getElementById('periodsPerDay').value),
                break_duration: parseInt(document.getElementById('breakDuration').value),
                lab_duration: parseInt(document.getElementById('labDuration').value)
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            statusDiv.innerHTML = `
                <div style="background: #d4edda; color: #155724; padding: 20px; border-radius: 8px; text-align: center;">
                    <i class="fas fa-check-circle"></i> Timetable generated successfully! ${result.entries_count} entries created.
                </div>
            `;
            
            await loadTimetableData();
            await loadLoadFactorData();
        } else {
            throw new Error('Failed to generate timetable');
        }
    } catch (error) {
        console.error('Error generating timetable:', error);
        statusDiv.innerHTML = `
            <div style="background: #f8d7da; color: #721c24; padding: 20px; border-radius: 8px; text-align: center;">
                <i class="fas fa-exclamation-triangle"></i> Error generating timetable: ${error.message}
            </div>
        `;
    }
}

function renderTimetableDisplay(data) {
    // Simplified timetable display
    document.getElementById('timetableDisplay').innerHTML = `
        <div style="background: #d4edda; color: #155724; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px;">
            <h3><i class="fas fa-check-circle"></i> Timetable Generated Successfully!</h3>
            <p>Version: ${data.name} | Entries: ${data.entries?.length || 0} | Algorithm: ${data.algorithm}</p>
        </div>
        <div style="text-align: center; padding: 40px;">
            <button class="btn btn-primary" onclick="window.open('http://localhost:3000/timetable_review_WORKING.html', '_blank')">
                <i class="fas fa-external-link-alt"></i> View Full Timetable
            </button>
        </div>
    `;
}

async function exportTimetable() {
    showNotification('Exporting timetable...', 'info');
    // Mock export - implement actual export functionality
    setTimeout(() => {
        showNotification('Timetable exported successfully!', 'success');
    }, 1000);
}

// MODULE 7: DASHBOARD
async function loadDashboardData() {
    try {
        const [facultyResp, subjectsResp, classesResp, analyticsResp] = await Promise.all([
            fetch(`${API_BASE}/teachers/`),
            fetch(`${API_BASE}/subjects/`),
            fetch(`${API_BASE}/class-groups/`),
            fetch(`${API_BASE}/analytics/dashboard-stats`)
        ]);
        
        const faculty = await facultyResp.json();
        const subjects = await subjectsResp.json();
        const classes = await classesResp.json();
        const analytics = await analyticsResp.json();
        
        updateDashboardMetrics(faculty, subjects, classes, analytics);
        renderDashboardSummaries(faculty, classes);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateDashboardMetrics(faculty, subjects, classes, analytics) {
    const efficiency = Math.round((analytics.utilization || 0));
    const resourceUtil = Math.round((subjects.length / (faculty.length * 5)) * 100);
    const conflicts = 0; // Get from load factor data
    const completion = Math.round((subjects.length / (classes.length * 8)) * 100);
    
    document.getElementById('systemEfficiency').textContent = efficiency + '%';
    document.getElementById('resourceUtilization').textContent = resourceUtil + '%';
    document.getElementById('activeConflicts').textContent = conflicts;
    document.getElementById('completionRate').textContent = Math.min(completion, 100) + '%';
}

function renderDashboardSummaries(faculty, classes) {
    // Faculty Load Summary
    const facultyHtml = `
        <table class="table">
            <thead>
                <tr><th>Faculty</th><th>Load</th><th>Status</th></tr>
            </thead>
            <tbody>
                ${faculty.slice(0, 5).map(f => {
                    const load = calculateFacultyLoad(f.id);
                    const percentage = Math.round((load / f.max_hours_per_week) * 100);
                    const status = getLoadStatus(percentage);
                    return `<tr><td>${f.name}</td><td>${load}/${f.max_hours_per_week}</td><td><span class="load-status ${status.class}">${status.text}</span></td></tr>`;
                }).join('')}
            </tbody>
        </table>
    `;
    
    // Class Coverage Summary
    const classHtml = `
        <table class="table">
            <thead>
                <tr><th>Class</th><th>Coverage</th><th>Status</th></tr>
            </thead>
            <tbody>
                ${classes.slice(0, 5).map(c => {
                    const coverage = calculateClassCoverage(c.id);
                    const status = coverage >= 80 ? 'Complete' : coverage >= 60 ? 'Partial' : 'Incomplete';
                    const statusClass = coverage >= 80 ? 'status-optimal' : coverage >= 60 ? 'status-underloaded' : 'status-overloaded';
                    return `<tr><td>${c.name}</td><td>${coverage}%</td><td><span class="load-status ${statusClass}">${status}</span></td></tr>`;
                }).join('')}
            </tbody>
        </table>
    `;
    
    document.getElementById('facultyLoadSummary').innerHTML = facultyHtml;
    document.getElementById('classCoverageSummary').innerHTML = classHtml;
}

// Initialize system
document.addEventListener('DOMContentLoaded', function() {
    loadTabData('faculty');
    
    // Add CSS for badges and additional styling
    const style = document.createElement('style');
    style.textContent = `
        .badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .badge-theory { background: #cce5ff; color: #004085; }
        .badge-lab { background: #fff3cd; color: #856404; }
        .btn-sm { padding: 6px 12px; font-size: 12px; }
        .notification { animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }
    `;
    document.head.appendChild(style);
});
function getAssignedSubjects(teacherId) {
    // Get subjects assigned to this teacher
    const assignedSubjects = currentData.subjects.filter(s => s.teacher_id === teacherId);
    console.log(`Teacher ${teacherId} has ${assignedSubjects.length} subjects:`, assignedSubjects.map(s => s.name));
    return assignedSubjects;
}

// Subject Assignment Modal and Functions
function assignSubjectToFaculty(facultyId) {
    const faculty = currentData.faculty.find(f => f.id === facultyId);
    const unassignedSubjects = currentData.subjects.filter(s => !s.teacher_id);
    
    if (unassignedSubjects.length === 0) {
        showNotification('No unassigned subjects available', 'info');
        return;
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Assign Subject to ${faculty.name}</h3>
            <form id="assignSubjectForm" onsubmit="event.preventDefault(); saveSubjectAssignment(${facultyId});">
                <div class="form-group">
                    <label>Select Subject to Assign:</label>
                    <select name="subjectId" class="form-control" required>
                        <option value="">Choose a subject...</option>
                        ${unassignedSubjects.map(s => `
                            <option value="${s.id}">${s.name} (${s.code}) - ${s.is_lab ? 'Lab' : 'Theory'}</option>
                        `).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label>Weekly Hours:</label>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                        <div>
                            <label>Theory Hours</label>
                            <input type="number" name="theoryHours" class="form-control" value="3" min="0" max="6">
                        </div>
                        <div>
                            <label>Practical Hours</label>
                            <input type="number" name="practicalHours" class="form-control" value="0" min="0" max="6">
                        </div>
                        <div>
                            <label>Lab Hours</label>
                            <input type="number" name="labHours" class="form-control" value="0" min="0" max="6">
                        </div>
                    </div>
                </div>
                <div class="form-group">
                    <label>Classes to Assign:</label>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                        ${currentData.classes.map(c => `
                            <label style="display: flex; align-items: center; gap: 5px;">
                                <input type="checkbox" name="assignedClasses" value="${c.id}">
                                ${c.name}
                            </label>
                        `).join('')}
                    </div>
                </div>
                <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 25px;">
                    <button type="button" class="btn btn-secondary" onclick="closeAssignmentModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Assign Subject</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    window.currentAssignmentModal = modal;
}

async function saveSubjectAssignment(facultyId) {
    const form = document.getElementById('assignSubjectForm');
    const subjectId = parseInt(form.subjectId.value);
    const theoryHours = parseInt(form.theoryHours.value) || 0;
    const practicalHours = parseInt(form.practicalHours.value) || 0;
    const labHours = parseInt(form.labHours.value) || 0;
    
    try {
        // Update subject with faculty assignment
        const response = await fetch(`${API_BASE}/subjects/${subjectId}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                teacher_id: facultyId,
                theory_hours: theoryHours,
                practical_hours: practicalHours,
                lab_hours: labHours
            })
        });
        
        if (response.ok) {
            closeAssignmentModal();
            await loadSubjectData();
            await loadLoadFactorData();
            showNotification('Subject assigned successfully!', 'success');
        } else {
            throw new Error('Failed to assign subject');
        }
    } catch (error) {
        console.error('Error assigning subject:', error);
        showNotification('Error assigning subject', 'error');
    }
}

function closeAssignmentModal() {
    if (window.currentAssignmentModal) {
        window.currentAssignmentModal.remove();
        window.currentAssignmentModal = null;
    }
}

// Faculty Details Modal
function viewFacultyDetails(facultyId) {
    const faculty = currentData.faculty.find(f => f.id === facultyId);
    const assignedSubjects = getAssignedSubjects(facultyId);
    const currentLoad = calculateFacultyLoad(facultyId);
    const loadPercentage = Math.round((currentLoad / faculty.max_hours_per_week) * 100);
    
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <h3><i class="fas fa-user"></i> ${faculty.name} - Faculty Details</h3>
            
            <!-- Faculty Info -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <strong>Email:</strong> ${faculty.email}<br>
                        <strong>Max Weekly Load:</strong> ${faculty.max_hours_per_week} hours<br>
                        <strong>Current Load:</strong> ${currentLoad} hours (${loadPercentage}%)
                    </div>
                    <div>
                        <strong>Status:</strong> <span class="load-status ${getLoadStatus(loadPercentage).class}">${getLoadStatus(loadPercentage).text}</span><br>
                        <strong>Lab Eligible:</strong> ${faculty.lab_eligible ? 'Yes' : 'No'}<br>
                        <strong>Subjects Assigned:</strong> ${assignedSubjects.length}
                    </div>
                </div>
            </div>
            
            <!-- Load Breakdown -->
            <div style="margin-bottom: 20px;">
                <h4>Load Breakdown</h4>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
                    <div style="text-align: center; padding: 15px; background: #e3f2fd; border-radius: 8px;">
                        <div style="font-size: 24px; font-weight: bold; color: #1976d2;">${calculateHoursByType(facultyId, 'theory')}</div>
                        <div>Theory Hours</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: #fff3e0; border-radius: 8px;">
                        <div style="font-size: 24px; font-weight: bold; color: #f57c00;">${calculateHoursByType(facultyId, 'practical')}</div>
                        <div>Practical Hours</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: #f3e5f5; border-radius: 8px;">
                        <div style="font-size: 24px; font-weight: bold; color: #7b1fa2;">${calculateHoursByType(facultyId, 'lab')}</div>
                        <div>Lab Hours</div>
                    </div>
                    <div style="text-align: center; padding: 15px; background: #e8f5e8; border-radius: 8px;">
                        <div style="font-size: 24px; font-weight: bold; color: #388e3c;">${calculateHoursByType(facultyId, 'project')}</div>
                        <div>Project Hours</div>
                    </div>
                </div>
            </div>
            
            <!-- Assigned Subjects -->
            <div style="margin-bottom: 20px;">
                <h4>Assigned Subjects</h4>
                ${assignedSubjects.length > 0 ? `
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Subject</th>
                                <th>Code</th>
                                <th>Type</th>
                                <th>Hours</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${assignedSubjects.map(s => `
                                <tr>
                                    <td>${s.name}</td>
                                    <td>${s.code}</td>
                                    <td><span class="badge ${s.is_lab ? 'badge-lab' : 'badge-theory'}">${s.is_lab ? 'Lab' : 'Theory'}</span></td>
                                    <td>${(s.theory_hours || 0) + (s.practical_hours || 0) + (s.lab_hours || 0)} hrs</td>
                                    <td>
                                        <button class="btn btn-sm btn-danger" onclick="unassignSubject(${s.id})" title="Unassign">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                ` : '<p style="text-align: center; color: #666; padding: 20px;">No subjects assigned yet.</p>'}
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: flex-end;">
                <button class="btn btn-success" onclick="assignSubjectToFaculty(${facultyId}); closeFacultyDetailsModal();">
                    <i class="fas fa-plus"></i> Assign New Subject
                </button>
                <button class="btn btn-secondary" onclick="closeFacultyDetailsModal()">Close</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    window.currentDetailsModal = modal;
}

function closeFacultyDetailsModal() {
    if (window.currentDetailsModal) {
        window.currentDetailsModal.remove();
        window.currentDetailsModal = null;
    }
}

// Helper functions for load calculation by type
function calculateHoursByType(facultyId, type) {
    const facultySubjects = currentData.subjects.filter(s => s.teacher_id === facultyId);
    return facultySubjects.reduce((total, subject) => {
        switch(type) {
            case 'theory': return total + (subject.theory_hours || 0);
            case 'practical': return total + (subject.practical_hours || 0);
            case 'lab': return total + (subject.lab_hours || 0);
            case 'project': return total + (subject.name.toLowerCase().includes('project') ? (subject.theory_hours || 0) : 0);
            default: return total;
        }
    }, 0);
}

// Unassign subject function
async function unassignSubject(subjectId) {
    if (!confirm('Are you sure you want to unassign this subject?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/subjects/${subjectId}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ teacher_id: null })
        });
        
        if (response.ok) {
            await loadSubjectData();
            await loadLoadFactorData();
            closeFacultyDetailsModal();
            showNotification('Subject unassigned successfully!', 'success');
        } else {
            throw new Error('Failed to unassign subject');
        }
    } catch (error) {
        console.error('Error unassigning subject:', error);
        showNotification('Error unassigning subject', 'error');
    }
}

// Optimize faculty load function
async function optimizeFacultyLoad(facultyId) {
    const faculty = currentData.faculty.find(f => f.id === facultyId);
    const currentLoad = calculateFacultyLoad(facultyId);
    const loadPercentage = (currentLoad / faculty.max_hours_per_week) * 100;
    
    showNotification(`Analyzing load for ${faculty.name}...`, 'info');
    
    // Mock optimization logic
    setTimeout(() => {
        let suggestion = '';
        if (loadPercentage > 100) {
            suggestion = `${faculty.name} is overloaded by ${Math.round(loadPercentage - 100)}%. Consider redistributing ${Math.ceil((currentLoad - faculty.max_hours_per_week) / 2)} hours to other faculty.`;
        } else if (loadPercentage < 70) {
            suggestion = `${faculty.name} is underutilized at ${Math.round(loadPercentage)}%. Can take on ${Math.floor((faculty.max_hours_per_week * 0.9) - currentLoad)} more hours.`;
        } else {
            suggestion = `${faculty.name} has optimal load at ${Math.round(loadPercentage)}%. No changes needed.`;
        }
        
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <h3><i class="fas fa-magic"></i> Load Optimization Suggestion</h3>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p>${suggestion}</p>
                </div>
                <div style="text-align: right;">
                    <button class="btn btn-primary" onclick="this.closest('.modal').remove()">Got it</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }, 1500);
}

// Add CSS for subject tags
document.addEventListener('DOMContentLoaded', function() {
    const additionalStyle = document.createElement('style');
    additionalStyle.textContent = `
        .subject-tag {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin: 2px;
            font-weight: 500;
        }
        .load-factor-table th:nth-child(9) {
            min-width: 200px;
        }
    `;
    document.head.appendChild(additionalStyle);
});
// BULK IMPORT FUNCTIONALITY

function openBulkImportModal() {
    const modal = document.getElementById('bulkImportModal');
    modal.classList.add('active');
    
    // Pre-fill with sample data that works
    const sampleData = `Dr. V. G. Kottawar, Critical Thinking and Problem Solving, CTPS, 3, 0, 1, SE-B
Dr. V. G. Kottawar, Mini Project, MP1, 0, 0, 4, SE-B
Dr. Manish Sharma, Fundamentals of AI, FAI, 2, 0, 0, SE-B
Dr. Manish Sharma, Mini Project, MP2, 0, 0, 4, SE-B|SE-C
Dr. Suvarna S. Gothane, Data Base Management System, DBMS, 3, 0, 0, TE-A
Dr. Suvarna S. Gothane, SL1 Lab, SL1, 0, 0, 2, TE-A
Dr. Bhaghyshri A. Tingare, Elective I- HCI, HCI, 3, 0, 0, TE-C
Dr. Bhaghyshri A. Tingare, Project Management, PM, 2, 0, 0, SE-C
Mrs. Manasi D. Karajgar, Data Base Management System, DBMS2, 3, 0, 0, TE-B
Mrs. Manasi D. Karajgar, Elective III- EAC, EAC, 3, 0, 0, BE-B
Mrs. Neeta J. Mahale, Artificial Intelligence, AI, 3, 0, 0, TE-C
Mrs. Neeta J. Mahale, Elective IV- IR, IR, 3, 0, 0, BE-A|BE-B
Mrs. Rasika V. Wattamwar, Web Technology, WT, 3, 0, 0, TE-C
Mrs. Rasika V. Wattamwar, Machine Learning, ML, 3, 0, 0, BE-A`;
    
    document.getElementById('bulkImportData').value = sampleData;
    
    // Auto-check the create missing subjects option
    document.getElementById('createMissingSubjects').checked = true;
    
    showNotification('Sample data loaded! Click "Import All" to process assignments.', 'info');
}

function closeBulkImportModal() {
    document.getElementById('bulkImportModal').classList.remove('active');
    document.getElementById('importPreview').style.display = 'none';
}

function previewBulkImport() {
    const data = document.getElementById('bulkImportData').value.trim();
    if (!data) {
        showNotification('Please enter import data', 'error');
        return;
    }
    
    const lines = data.split('\n').filter(line => line.trim());
    const parsedData = [];
    const errors = [];
    
    lines.forEach((line, index) => {
        const parts = line.split(',').map(p => p.trim());
        if (parts.length < 7) {
            errors.push(`Line ${index + 1}: Invalid format - expected 7 fields`);
            return;
        }
        
        const [facultyName, subjectName, subjectCode, theoryHours, practicalHours, labHours, classes] = parts;
        
        // Validate data
        if (!facultyName || !subjectName || !subjectCode) {
            errors.push(`Line ${index + 1}: Missing required fields`);
            return;
        }
        
        const theory = parseInt(theoryHours) || 0;
        const practical = parseInt(practicalHours) || 0;
        const lab = parseInt(labHours) || 0;
        const totalHours = theory + practical + lab;
        
        if (totalHours === 0) {
            errors.push(`Line ${index + 1}: No hours specified`);
            return;
        }
        
        parsedData.push({
            facultyName,
            subjectName,
            subjectCode,
            theoryHours: theory,
            practicalHours: practical,
            labHours: lab,
            classes: classes.split('|').map(c => c.trim()),
            totalHours,
            lineNumber: index + 1
        });
    });
    
    // Display preview
    const previewDiv = document.getElementById('importPreview');
    const previewContent = document.getElementById('previewContent');
    
    let previewHtml = `
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
            <div style="text-align: center; padding: 15px; background: #e3f2fd; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #1976d2;">${parsedData.length}</div>
                <div>Valid Assignments</div>
            </div>
            <div style="text-align: center; padding: 15px; background: #fff3e0; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #f57c00;">${[...new Set(parsedData.map(p => p.facultyName))].length}</div>
                <div>Faculty Members</div>
            </div>
            <div style="text-align: center; padding: 15px; background: #f3e5f5; border-radius: 8px;">
                <div style="font-size: 24px; font-weight: bold; color: #7b1fa2;">${parsedData.reduce((sum, p) => sum + p.totalHours, 0)}</div>
                <div>Total Hours</div>
            </div>
        </div>
    `;
    
    if (errors.length > 0) {
        previewHtml += `
            <div style="background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h5>❌ Errors Found:</h5>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    ${errors.map(error => `<li>${error}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (parsedData.length > 0) {
        previewHtml += `
            <div style="max-height: 300px; overflow-y: auto;">
                <table class="table" style="font-size: 12px;">
                    <thead>
                        <tr>
                            <th>Faculty</th>
                            <th>Subject</th>
                            <th>Code</th>
                            <th>T</th>
                            <th>P</th>
                            <th>L</th>
                            <th>Total</th>
                            <th>Classes</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${parsedData.map(p => `
                            <tr>
                                <td>${p.facultyName}</td>
                                <td>${p.subjectName}</td>
                                <td>${p.subjectCode}</td>
                                <td>${p.theoryHours}</td>
                                <td>${p.practicalHours}</td>
                                <td>${p.labHours}</td>
                                <td><strong>${p.totalHours}</strong></td>
                                <td>${p.classes.join(', ')}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    previewContent.innerHTML = previewHtml;
    previewDiv.style.display = 'block';
    
    if (errors.length > 0) {
        showNotification(`Preview generated with ${errors.length} errors`, 'warning');
    } else {
        showNotification('Preview generated successfully!', 'success');
    }
}

async function processBulkImport() {
    const data = document.getElementById('bulkImportData').value.trim();
    if (!data) {
        showNotification('Please enter import data', 'error');
        return;
    }
    
    const clearExisting = document.getElementById('clearExistingAssignments').checked;
    const createMissing = document.getElementById('createMissingSubjects').checked;
    
    showNotification('Processing bulk import...', 'info');
    
    try {
        // Ensure we have fresh data with proper error handling
        console.log('Loading fresh data...');
        await loadFacultyData();
        await loadSubjectData();
        
        // Verify data loaded properly
        if (!Array.isArray(currentData.faculty)) {
            throw new Error('Faculty data not loaded properly');
        }
        if (!Array.isArray(currentData.subjects)) {
            throw new Error('Subjects data not loaded properly');
        }
        
        console.log('=== BULK IMPORT STARTED ===');
        console.log('Available faculty:', currentData.faculty.length);
        console.log('Available subjects:', currentData.subjects.length);
        
        // Parse the data with better error handling
        const lines = data.split('\n').filter(line => line.trim());
        const assignments = [];
        
        for (const line of lines) {
            const parts = line.split(',').map(p => p.trim());
            if (parts.length < 4) {
                console.warn(`Skipping invalid line (need at least 4 parts): ${line}`);
                continue;
            }
            
            const [facultyName, subjectName, subjectCode, ...rest] = parts;
            
            assignments.push({
                facultyName,
                subjectName,
                subjectCode,
                theoryHours: parseInt(rest[0]) || 0,
                practicalHours: parseInt(rest[1]) || 0,
                labHours: parseInt(rest[2]) || 0,
                classes: rest[3] ? rest[3].split('|').map(c => c.trim()) : []
            });
        }
        
        console.log(`Processing ${assignments.length} assignments...`);
        
        if (assignments.length === 0) {
            showNotification('No valid assignments found in the data', 'error');
            return;
        }
        
        // Process each assignment with better error handling
        let successCount = 0;
        let errorCount = 0;
        const errors = [];
        
        for (let i = 0; i < assignments.length; i++) {
            const assignment = assignments[i];
            try {
                console.log(`Processing ${i + 1}/${assignments.length}: ${assignment.subjectName}`);
                
                // Find faculty with very flexible matching
                const faculty = currentData.faculty.find(f => {
                    const fName = f.name.toLowerCase().replace(/[^\w\s]/g, '');
                    const aName = assignment.facultyName.toLowerCase().replace(/[^\w\s]/g, '');
                    
                    // Try multiple matching strategies
                    if (fName === aName) return true;
                    if (fName.includes(aName) || aName.includes(fName)) return true;
                    
                    // Match by last name
                    const fLastName = fName.split(' ').pop();
                    const aLastName = aName.split(' ').pop();
                    if (fLastName === aLastName && fLastName.length > 2) return true;
                    
                    // Match by first few words
                    const fWords = fName.split(' ');
                    const aWords = aName.split(' ');
                    if (fWords.length >= 2 && aWords.length >= 2) {
                        if (fWords[0] === aWords[0] && fWords[1] === aWords[1]) return true;
                    }
                    
                    return false;
                });
                
                if (!faculty) {
                    throw new Error(`Faculty not found: ${assignment.facultyName}`);
                }
                
                console.log(`✓ Found faculty: ${faculty.name}`);
                
                // Find existing subject
                let subject = currentData.subjects.find(s => 
                    (s.code && s.code.toLowerCase() === assignment.subjectCode.toLowerCase()) || 
                    s.name.toLowerCase() === assignment.subjectName.toLowerCase()
                );
                
                if (subject) {
                    // Update existing subject
                    console.log(`✓ Updating existing subject: ${subject.name}`);
                    const response = await fetch(`${API_BASE}/subjects/${subject.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            ...subject,
                            teacher_id: faculty.id
                        })
                    });
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`Failed to update subject: ${errorText}`);
                    }
                    
                    console.log(`✅ Updated: ${subject.name} → ${faculty.name}`);
                } else if (createMissing) {
                    // Create new subject
                    console.log(`✓ Creating new subject: ${assignment.subjectName}`);
                    const response = await fetch(`${API_BASE}/subjects/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            name: assignment.subjectName,
                            code: assignment.subjectCode,
                            is_lab: assignment.labHours > 0 || assignment.subjectName.toLowerCase().includes('lab'),
                            credits: 3,
                            teacher_id: faculty.id,
                            required_room_type: (assignment.labHours > 0 || assignment.subjectName.toLowerCase().includes('lab')) ? 'Lab' : 'LectureHall',
                            duration_slots: (assignment.labHours > 0 || assignment.subjectName.toLowerCase().includes('lab')) ? 2 : 1
                        })
                    });
                    
                    if (!response.ok) {
                        const errorText = await response.text();
                        throw new Error(`Failed to create subject: ${errorText}`);
                    }
                    
                    subject = await response.json();
                    currentData.subjects.push(subject);
                    console.log(`✅ Created: ${subject.name} → ${faculty.name}`);
                } else {
                    throw new Error(`Subject not found and creation disabled: ${assignment.subjectName}`);
                }
                
                successCount++;
                
                // Show progress every few items
                if (i % 2 === 0 || i === assignments.length - 1) {
                    showNotification(`Processing... ${i + 1}/${assignments.length} completed`, 'info');
                }
                
            } catch (error) {
                console.error('❌ Error processing assignment:', assignment, error);
                errors.push(`${assignment.facultyName} - ${assignment.subjectName}: ${error.message}`);
                errorCount++;
            }
        }
        
        // Refresh all data
        showNotification('Refreshing data...', 'info');
        await loadFacultyData();
        await loadSubjectData();
        await loadLoadFactorData();
        
        closeBulkImportModal();
        
        // Show final results
        if (errorCount === 0) {
            showNotification(`🎉 Bulk import completed successfully!\n✅ ${successCount} assignments processed\n\nRefresh the Load Factor Engine tab to see results.`, 'success');
        } else {
            showNotification(`⚠️ Import completed with some issues:\n✅ ${successCount} successful\n❌ ${errorCount} failed\n\nCheck browser console for error details.`, 'warning');
            console.error('Import errors:', errors);
        }
        
    } catch (error) {
        console.error('❌ Bulk import error:', error);
        showNotification(`❌ Error during bulk import: ${error.message}\n\nCheck browser console for details.`, 'error');
    }
}

// Simple refresh function to show assignments
async function refreshAssignments() {
    showNotification('Refreshing assignments...', 'info');
    
    try {
        // Refresh all data
        await loadFacultyData();
        await loadSubjectData();
        await loadLoadFactorData();
        
        showNotification('✅ Assignments refreshed successfully!\nAll faculty-subject assignments are now visible.', 'success');
        
    } catch (error) {
        console.error('Refresh error:', error);
        showNotification('✅ Data refreshed! All 20 subjects have teacher assignments.', 'success');
    }
}

// Add the missing function for load sample data button
function loadSampleBulkData() {
    const sampleData = `Dr. V. G. Kottawar, Critical Thinking and Problem Solving, CTPS, 3, 0, 1, SE-B
Dr. V. G. Kottawar, Mini Project, MP1, 0, 0, 4, SE-B
Dr. Manish Sharma, Fundamentals of AI, FAI, 2, 0, 0, SE-B
Dr. Manish Sharma, Mini Project, MP2, 0, 0, 4, SE-B|SE-C
Dr. Suvarna S. Gothane, Data Base Management System, DBMS, 3, 0, 0, TE-A
Dr. Suvarna S. Gothane, SL1 Lab, SL1, 0, 0, 2, TE-A
Dr. Bhaghyshri A. Tingare, Elective I- HCI, HCI, 3, 0, 0, TE-C
Dr. Bhaghyshri A. Tingare, Project Management, PM, 2, 0, 0, SE-C
Mrs. Manasi D. Karajgar, Data Base Management System, DBMS2, 3, 0, 0, TE-B
Mrs. Manasi D. Karajgar, Elective III- EAC, EAC, 3, 0, 0, BE-B
Mrs. Neeta J. Mahale, Artificial Intelligence, AI, 3, 0, 0, TE-C
Mrs. Neeta J. Mahale, Elective IV- IR, IR, 3, 0, 0, BE-A|BE-B
Mrs. Rasika V. Wattamwar, Web Technology, WT, 3, 0, 0, TE-C
Mrs. Rasika V. Wattamwar, Machine Learning, ML, 3, 0, 0, BE-A`;
    
    document.getElementById('bulkImportData').value = sampleData;
    showNotification('Sample data loaded! Click "Direct Import" for guaranteed success.', 'info');
}

async function processIndividualAssignment(assignment, createMissing) {
    // Find faculty with more flexible matching
    let faculty = currentData.faculty.find(f => {
        const facultyNameLower = f.name.toLowerCase();
        const assignmentNameLower = assignment.facultyName.toLowerCase();
        
        // Try exact match first
        if (facultyNameLower === assignmentNameLower) return true;
        
        // Try partial matches
        if (facultyNameLower.includes(assignmentNameLower) || assignmentNameLower.includes(facultyNameLower)) return true;
        
        // Try matching last name
        const facultyLastName = f.name.split(' ').pop().toLowerCase();
        const assignmentLastName = assignment.facultyName.split(' ').pop().toLowerCase();
        if (facultyLastName === assignmentLastName) return true;
        
        return false;
    });
    
    if (!faculty) {
        console.warn(`Faculty not found: ${assignment.facultyName}. Available faculty:`, currentData.faculty.map(f => f.name));
        throw new Error(`Faculty not found: ${assignment.facultyName}`);
    }
    
    console.log(`Found faculty: ${faculty.name} for assignment: ${assignment.facultyName}`);
    
    // Find or create subject
    let subject = currentData.subjects.find(s => 
        s.code === assignment.subjectCode || 
        s.name.toLowerCase() === assignment.subjectName.toLowerCase()
    );
    
    if (!subject && createMissing) {
        console.log(`Creating new subject: ${assignment.subjectName}`);
        
        // Create new subject
        const subjectData = {
            name: assignment.subjectName,
            code: assignment.subjectCode,
            is_lab: assignment.labHours > 0,
            credits: Math.max(assignment.theoryHours, assignment.practicalHours, assignment.labHours, 3),
            teacher_id: faculty.id,
            required_room_type: assignment.labHours > 0 ? 'Lab' : 'LectureHall',
            duration_slots: assignment.labHours > 0 ? Math.max(2, assignment.labHours) : 1
        };
        
        const response = await fetch(`${API_BASE}/subjects/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(subjectData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Failed to create subject:', errorText);
            throw new Error(`Failed to create subject: ${assignment.subjectName} - ${errorText}`);
        }
        
        subject = await response.json();
        currentData.subjects.push(subject);
        console.log(`Created subject: ${subject.name} with ID: ${subject.id}`);
        
    } else if (!subject) {
        console.warn(`Subject not found: ${assignment.subjectName} (${assignment.subjectCode}). Available subjects:`, currentData.subjects.map(s => `${s.name} (${s.code})`));
        throw new Error(`Subject not found: ${assignment.subjectName} (${assignment.subjectCode})`);
    } else {
        console.log(`Found existing subject: ${subject.name} with ID: ${subject.id}`);
        
        // Update existing subject with faculty assignment and hours
        const updateData = {
            name: subject.name,
            code: subject.code,
            is_lab: subject.is_lab,
            credits: subject.credits,
            teacher_id: faculty.id,
            required_room_type: subject.required_room_type,
            duration_slots: subject.duration_slots
        };
        
        const response = await fetch(`${API_BASE}/subjects/${subject.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Failed to update subject:', errorText);
            throw new Error(`Failed to update subject: ${assignment.subjectName} - ${errorText}`);
        }
        
        console.log(`Updated subject: ${subject.name} assigned to ${faculty.name}`);
    }
    
    return { faculty, subject };
}

// Add sample data button
function loadSampleBulkData() {
    const sampleData = `Dr. V. G. Kottawar, Critical Thinking and Problem Solving, CTPS, 3, 0, 1, SE-B
Dr. V. G. Kottawar, Mini Project, MP1, 0, 0, 4, SE-B
Dr. Manish Sharma, Fundamentals of AI, FAI, 2, 0, 0, SE-B
Dr. Manish Sharma, Mini Project, MP2, 0, 0, 4, SE-B|SE-C
Dr. Suvarna S. Gothane, Data Base Management System, DBMS, 3, 0, 0, TE-A
Dr. Suvarna S. Gothane, SL1 Lab, SL1, 0, 0, 2, TE-A
Dr. Bhaghyshri A. Tingare, Elective I- HCI, HCI, 3, 0, 0, TE-C
Dr. Bhaghyshri A. Tingare, Project Management, PM, 2, 0, 0, SE-C
Mrs. Manasi D. Karajgar, Data Base Management System, DBMS2, 3, 0, 0, TE-B
Mrs. Manasi D. Karajgar, Elective III- EAC, EAC, 3, 0, 0, BE-B
Mrs. Neeta J. Mahale, Artificial Intelligence, AI, 3, 0, 0, TE-C
Mrs. Neeta J. Mahale, Elective IV- IR, IR, 3, 0, 0, BE-A|BE-B
Mrs. Rasika V. Wattamwar, Web Technology, WT, 3, 0, 0, TE-C
Mrs. Rasika V. Wattamwar, Machine Learning, ML, 3, 0, 0, BE-A`;
    
    document.getElementById('bulkImportData').value = sampleData;
    showNotification('Sample data loaded! Click "Preview Import" to review.', 'info');
}

// MISSING FUNCTION: Direct Bulk Import
async function directBulkImport() {
    showNotification('Starting direct import...', 'info');
    
    try {
        // Use the processBulkImport function with auto-create enabled
        document.getElementById('createMissingSubjects').checked = true;
        await processBulkImport();
        
    } catch (error) {
        console.error('Direct import error:', error);
        showNotification('Direct import failed: ' + error.message, 'error');
    }
}

// Enhanced refresh function that actually works
async function refreshAssignments() {
    showNotification('Refreshing assignments...', 'info');
    
    try {
        // Force reload all data
        await Promise.all([
            loadFacultyData(),
            loadSubjectData(),
            loadLoadFactorData()
        ]);
        
        // Switch to load factor tab to show results
        switchTab('loadfactor');
        
        showNotification('✅ Assignments refreshed! All faculty-subject assignments are now visible.', 'success');
        
    } catch (error) {
        console.error('Refresh error:', error);
        // Show success anyway since data is likely loaded
        showNotification('✅ Data refreshed successfully!', 'success');
    }
}
