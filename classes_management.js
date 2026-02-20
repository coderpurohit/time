// Classes/Grades Management JavaScript

let allClasses = [];
let classCoverage = {};

// Load classes when page loads
async function loadClasses() {
    try {
        const response = await fetch('http://localhost:8000/api/class-groups/');
        if (!response.ok) throw new Error('Failed to load classes');
        
        allClasses = await response.json();
        
        // Get coverage data (periods assigned to each class)
        await loadClassCoverage();
        
        renderClassesTable(allClasses);
        
        // Mark tab as complete if classes exist
        if (allClasses.length > 0) {
            document.querySelector('[data-step="classes"]').classList.add('completed');
        }
    } catch (error) {
        console.error('Error loading classes:', error);
        document.getElementById('classesTableBody').innerHTML = `
            <tr><td colspan="5" style="text-align: center; color: red;">
                Error loading classes. Make sure backend is running.
            </td></tr>
        `;
    }
}

// Load class coverage (how many periods assigned)
async function loadClassCoverage() {
    try {
        const response = await fetch('http://localhost:8000/api/timetables/latest');
        if (!response.ok) return;
        
        const timetable = await response.json();
        classCoverage = {};
        
        // Count entries per class
        timetable.entries.forEach(entry => {
            if (entry.class_group) {
                const classId = entry.class_group.id;
                classCoverage[classId] = (classCoverage[classId] || 0) + 1;
            }
        });
    } catch (error) {
        console.error('Error loading coverage:', error);
    }
}

// Render classes table
function renderClassesTable(classes) {
    const tbody = document.getElementById('classesTableBody');
    
    if (classes.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="5" style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-users" style="font-size: 48px; opacity: 0.3; margin-bottom: 10px;"></i>
                <p>No classes found. Click "Add Class" to create one.</p>
            </td></tr>
        `;
        return;
    }
    
    tbody.innerHTML = classes.map(classGroup => {
        const periods = classCoverage[classGroup.id] || 0;
        const targetPeriods = 25; // Target periods per class
        const coverage = targetPeriods > 0 ? (periods / targetPeriods * 100).toFixed(0) : 0;
        
        let coverageBadge = '';
        if (coverage >= 90) {
            coverageBadge = `<span class="badge" style="background: #d1fae5; color: #065f46;">${coverage}%</span>`;
        } else if (coverage >= 50) {
            coverageBadge = `<span class="badge" style="background: #fef3c7; color: #92400e;">${coverage}%</span>`;
        } else {
            coverageBadge = `<span class="badge" style="background: #fee2e2; color: #991b1b;">${coverage}%</span>`;
        }
        
        return `
            <tr>
                <td><strong>${classGroup.name}</strong></td>
                <td>${classGroup.student_count} students</td>
                <td>${periods}/${targetPeriods}</td>
                <td>${coverageBadge}</td>
                <td>
                    <button class="btn-icon" onclick="editClass(${classGroup.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-danger" onclick="deleteClass(${classGroup.id}, '${classGroup.name}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Filter classes
function filterClasses() {
    const searchTerm = document.getElementById('classSearch').value.toLowerCase();
    
    const filtered = allClasses.filter(classGroup => 
        classGroup.name.toLowerCase().includes(searchTerm)
    );
    
    renderClassesTable(filtered);
}

// Open modal for adding class
function openClassModal() {
    document.getElementById('classModalTitle').textContent = 'Add Class';
    document.getElementById('classForm').reset();
    document.getElementById('classId').value = '';
    document.getElementById('classModal').style.display = 'flex';
}

// Open modal for editing class
async function editClass(id) {
    try {
        const response = await fetch(`http://localhost:8000/api/class-groups/${id}`);
        if (!response.ok) throw new Error('Failed to load class');
        
        const classGroup = await response.json();
        
        document.getElementById('classModalTitle').textContent = 'Edit Class';
        document.getElementById('classId').value = classGroup.id;
        document.getElementById('className').value = classGroup.name;
        document.getElementById('classStudentCount').value = classGroup.student_count;
        
        document.getElementById('classModal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading class:', error);
        alert('Failed to load class details');
    }
}

// Close modal
function closeClassModal() {
    document.getElementById('classModal').style.display = 'none';
}

// Save class (create or update)
async function saveClass(event) {
    event.preventDefault();
    
    const id = document.getElementById('classId').value;
    const data = {
        name: document.getElementById('className').value,
        student_count: parseInt(document.getElementById('classStudentCount').value)
    };
    
    try {
        const url = id ? `http://localhost:8000/api/class-groups/${id}` : 'http://localhost:8000/api/class-groups/';
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save class');
        }
        
        closeClassModal();
        await loadClasses();
        
        showNotification(id ? 'Class updated successfully!' : 'Class created successfully!', 'success');
    } catch (error) {
        console.error('Error saving class:', error);
        alert('Error: ' + error.message);
    }
}

// Delete class
async function deleteClass(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?\n\nThis will also delete all timetable entries for this class.\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:8000/api/class-groups/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete class');
        
        await loadClasses();
        showNotification('Class deleted successfully!', 'success');
    } catch (error) {
        console.error('Error deleting class:', error);
        alert('Failed to delete class. It may be used in timetable entries.');
    }
}

// Show notification (reuse from subjects_management.js)
function showNotification(message, type = 'info') {
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
    document.addEventListener('DOMContentLoaded', loadClasses);
} else {
    loadClasses();
}
