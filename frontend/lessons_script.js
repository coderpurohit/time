// Lessons Script - Core Functions

async function loadLessons() {
    try {
        const response = await fetch(`${API_BASE}/lessons`);
        const lessons = await response.json();
        
        const container = document.getElementById('lessonsList');
        if (!container) return;
        
        if (lessons.length === 0) {
            container.innerHTML = `
                <div class="lessons-empty">
                    <div class="lessons-empty-icon">📚</div>
                    <div class="lessons-empty-text">No lessons found</div>
                    <div class="lessons-empty-subtext">Create your first lesson to get started</div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = lessons.map(lesson => `
            <div class="lesson-item">
                <div class="lesson-item-header">
                    <div>
                        <div class="lesson-item-title">${lesson.subject?.name || 'Unknown Subject'}</div>
                        <div class="lesson-item-meta">
                            <div class="lesson-meta-item">
                                <strong>Teacher:</strong> ${lesson.teacher?.name || 'TBA'}
                            </div>
                            <div class="lesson-meta-item">
                                <strong>Class:</strong> ${lesson.class_group?.name || 'All'}
                            </div>
                            <div class="lesson-meta-item">
                                <strong>Periods:</strong> ${lesson.duration_slots || 1}
                            </div>
                        </div>
                    </div>
                    <div class="lesson-actions">
                        <button class="lesson-btn lesson-btn-edit" onclick="editLesson(${lesson.id})">Edit</button>
                        <button class="lesson-btn lesson-btn-delete" onclick="deleteLesson(${lesson.id})">Delete</button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading lessons:', error);
    }
}

async function editLesson(lessonId) {
    try {
        const response = await fetch(`${API_BASE}/lessons/${lessonId}`);
        const lesson = await response.json();
        
        console.log('Edit lesson:', lesson);
        showStatus('Edit functionality coming soon!', 'info');
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error loading lesson', 'error');
    }
}

async function deleteLesson(lessonId) {
    if (!confirm('Are you sure you want to delete this lesson?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/lessons/${lessonId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showStatus('Lesson deleted successfully!', 'success');
            loadLessons();
        } else {
            showStatus('Failed to delete lesson', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Lessons script loaded');
    loadLessons();
});
