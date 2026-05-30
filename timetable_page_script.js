// Timetable Page Script - Core Functions

// Generate new timetable
async function generateNewTimetable() {
    try {
        showStatus('Generating timetable... This may take a moment.', 'info');
        
        const response = await fetch(`${API_BASE}/solvers/generate?method=csp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            showStatus('Timetable generated successfully!', 'success');
            
            // Reload the timetable display
            if (typeof loadTimetableInline === 'function') {
                loadTimetableInline();
            }
        } else {
            const error = await response.json();
            showStatus('Generation failed: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Load subjects
async function loadSubjects() {
    try {
        console.log('Loading subjects from:', `${API_BASE}/subjects`);
        const response = await fetch(`${API_BASE}/subjects`);
        const subjects = await response.json();
        console.log('Subjects loaded:', subjects.length);
        
        const tbody = document.getElementById('subjectsTableBody');
        if (!tbody) {
            console.error('subjectsTableBody not found');
            return;
        }
        
        if (subjects.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">No subjects found</td></tr>';
            return;
        }
        
        tbody.innerHTML = subjects.map(s => `
            <tr data-type="${s.is_lab ? 'lab' : 'theory'}">
                <td>${s.code}</td>
                <td>${s.name}</td>
                <td>${s.credits}</td>
                <td>${s.is_lab ? 'Lab' : 'Theory'}</td>
                <td>${s.duration_slots} periods</td>
                <td>${s.teacher?.name || 'Unassigned'}</td>
                <td>${s.room_type}</td>
                <td>
                    <button onclick="editSubject(${s.id})" style="padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px;">Edit</button>
                    <button onclick="deleteSubject(${s.id})" style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Delete</button>
                </td>
            </tr>
        `).join('');
        console.log('Subjects table updated');
    } catch (error) {
        console.error('Error loading subjects:', error);
    }
}

// Load classes
async function loadClasses() {
    try {
        console.log('Loading classes from:', `${API_BASE}/class-groups`);
        const response = await fetch(`${API_BASE}/class-groups`);
        const classes = await response.json();
        console.log('Classes loaded:', classes.length);
        
        const tbody = document.getElementById('classesTableBody');
        if (!tbody) {
            console.error('classesTableBody not found');
            return;
        }
        
        if (classes.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px;">No classes found</td></tr>';
            return;
        }
        
        tbody.innerHTML = classes.map(c => `
            <tr>
                <td>${c.name}</td>
                <td>${c.student_count}</td>
                <td>-</td>
                <td>-</td>
                <td>
                    <button onclick="editClass(${c.id})" style="padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px;">Edit</button>
                    <button onclick="deleteClass(${c.id})" style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Delete</button>
                </td>
            </tr>
        `).join('');
        console.log('Classes table updated');
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

// Load rooms
async function loadRooms() {
    try {
        console.log('Loading rooms from:', `${API_BASE}/rooms`);
        const response = await fetch(`${API_BASE}/rooms`);
        const rooms = await response.json();
        console.log('Rooms loaded:', rooms.length);
        
        const tbody = document.getElementById('roomsTableBody');
        if (!tbody) return;
        
        if (rooms.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">No rooms found</td></tr>';
            return;
        }
        
        tbody.innerHTML = rooms.map(r => `
            <tr data-type="${r.room_type}">
                <td>${r.name}</td>
                <td>${r.room_type}</td>
                <td>${r.capacity}</td>
                <td>${r.resources || '-'}</td>
                <td>-</td>
                <td>
                    <button onclick="editRoom(${r.id})" style="padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px;">Edit</button>
                    <button onclick="deleteRoom(${r.id})" style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

// Load teachers
async function loadTeachersInPage() {
    try {
        const response = await fetch(`${API_BASE}/teachers`);
        const teachers = await response.json();
        
        const container = document.getElementById('teachersListContainer');
        if (!container) return;
        
        if (teachers.length === 0) {
            container.innerHTML = '<div style="text-align: center; padding: 30px; color: #666; grid-column: 1/-1;">No teachers found</div>';
            return;
        }
        
        container.innerHTML = teachers.map(t => `
            <div class="teacher-card">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div>
                        <div style="font-size: 16px; font-weight: 600; color: #1f2937;">${t.name}</div>
                        <div style="font-size: 12px; color: #6b7280;">${t.email}</div>
                    </div>
                    <button onclick="openDeleteTeacherModal(${t.id}, '${t.name}')" class="btn-danger" style="padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">Delete</button>
                </div>
                <div style="background: #f9fafb; padding: 10px; border-radius: 6px; font-size: 13px;">
                    <div style="margin-bottom: 5px;"><strong>Max Hours/Week:</strong> ${t.max_hours_per_week || 20}</div>
                    <div><strong>Status:</strong> <span style="color: #10b981;">Active</span></div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading teachers:', error);
    }
}

// Filter teachers
function filterTeachersInPage() {
    const searchTerm = document.getElementById('teacherSearchInput').value.toLowerCase();
    const cards = document.querySelectorAll('.teacher-card');
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

// Load lessons
async function loadLessons() {
    try {
        console.log('Loading lessons...');
        const response = await fetch(`${API_BASE}/lessons`);
        const lessons = await response.json();
        console.log('Lessons loaded:', lessons.length);
        
        const container = document.getElementById('lessonsList');
        if (!container) {
            console.error('lessonsList container not found');
            return;
        }
        
        if (lessons.length === 0) {
            container.innerHTML = '<div style="text-align: center; padding: 30px; color: #666;">No lessons found</div>';
            return;
        }
        
        // Group lessons by class
        const lessonsByClass = {};
        lessons.forEach(lesson => {
            const classNames = lesson.class_groups?.map(c => c.name).join(', ') || 'Unknown';
            if (!lessonsByClass[classNames]) {
                lessonsByClass[classNames] = [];
            }
            lessonsByClass[classNames].push(lesson);
        });
        
        // Build HTML
        let html = `<div style="padding: 20px;">`;
        html += `<div style="text-align: center; margin-bottom: 20px; font-weight: bold; color: #667eea;">Total: ${lessons.length} lessons</div>`;
        
        Object.keys(lessonsByClass).sort().forEach(className => {
            const classLessons = lessonsByClass[className];
            html += `<div style="margin-bottom: 20px; border: 1px solid #ddd; border-radius: 8px; padding: 15px;">`;
            html += `<h4 style="color: #667eea; margin-top: 0;">${className} (${classLessons.length} lessons)</h4>`;
            html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px;">`;
            
            classLessons.forEach(lesson => {
                const teachers = lesson.teachers?.map(t => t.name).join(', ') || 'TBD';
                const subjects = lesson.subjects?.map(s => s.name).join(', ') || 'TBD';
                html += `
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 6px; border-left: 4px solid #667eea;">
                        <div style="font-weight: 600; color: #333; margin-bottom: 5px;">${subjects}</div>
                        <div style="font-size: 0.9em; color: #666; margin-bottom: 3px;">👨‍🏫 ${teachers}</div>
                        <div style="font-size: 0.85em; color: #999;">${lesson.lessons_per_week} periods/week</div>
                    </div>
                `;
            });
            
            html += `</div></div>`;
        });
        
        html += `</div>`;
        container.innerHTML = html;
        console.log('Lessons displayed');
    } catch (error) {
        console.error('Error loading lessons:', error);
    }
}

// Set lesson view
function setLessonView(view) {
    console.log('Setting lesson view to:', view);
    
    // Update button states
    document.getElementById('view-class-wise').classList.toggle('active', view === 'class');
    document.getElementById('view-teacher-wise').classList.toggle('active', view === 'teacher');
    
    // Load lessons with the selected view
    loadLessons();
}

// Open master timetable
function openMasterTimetable() {
    window.open('master_timetable.html', '_blank');
}

// Export functions
function exportTimetableToPDF() {
    showStatus('PDF export coming soon!', 'info');
}

function exportTimetableToCSV() {
    showStatus('CSV export coming soon!', 'info');
}

// Bulk import
function openBulkImportModal() {
    const modal = document.getElementById('bulkImportModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeBulkImportModal() {
    const modal = document.getElementById('bulkImportModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function submitBulkImport() {
    const text = document.getElementById('bulkImportText').value;
    const clearExisting = document.getElementById('clearExistingLessons').checked;
    
    if (!text.trim()) {
        showStatus('Please enter lesson data', 'warning');
        return;
    }
    
    try {
        showStatus('Importing lessons...', 'info');
        
        const response = await fetch(`${API_BASE}/lessons/bulk-import`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data: text,
                clear_existing: clearExisting
            })
        });
        
        if (response.ok) {
            showStatus('Lessons imported successfully!', 'success');
            closeBulkImportModal();
            loadLessons();
        } else {
            const error = await response.json();
            showStatus('Import failed: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}

// Load factor functions
function filterLoadFactorByClass() {
    const classFilter = document.getElementById('loadFactorClassFilter').value;
    console.log('Filtering by class:', classFilter);
    
    if (typeof loadLoadFactorInline === 'function') {
        loadLoadFactorInline();
    }
}

function clearLoadFactorFilter() {
    document.getElementById('loadFactorClassFilter').value = '';
    if (typeof loadLoadFactorInline === 'function') {
        loadLoadFactorInline();
    }
}

async function uploadDocxWorkload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showStatus('Parsing DOCX file and optimizing workload...', 'info');
        
        const response = await fetch(`${API_BASE}/analytics/optimize-workload-from-docx`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showStatus('Workload optimized successfully! ' + result.message, 'success');
            
            // Reload the load factor display
            setTimeout(() => {
                if (typeof loadLoadFactorInline === 'function') {
                    loadLoadFactorInline();
                }
            }, 500);
        } else {
            const error = await response.json();
            showStatus('Failed to optimize workload: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    } finally {
        // Clear the input
        event.target.value = '';
    }
}

async function uploadComprehensiveDocx(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    showStatus('Importing DOCX file...', 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        console.log('Uploading file:', file.name);
        
        // Use the working workload-from-docx endpoint
        const response = await fetch(`${API_BASE}/analytics/workload-from-docx/0`, {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        const responseText = await response.text();
        console.log('Response:', responseText.substring(0, 300));
        
        if (!response.ok) {
            showStatus(`Upload failed: ${responseText}`, 'error');
            return;
        }
        
        try {
            const result = JSON.parse(responseText);
            showStatus(`✓ Import successful! ${result.message || ''}`, 'success');
        } catch (e) {
            showStatus('✓ Import successful!', 'success');
        }
        
        // Refresh all data
        setTimeout(() => {
            loadSubjects();
            loadTeachersInPage();
            loadClasses();
            loadRooms();
            loadLessons();
            loadLoadFactorInline();
        }, 500);
        
    } catch (error) {
        console.error('Upload error:', error);
        showStatus(`Upload failed: ${error.message}`, 'error');
    }
    
    // Clear the input
    event.target.value = '';
}
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
