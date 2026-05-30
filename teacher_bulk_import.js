// Teacher Bulk Import Functions

async function submitTeacherBulkImport() {
    const fileInput = document.getElementById('teacherBulkFile');
    const file = fileInput.files[0];
    const clearExisting = document.getElementById('clearExistingTeachers').checked;
    
    if (!file) {
        showStatus('Please select a file (CSV or DOCX)', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showStatus('Importing teachers...', 'info');
        
        // Determine file type and call appropriate endpoint
        let endpoint = '';
        if (file.name.toLowerCase().endsWith('.docx')) {
            endpoint = `${API_BASE}/analytics/workload-from-docx/0`;
        } else if (file.name.toLowerCase().endsWith('.csv') || file.name.toLowerCase().endsWith('.txt')) {
            endpoint = `${API_BASE}/import/teachers-csv`;
        } else {
            showStatus('Unsupported file type. Please use CSV or DOCX', 'error');
            return;
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showStatus('Teachers imported successfully!', 'success');
            closeTeacherBulkImportModal();
            loadTeachersInPage();
            
            // Reload load factor if available
            setTimeout(() => {
                if (typeof loadLoadFactorInline === 'function') {
                    loadLoadFactorInline();
                }
            }, 500);
        } else {
            const error = await response.json();
            showStatus('Import failed: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    } finally {
        // Clear the input
        fileInput.value = '';
    }
}
