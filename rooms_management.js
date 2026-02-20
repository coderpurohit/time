// Rooms Management JavaScript

let allRooms = [];
let roomUtilization = {};

// Load rooms when page loads
async function loadRooms() {
    try {
        const response = await fetch('http://localhost:8000/api/rooms/');
        if (!response.ok) throw new Error('Failed to load rooms');
        
        allRooms = await response.json();
        
        // Get utilization data
        await loadRoomUtilization();
        
        renderRoomsTable(allRooms);
        
        // Mark tab as complete if rooms exist
        if (allRooms.length > 0) {
            document.querySelector('[data-step="rooms"]').classList.add('completed');
        }
    } catch (error) {
        console.error('Error loading rooms:', error);
        document.getElementById('roomsTableBody').innerHTML = `
            <tr><td colspan="6" style="text-align: center; color: red;">
                Error loading rooms. Make sure backend is running.
            </td></tr>
        `;
    }
}

// Load room utilization (how many times each room is used)
async function loadRoomUtilization() {
    try {
        const response = await fetch('http://localhost:8000/api/timetables/latest');
        if (!response.ok) return;
        
        const timetable = await response.json();
        roomUtilization = {};
        
        // Count entries per room
        timetable.entries.forEach(entry => {
            if (entry.room) {
                const roomId = entry.room.id;
                roomUtilization[roomId] = (roomUtilization[roomId] || 0) + 1;
            }
        });
    } catch (error) {
        console.error('Error loading utilization:', error);
    }
}

// Render rooms table
function renderRoomsTable(rooms) {
    const tbody = document.getElementById('roomsTableBody');
    
    if (rooms.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="6" style="text-align: center; padding: 40px; color: #666;">
                <i class="fas fa-door-open" style="font-size: 48px; opacity: 0.3; margin-bottom: 10px;"></i>
                <p>No rooms found. Click "Add Room" to create one.</p>
            </td></tr>
        `;
        return;
    }
    
    tbody.innerHTML = rooms.map(room => {
        const typeBadge = {
            'LectureHall': '<span class="badge" style="background: #dbeafe; color: #1e40af;">Lecture Hall</span>',
            'Lab': '<span class="badge" style="background: #fce7f3; color: #be185d;">Lab</span>',
            'Seminar': '<span class="badge" style="background: #d1fae5; color: #065f46;">Seminar</span>'
        }[room.type] || room.type;
        
        const resources = Array.isArray(room.resources) && room.resources.length > 0
            ? room.resources.join(', ')
            : '<span style="color: #9ca3af;">None</span>';
        
        const usage = roomUtilization[room.id] || 0;
        const maxSlots = 25; // Total slots per week
        const utilizationPct = maxSlots > 0 ? (usage / maxSlots * 100).toFixed(0) : 0;
        
        let utilizationBadge = '';
        if (utilizationPct >= 80) {
            utilizationBadge = `<span class="badge" style="background: #fee2e2; color: #991b1b;">${utilizationPct}% (${usage}/${maxSlots})</span>`;
        } else if (utilizationPct >= 50) {
            utilizationBadge = `<span class="badge" style="background: #fef3c7; color: #92400e;">${utilizationPct}% (${usage}/${maxSlots})</span>`;
        } else {
            utilizationBadge = `<span class="badge" style="background: #d1fae5; color: #065f46;">${utilizationPct}% (${usage}/${maxSlots})</span>`;
        }
        
        return `
            <tr>
                <td><strong>${room.name}</strong></td>
                <td>${typeBadge}</td>
                <td>${room.capacity} seats</td>
                <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${resources}</td>
                <td>${utilizationBadge}</td>
                <td>
                    <button class="btn-icon" onclick="editRoom(${room.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon btn-danger" onclick="deleteRoom(${room.id}, '${room.name}')" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Filter rooms
function filterRooms() {
    const searchTerm = document.getElementById('roomSearch').value.toLowerCase();
    const typeFilter = document.getElementById('roomTypeFilter').value;
    
    const filtered = allRooms.filter(room => {
        const matchesSearch = room.name.toLowerCase().includes(searchTerm);
        const matchesType = !typeFilter || room.type === typeFilter;
        return matchesSearch && matchesType;
    });
    
    renderRoomsTable(filtered);
}

// Open modal for adding room
function openRoomModal() {
    document.getElementById('roomModalTitle').textContent = 'Add Room';
    document.getElementById('roomForm').reset();
    document.getElementById('roomId').value = '';
    document.getElementById('roomModal').style.display = 'flex';
}

// Open modal for editing room
async function editRoom(id) {
    try {
        const response = await fetch(`http://localhost:8000/api/rooms/${id}`);
        if (!response.ok) throw new Error('Failed to load room');
        
        const room = await response.json();
        
        document.getElementById('roomModalTitle').textContent = 'Edit Room';
        document.getElementById('roomId').value = room.id;
        document.getElementById('roomName').value = room.name;
        document.getElementById('roomType').value = room.type;
        document.getElementById('roomCapacity').value = room.capacity;
        
        // Convert resources array to comma-separated string
        const resourcesStr = Array.isArray(room.resources) ? room.resources.join(', ') : '';
        document.getElementById('roomResources').value = resourcesStr;
        
        document.getElementById('roomModal').style.display = 'flex';
    } catch (error) {
        console.error('Error loading room:', error);
        alert('Failed to load room details');
    }
}

// Close modal
function closeRoomModal() {
    document.getElementById('roomModal').style.display = 'none';
}

// Save room (create or update)
async function saveRoom(event) {
    event.preventDefault();
    
    const id = document.getElementById('roomId').value;
    
    // Parse resources from comma-separated string to array
    const resourcesInput = document.getElementById('roomResources').value;
    const resources = resourcesInput
        ? resourcesInput.split(',').map(r => r.trim()).filter(r => r.length > 0)
        : [];
    
    const data = {
        name: document.getElementById('roomName').value,
        type: document.getElementById('roomType').value,
        capacity: parseInt(document.getElementById('roomCapacity').value),
        resources: resources
    };
    
    try {
        const url = id ? `http://localhost:8000/api/rooms/${id}` : 'http://localhost:8000/api/rooms/';
        const method = id ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to save room');
        }
        
        closeRoomModal();
        await loadRooms();
        
        showNotification(id ? 'Room updated successfully!' : 'Room created successfully!', 'success');
    } catch (error) {
        console.error('Error saving room:', error);
        alert('Error: ' + error.message);
    }
}

// Delete room
async function deleteRoom(id, name) {
    if (!confirm(`Are you sure you want to delete "${name}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        const response = await fetch(`http://localhost:8000/api/rooms/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete room');
        
        await loadRooms();
        showNotification('Room deleted successfully!', 'success');
    } catch (error) {
        console.error('Error deleting room:', error);
        alert('Failed to delete room. It may be used in timetable entries.');
    }
}

// Show notification
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
    document.addEventListener('DOMContentLoaded', loadRooms);
} else {
    loadRooms();
}
