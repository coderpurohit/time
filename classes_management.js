// Classes Management Functions

async function editClass(classId) {
    try {
        const response = await fetch(`${API_BASE}/class-groups/${classId}`);
        const classData = await response.json();
        
        document.getElementById('classId').value = classData.id;
        document.getElementById('className').value = classData.name;
        document.getElementById('classStudentCount').value = classData.student_count;
        
        document.getElementById('classModalTitle').textContent = 'Edit Class';
        document.getElementById('classModal').style.display = 'flex';
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error loading class', 'error');
    }
}

async function deleteClass(classId) {
    if (!confirm('Are you sure you want to delete this class?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/class-groups/${classId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showStatus('Class deleted successfully!', 'success');
            loadClasses();
        } else {
            showStatus('Failed to delete class', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}
