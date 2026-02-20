const API_BASE = 'http://localhost:8000/api';

let allTeachers = [];
let editingTeacherId = null;
let deletingTeacherId = null;

// Load teachers on page load
document.addEventListener('DOMContentLoaded', () => {
    loadTeachers();
});

async function loadTeachers() {
    try {
        const response = await fetch(`${API_BASE}/teachers`);
        if (!response.ok) throw new Error('Failed to load teachers');
        
        allTeachers = await response.json();
        renderTeachers(allTeachers);
        updateStats();
    } catch (error) {
        showStatus('Error loading teachers: ' + error.message, 'error');
        document.getElementById('teachersContainer').innerHTML = 
            '<div class="empty-state">Failed to load teachers. Make sure the backend is running.</div>';
    }
}

function renderTeachers(teachers) {
    const container = document.getElementById('teachersContainer');
    
    if (teachers.length === 0) {
        container.innerHTML = '<div class="empty-state">No teachers found. Click "Add New Teacher" to get started!</div>';
        return;
    }

    container.innerHTML = teachers.map(teacher => `
        <div class="teacher-card">
            <div class="teacher-header">
                <div>
                    <div class="teacher-name">${teacher.name}</div>
                    <div class="teacher-email">📧 ${teacher.email}</div>
                </div>
            </div>
            
            <div class="teacher-info">
                <div class="info-row">
                    <span class="info-label">Max Hours/Week:</span>
                    <span>${teacher.max_hours_per_week || 20} hours</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Teacher ID:</span>
                    <span>#${teacher.id}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Created:</span>
                    <span>${new Date(teacher.created_at).toLocaleDateString()}</span>
                </div>
            </div>

            <div class="teacher-actions">
                <button class="btn btn-primary" onclick="openEditModal(${teacher.id})">✏️ Edit</button>
                <button class="btn btn-danger" onclick="openDeleteModal(${teacher.id}, '${teacher.name.replace(/'/g, "\\'")}')">🗑️ Delete</button>
            </div>
        </div>
    `).join('');
}

function filterTeachers() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filtered = allTeachers.filter(teacher => 
        teacher.name.toLowerCase().includes(searchTerm) ||
        teacher.email.toLowerCase().includes(searchTerm)
    );
    renderTeachers(filtered);
}

function updateStats() {
    document.getElementById('totalTeachers').textContent = allTeachers.length;
    
    if (allTeachers.length > 0) {
        const avgHours = allTeachers.reduce((sum, t) => sum + (t.max_hours_per_week || 20), 0) / allTeachers.length;
        document.getElementById('avgHours').textContent = Math.round(avgHours);
    } else {
        document.getElementById('avgHours').textContent = '0';
    }
}

function openAddModal() {
    editingTeacherId = null;
    document.getElementById('modalTitle').textContent = 'Add New Teacher';
    document.getElementById('teacherForm').reset();
    document.getElementById('teacherHours').value = 20;
    document.getElementById('teacherModal').classList.add('active');
}

function openEditModal(teacherId) {
    const teacher = allTeachers.find(t => t.id === teacherId);
    if (!teacher) return;

    editingTeacherId = teacherId;
    document.getElementById('modalTitle').textContent = 'Edit Teacher';
    document.getElementById('teacherName').value = teacher.name;
    document.getElementById('teacherEmail').value = teacher.email;
    document.getElementById('teacherHours').value = teacher.max_hours_per_week || 20;
    document.getElementById('teacherModal').classList.add('active');
}

function closeModal() {
    document.getElementById('teacherModal').classList.remove('active');
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
            // Update existing teacher
            response = await fetch(`${API_BASE}/teachers/${editingTeacherId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(teacherData)
            });
        } else {
            // Create new teacher
            response = await fetch(`${API_BASE}/teachers/`, {
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
        closeModal();
        loadTeachers();
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
}

function openDeleteModal(teacherId, teacherName) {
    deletingTeacherId = teacherId;
    document.getElementById('deleteTeacherName').textContent = teacherName;
    document.getElementById('deleteModal').classList.add('active');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('active');
    deletingTeacherId = null;
}

async function confirmDelete() {
    if (!deletingTeacherId) return;

    try {
        const response = await fetch(`${API_BASE}/teachers/${deletingTeacherId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete teacher');
        }

        showStatus('Teacher deleted successfully!', 'success');
        closeDeleteModal();
        loadTeachers();
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
        closeDeleteModal();
    }
}

function showStatus(message, type) {
    const statusEl = document.getElementById('statusMessage');
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    statusEl.style.display = 'block';

    setTimeout(() => {
        statusEl.style.display = 'none';
    }, 5000);
}

// Close modals when clicking outside
window.onclick = function(event) {
    const teacherModal = document.getElementById('teacherModal');
    const deleteModal = document.getElementById('deleteModal');
    
    if (event.target === teacherModal) {
        closeModal();
    }
    if (event.target === deleteModal) {
        closeDeleteModal();
    }
}
