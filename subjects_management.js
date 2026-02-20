// Subjects Management JavaScript

let allSubjects = [];
let allTeachers = [];

// Load subjects when page loads
async function loadSubjects() {
    try {
        const response = await fetch('http://localhost:8000/api/subjects/');
        if (!response.ok) throw new Error('Failed to load subjects');
        
        allSubjects = await response.json();
        renderSubjectsTable(allSubjects);
        
        // Mark tab as complete if subjects exist
        if (allSubjects.length > 0) {
            document.querySelector('[data-step="subjects"]').classList.add('completed');
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
        document.getElementById('subjectsTableBody').innerHTML = `
            <tr><td colspan="8" style="text-align: center; color: red;">
                Error loading subjects. Make sure backend is running.
            </td></tr>
        `;
    }
}

// Load teachers for dropdown
async function loadTeachersForSubjects() {
    try {
        const response = await fetch('http://localhost:8000/api/teachers/');
        if (!response.ok) throw new Error('Failed to load teachers');
        
        allTeachers = await response.json();
        
        // Populate teacher dropdown
        const teacherSelect = document.getElementById('subjectTeacher');
        teacherSelect.innerHTML = '<option value="">-- No Teacher Assigned --</option>';
        
        allTeachers.forEach(teacher => {
            const option = document.createElement('option');
            option.value = teacher.id;
            option.textContent = teacher.name;
            teacherSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading teachers:', error);
    }
}

// Render subjects table
function renderSubjectsTable(subjects) {
    const tbody = document.getElementById('subjectsTableBody');
    
    if (subjects.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="8" style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-book" style="font-size: 48px; opacity: 0.3; margin-bottom: 10px;"></i>
                <p>No subjects found. Click "Add Subject" to create one.</p>
            </td></tr>
        `;
        return;
    }
    
    tbody.innerHTML = subjects.map(subject => {
        const teacher = allTeachers.find(t => t.id === subject.teacher_id);
        const teacherName = teacher ? teacher.name : '<span style="color: #999;">Unassigned</span>';
        const type = subject.is_lab ? '<span class="badge badge-lab">Lab</span>' : '<span class="badge badge-theory">Theory</span>';
        const duration = subject.duration_slots === 1 ? 'Single' : subject.duration_slots === 2 ? 'Double' : `${subject.duration_slots} periods`;
        
        return `
            <tr>
                <td><strong>${subject.code}</strong></td>
                <td>${subject.name}</td>
                <td>${subject.credits}</td>
                <td>${type}</td>
                <td>${duration}</td>
                <td>${teacherName}</td>
                <td>${subject.required_room_type}</td>
                <td>
                    <button class="btn-icon" onclick="editSubject(${subject.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-danger" onclick="deleteSubject(${subject.id}, '${subject.name}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Filter subjects
function filterSubjects() {
    const searchTerm = document.getElementById('subjectSearch').value.toLowerCase();
    const typeFilter = document.getElementById('subjectTypeFilter').value;
    
    let filtered = allSubjects.filter(subject => {
        const matchesSearch = subject.name.toLowerCase().includes(searchTerm) || 
                            subject.code.toLowerCase().includes(searchTerm);
        
        let matchesType = true;
        if (typeFilter === 'theory') matchesType = !subject.is_lab;
        if (typeFilter === 'lab') matchesType = subject.is_lab;
        
        return matchesSearch && matchesType;
    });
    
    renderSubjectsTable(filtered);
}

// Open modal for adding subject
function openSubjectModal() {
    document.getElementById('subjectModalTitle').textContent = 'Add Subject';
    document.getElementById('subjectForm').reset();
    document.getElementById('subjectId').value = '';
    document.getElementById('subjectModal').style.display = 'flex';
    loadTeachersForSubjects();
}

// Open modal for editing subject
async function editSubject(id) {
    try {
        const response = await fetch(`http://localhost:8000/api/subjects/${id}`);
        if (!response.ok) throw new Error('Failed to load subject');
        
        const subject = await response.json();
        
        document.getElementById('subjectModalTitle').textContent = 'Edit Subject';
        document.getElementById('subjectId').value = subject.id;
        document.getElementById('subjectName').value = subject.name;
        document.getElementById('subjectCode').value = subject.code;
        document.getElementById('subjectCredits').value = subject.credits;
        document.getElementById('subjectType').value = subject.is_lab.toString();
        document.getElementById('subjectDuration').value = subject.duration_slots;
        document.getElementById('subjectRoomType').value = subject.required_room_type;
        
        await loadTeachersForSubjects();
        document.getElementById('subjectTeacher').value = subject.teacher_id || '';
        
        document.getElementById('subjectModal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading subject:', error);
        alert('Failed to load subject details');
    }
}

// Close modal
function closeSubjectModal() {
    document.getElementById('subjectModal').style.display = 'none';
}

// Update room type based on subject type
function updateRoomType() {
    const isLab = document.getElementById('subjectType').value === 'true';
    const roomTypeSelect = document.getElementById('subjectRoomType');
    
    if (isLab) {
        roomTypeSelect.value = 'Lab';
    } else {
        roomTypeSelect.value = 'LectureHall';
    }
}

// Save subject (create or update)
async function saveSubject(event) {
    event.preventDefault();
    
    const id = document.getElementById('subjectId').value;
    const data = {
        name: document.getElementById('subjectName').value,
        code: document.getElementById('subjectCode').value,
        credits: parseInt(document.getElementById('subjectCredits').value),
        is_lab: document.getElementById('subjectType').value === 'true',
        duration_slots: parseInt(document.getElementById('subjectDuration').value),
        required_room_type: document.getElementById('subjectRoomType').value,
        teacher_id: document.getElementById('subjectTeacher').value ? parseInt(document.getElementById('subjectTeacher').value) : null
    };
    
    try {
        const url = id ? `http://localhost:8000/api/subjects/${id}` : 'http://localhost:8000/api/subjects/';
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save subject');
        }
        
        closeSubjectModal();
        await loadSubjects();
        
        // Show success message
        showNotification(id ? 'Subject updated successfully!' : 'Subject created successfully!', 'success');
    } catch (error) {
        console.error('Error saving subject:', error);
        alert('Error: ' + error.message);
    }
}

// Delete subject
async function deleteSubject(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:8000/api/subjects/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete subject');
        
        await loadSubjects();
        showNotification('Subject deleted successfully!', 'success');
    } catch (error) {
        console.error('Error deleting subject:', error);
        alert('Failed to delete subject. It may be used in lessons.');
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        ${message}
    `;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadSubjects);
} else {
    loadSubjects();
}
