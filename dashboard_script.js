// Dashboard Script - Core Functions

// Initialize wizard on page load
function initWizard() {
    console.log('Initializing wizard...');
    const firstTab = document.querySelector('.wizard-tab');
    if (firstTab) {
        firstTab.click();
    }
}

// Switch between tabs
function switchTab(step) {
    console.log('Switching to tab:', step);
    
    // Hide all sections
    document.querySelectorAll('.wizard-content').forEach(el => {
        el.classList.remove('active');
    });
    
    // Remove active from all tabs
    document.querySelectorAll('.wizard-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected section
    const section = document.getElementById(`step-${step}`);
    if (section) {
        section.classList.add('active');
    }
    
    // Mark tab as active
    const tab = document.querySelector(`[data-step="${step}"]`);
    if (tab) {
        tab.classList.add('active');
    }
}

// Teacher Management Functions
function openTeacherModal() {
    const modal = document.getElementById('teacherModal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('teacherModalTitle').textContent = 'Add New Teacher';
        document.getElementById('teacherForm').reset();
    }
}

function closeTeacherModal() {
    const modal = document.getElementById('teacherModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function openDeleteTeacherModal(teacherId, teacherName) {
    const modal = document.getElementById('deleteTeacherModal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('deleteTeacherName').textContent = teacherName;
        window.deleteTeacherId = teacherId;
    }
}

function closeDeleteTeacherModal() {
    const modal = document.getElementById('deleteTeacherModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function saveTeacher(event) {
    event.preventDefault();
    
    const name = document.getElementById('teacherName').value;
    const email = document.getElementById('teacherEmail').value;
    const hours = document.getElementById('teacherHours').value;
    
    try {
        const response = await fetch(`${API_BASE}/teachers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                email: email,
                max_hours_per_week: parseInt(hours)
            })
        });
        
        if (response.ok) {
            showStatus('Teacher added successfully!', 'success');
            closeTeacherModal();
            loadTeachersInPage();
        } else {
            showStatus('Failed to add teacher', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

async function confirmDeleteTeacher() {
    const teacherId = window.deleteTeacherId;
    
    try {
        const response = await fetch(`${API_BASE}/teachers/${teacherId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showStatus('Teacher deleted successfully!', 'success');
            closeDeleteTeacherModal();
            loadTeachersInPage();
        } else {
            showStatus('Failed to delete teacher', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Subject Management Functions
function openSubjectModal() {
    const modal = document.getElementById('subjectModal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('subjectModalTitle').textContent = 'Add Subject';
        document.getElementById('subjectForm').reset();
    }
}

function closeSubjectModal() {
    const modal = document.getElementById('subjectModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function saveSubject(event) {
    event.preventDefault();
    
    const name = document.getElementById('subjectName').value;
    const code = document.getElementById('subjectCode').value;
    const credits = document.getElementById('subjectCredits').value;
    const type = document.getElementById('subjectType').value === 'true';
    const duration = document.getElementById('subjectDuration').value;
    const roomType = document.getElementById('subjectRoomType').value;
    
    try {
        const response = await fetch(`${API_BASE}/subjects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                code: code,
                credits: parseInt(credits),
                is_lab: type,
                duration_slots: parseInt(duration),
                room_type: roomType
            })
        });
        
        if (response.ok) {
            showStatus('Subject added successfully!', 'success');
            closeSubjectModal();
            loadSubjects();
        } else {
            showStatus('Failed to add subject', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Class Management Functions
function openClassModal() {
    const modal = document.getElementById('classModal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('classModalTitle').textContent = 'Add Class';
        document.getElementById('classForm').reset();
    }
}

function closeClassModal() {
    const modal = document.getElementById('classModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function saveClass(event) {
    event.preventDefault();
    
    const name = document.getElementById('className').value;
    const studentCount = document.getElementById('classStudentCount').value;
    
    try {
        const response = await fetch(`${API_BASE}/class-groups`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                student_count: parseInt(studentCount)
            })
        });
        
        if (response.ok) {
            showStatus('Class added successfully!', 'success');
            closeClassModal();
            loadClasses();
        } else {
            showStatus('Failed to add class', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Room Management Functions
function openRoomModal() {
    const modal = document.getElementById('roomModal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('roomModalTitle').textContent = 'Add Room';
        document.getElementById('roomForm').reset();
    }
}

function closeRoomModal() {
    const modal = document.getElementById('roomModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function saveRoom(event) {
    event.preventDefault();
    
    const name = document.getElementById('roomName').value;
    const type = document.getElementById('roomType').value;
    const capacity = document.getElementById('roomCapacity').value;
    const resources = document.getElementById('roomResources').value;
    
    try {
        const response = await fetch(`${API_BASE}/rooms`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                room_type: type,
                capacity: parseInt(capacity),
                resources: resources
            })
        });
        
        if (response.ok) {
            showStatus('Room added successfully!', 'success');
            closeRoomModal();
            loadRooms();
        } else {
            showStatus('Failed to add room', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Bulk Import Functions
function openTeacherBulkImportModal() {
    const modal = document.getElementById('teacherBulkImportModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeTeacherBulkImportModal() {
    const modal = document.getElementById('teacherBulkImportModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function submitTeacherBulkImport() {
    const fileInput = document.getElementById('teacherCsvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showStatus('Please select a CSV file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/import/teachers-csv`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            showStatus('Teachers imported successfully!', 'success');
            closeTeacherBulkImportModal();
            loadTeachersInPage();
        } else {
            const error = await response.json();
            showStatus('Import failed: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Utility Functions
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('statusMessage');
    if (statusDiv) {
        statusDiv.textContent = message;
        statusDiv.className = `status-message ${type}`;
        statusDiv.style.display = 'block';
        
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
    }
}

function updateRoomType() {
    const type = document.getElementById('subjectType').value;
    const roomTypeSelect = document.getElementById('subjectRoomType');
    if (type === 'true') {
        roomTypeSelect.value = 'Lab';
    } else {
        roomTypeSelect.value = 'LectureHall';
    }
}

function filterSubjects() {
    const searchTerm = document.getElementById('subjectSearch').value.toLowerCase();
    const typeFilter = document.getElementById('subjectTypeFilter').value;
    
    const rows = document.querySelectorAll('#subjectsTableBody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const type = row.getAttribute('data-type') || '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesType = !typeFilter || type === typeFilter;
        
        row.style.display = (matchesSearch && matchesType) ? '' : 'none';
    });
}

function filterClasses() {
    const searchTerm = document.getElementById('classSearch').value.toLowerCase();
    
    const rows = document.querySelectorAll('#classesTableBody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

function filterRooms() {
    const searchTerm = document.getElementById('roomSearch').value.toLowerCase();
    const typeFilter = document.getElementById('roomTypeFilter').value;
    
    const rows = document.querySelectorAll('#roomsTableBody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const type = row.getAttribute('data-type') || '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesType = !typeFilter || type === typeFilter;
        
        row.style.display = (matchesSearch && matchesType) ? '' : 'none';
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard script loaded');
    initWizard();
});
