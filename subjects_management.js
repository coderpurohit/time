// Subjects Management Functions

async function editSubject(subjectId) {
    try {
        const response = await fetch(`${API_BASE}/subjects/${subjectId}`);
        const subject = await response.json();
        
        document.getElementById('subjectId').value = subject.id;
        document.getElementById('subjectName').value = subject.name;
        document.getElementById('subjectCode').value = subject.code;
        document.getElementById('subjectCredits').value = subject.credits;
        document.getElementById('subjectType').value = subject.is_lab ? 'true' : 'false';
        document.getElementById('subjectDuration').value = subject.duration_slots;
        document.getElementById('subjectRoomType').value = subject.room_type;
        
        document.getElementById('subjectModalTitle').textContent = 'Edit Subject';
        document.getElementById('subjectModal').style.display = 'flex';
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error loading subject', 'error');
    }
}

async function deleteSubject(subjectId) {
    if (!confirm('Are you sure you want to delete this subject?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/subjects/${subjectId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showStatus('Subject deleted successfully!', 'success');
            loadSubjects();
        } else {
            showStatus('Failed to delete subject', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}
