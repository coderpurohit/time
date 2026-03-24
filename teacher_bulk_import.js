// Teacher Bulk Import Functions

function openTeacherBulkImportModal() {
    document.getElementById('teacherBulkImportModal').style.display = 'flex';
    // Reset form
    document.getElementById('teacherCsvFile').value = '';
    document.getElementById('clearExistingTeachers').checked = false;
}

function closeTeacherBulkImportModal() {
    document.getElementById('teacherBulkImportModal').style.display = 'none';
}

async function submitTeacherBulkImport() {
    console.log('=== submitTeacherBulkImport CALLED ===');
    console.log('This is the TEACHER import function, not lessons!');
    
    const fileInput = document.getElementById('teacherCsvFile');
    const clearExisting = document.getElementById('clearExistingTeachers').checked;
    
    console.log('File input element:', fileInput);
    console.log('Clear existing checkbox:', clearExisting);
    
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Please select a CSV file to upload');
        return;
    }
    
    const file = fileInput.files[0];
    console.log('Selected file:', file.name, file.type, file.size);
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.txt')) {
        alert('Please upload a CSV or TXT file');
        return;
    }
    
    // Confirm if clearing existing
    if (clearExisting) {
        const confirmed = confirm(
            '⚠️ WARNING: This will DELETE all existing teachers!\n\n' +
            'Are you sure you want to continue?'
        );
        if (!confirmed) {
            return;
        }
    }
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('dataset', 'teachers');
        formData.append('file', file);
        formData.append('force_clear_existing', clearExisting ? 'true' : 'false');
        
        // Debug logging
        console.log('=== TEACHER BULK IMPORT DEBUG ===');
        console.log('Dataset:', 'teachers');
        console.log('File:', file.name);
        console.log('Clear existing:', clearExisting);
        console.log('FormData entries:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ':', pair[1]);
        }
        console.log('API endpoint:', `${API_BASE}/import/`);
        
        // Show loading
        const importBtn = event.target;
        const originalText = importBtn.innerHTML;
        importBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Importing...';
        importBtn.disabled = true;
        
        // Upload to API
        const response = await fetch(`${API_BASE}/import/`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        console.log('Response:', result);
        
        // Restore button
        importBtn.innerHTML = originalText;
        importBtn.disabled = false;
        
        if (response.ok) {
            let message = result.message || `Successfully imported ${result.added} teachers`;
            
            if (result.updated > 0) {
                message += `\nUpdated: ${result.updated}`;
            }
            if (result.skipped > 0) {
                message += `\nSkipped: ${result.skipped}`;
            }
            if (result.cleared) {
                message += `\nCleared: ${result.cleared} old teachers`;
            }
            if (result.lessons_cleared) {
                message += `\nLessons cleared: ${result.lessons_cleared}`;
            }
            if (result.timetable_cleared) {
                message += `\nTimetable cleared (regenerate required)`;
            }
            if (result.errors && result.errors.length > 0) {
                message += `\n\nErrors:\n${result.errors.join('\n')}`;
            }
            
            alert(message);
            closeTeacherBulkImportModal();
            
            // Reload teachers list
            if (typeof loadTeachersInPage === 'function') {
                loadTeachersInPage();
            }
        } else {
            alert('Import failed: ' + (result.detail || result.message || 'Unknown error'));
        }
        
    } catch (error) {
        console.error('Import error:', error);
        alert('Import failed: ' + error.message);
    }
}

// Make functions globally accessible
window.openTeacherBulkImportModal = openTeacherBulkImportModal;
window.closeTeacherBulkImportModal = closeTeacherBulkImportModal;
window.submitTeacherBulkImport = submitTeacherBulkImport;
