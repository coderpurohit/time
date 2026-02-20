// Lessons Management Script
if (typeof API_BASE === 'undefined') {
    var API_BASE = window.location.origin + '/api';
}

// Ensure API_BASE doesn't end with a slash for consistency
API_BASE = API_BASE.replace(/\/$/, '');

let allLessons = [];
let currentLessonView = 'class'; // 'class' or 'teacher'

async function loadLessons() {
    try {
        const response = await fetch(`${API_BASE}/lessons/`);
        allLessons = await response.json();
        renderLessons();
    } catch (error) {
        console.error('Error loading lessons:', error);
        // Show error in console, don't break the page
        const container = document.getElementById('lessonsList');
        if (container) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <h3>Failed to Load Lessons</h3>
                    <p>Error: ${error.message}</p>
                </div>
            `;
        }
    }
}

function setLessonView(view) {
    currentLessonView = view;
    document.getElementById('view-class-wise').classList.toggle('active', view === 'class');
    document.getElementById('view-teacher-wise').classList.toggle('active', view === 'teacher');
    renderLessons();
}

function renderLessons() {
    const container = document.getElementById('lessonsList');
    if (!container) return;

    if (allLessons.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📖</div>
                <h3>No Lessons Configured</h3>
                <p>Add lessons manually or use Bulk Import to get started.</p>
            </div>
        `;
        return;
    }

    if (currentLessonView === 'class') {
        renderClassWise(container);
    } else {
        renderTeacherWise(container);
    }
}

function renderClassWise(container) {
    // Group lessons by Class Group
    const groups = {};
    allLessons.forEach(lesson => {
        lesson.class_groups.forEach(cg => {
            if (!groups[cg.name]) {
                groups[cg.name] = {
                    info: cg,
                    lessons: []
                };
            }
            groups[cg.name].lessons.push(lesson);
        });
    });

    let html = '';
    Object.keys(groups).sort().forEach(groupName => {
        const group = groups[groupName];
        const totalPeriods = group.lessons.reduce((sum, l) => sum + l.lessons_per_week, 0);
        const uniqueTeachers = new Set();
        group.lessons.forEach(l => l.teachers.forEach(t => uniqueTeachers.add(t.name)));

        html += `
            <div class="lesson-group-card">
                <div class="lesson-group-header">
                    <div class="lesson-group-name">${groupName}</div>
                    <div class="lesson-group-info">
                        <div class="lesson-stats">
                            <div class="lesson-stat-item">📚 ${group.lessons.length} Lessons</div>
                            <div class="lesson-stat-item">⏱️ ${totalPeriods} Periods</div>
                            <div class="lesson-stat-item">👨‍🏫 ${uniqueTeachers.size} Teachers</div>
                        </div>
                    </div>
                </div>
                <div class="lesson-group-content">
                    <table class="lesson-table">
                        <thead>
                            <tr>
                                <th>Teachers</th>
                                <th>Subjects</th>
                                <th>Lessons/Week</th>
                                <th>Length</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${group.lessons.map(l => `
                                <tr>
                                    <td>
                                        <div class="lesson-teachers">${l.teachers.map(t => t.name).join(', ')}</div>
                                        <div class="lesson-badges">
                                            ${l.class_groups.length > 1 ? '<span class="badge badge-blue">Joint Class</span>' : ''}
                                        </div>
                                    </td>
                                    <td>
                                        <div class="lesson-subjects">${l.subjects.map(s => s.name).join(', ')}</div>
                                    </td>
                                    <td>${l.lessons_per_week}</td>
                                    <td>${l.length_per_lesson === 2 ? 'Double Period' : l.length_per_lesson === 3 ? 'Triple Period' : 'Single Period'}</td>
                                    <td>
                                        <button class="btn-icon" onclick="deleteLesson(${l.id})">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

function renderTeacherWise(container) {
    // Group lessons by Teacher
    const teachers = {};
    allLessons.forEach(lesson => {
        lesson.teachers.forEach(t => {
            if (!teachers[t.name]) {
                teachers[t.name] = {
                    info: t,
                    lessons: []
                };
            }
            teachers[t.name].lessons.push(lesson);
        });
    });

    let html = '';
    Object.keys(teachers).sort().forEach(teacherName => {
        const teacher = teachers[teacherName];
        const totalPeriods = teacher.lessons.reduce((sum, l) => sum + l.lessons_per_week, 0);

        html += `
            <div class="lesson-group-card">
                <div class="lesson-group-header">
                    <div class="lesson-group-name">${teacherName}</div>
                    <div class="lesson-stats">
                        <div class="lesson-stat-item">⏱️ ${totalPeriods} Assigned Periods / ${teacher.info.max_hours_per_week} Max</div>
                    </div>
                </div>
                <div class="lesson-group-content">
                    <table class="lesson-table">
                        <thead>
                            <tr>
                                <th>Classes</th>
                                <th>Subjects</th>
                                <th>Lessons/Week</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${teacher.lessons.map(l => `
                                <tr>
                                    <td>${l.class_groups.map(g => g.name).join(', ')}</td>
                                    <td>${l.subjects.map(s => s.name).join(', ')}</td>
                                    <td>${l.lessons_per_week}</td>
                                    <td>
                                        <button class="btn-icon" onclick="deleteLesson(${l.id})">🗑️</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    });
    container.innerHTML = html;
}

// Bulk Import functions
function openBulkImportModal() {
    document.getElementById('bulkImportModal').style.display = 'flex';
}

function closeBulkImportModal() {
    document.getElementById('bulkImportModal').style.display = 'none';
}

async function submitBulkImport() {
    const text = document.getElementById('bulkImportText').value;
    const clearExisting = document.getElementById('clearExistingLessons').checked;

    if (!text.trim()) {
        alert('Please enter some lesson data');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/lessons/bulk-import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, clear_existing: clearExisting })
        });

        const result = await response.json();
        if (response.ok) {
            let msg = `Successfully imported ${result.success_count} lessons.`;
            if (result.fail_count > 0) {
                msg += `\nFailed: ${result.fail_count}\nErrors:\n${result.errors.slice(0, 5).join('\n')}`;
            }
            alert(msg);
            closeBulkImportModal();
            loadLessons();
        } else {
            alert('Import failed: ' + (result.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Import error:', error);
        alert('Import failed: Failed to fetch. Make sure the backend server is running.');
    }
}

async function deleteLesson(id) {
    if (!confirm('Are you sure you want to delete this workload configuration?')) return;

    try {
        const response = await fetch(`${API_BASE}/lessons/${id}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            loadLessons();
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Failed to delete lesson: ' + error.message);
    }
}

// Placeholder for Add New Lesson - can be expanded to a full modal
function openAddLessonModal() {
    alert('Use Bulk Import for now to add lessons in the format:\nTeacher, Class, Subject, # Periods');
}

// Make functions globally accessible
window.openBulkImportModal = openBulkImportModal;
window.closeBulkImportModal = closeBulkImportModal;
window.submitBulkImport = submitBulkImport;
window.setLessonView = setLessonView;
window.deleteLesson = deleteLesson;
window.openAddLessonModal = openAddLessonModal;
window.loadLessons = loadLessons;
