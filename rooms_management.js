// Rooms Management Functions

async function editRoom(roomId) {
    try {
        const response = await fetch(`${API_BASE}/rooms/${roomId}`);
        const room = await response.json();
        
        document.getElementById('roomId').value = room.id;
        document.getElementById('roomName').value = room.name;
        document.getElementById('roomType').value = room.room_type;
        document.getElementById('roomCapacity').value = room.capacity;
        document.getElementById('roomResources').value = room.resources || '';
        
        document.getElementById('roomModalTitle').textContent = 'Edit Room';
        document.getElementById('roomModal').style.display = 'flex';
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error loading room', 'error');
    }
}

async function deleteRoom(roomId) {
    if (!confirm('Are you sure you want to delete this room?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/rooms/${roomId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showStatus('Room deleted successfully!', 'success');
            loadRooms();
        } else {
            showStatus('Failed to delete room', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Error: ' + error.message, 'error');
    }
}
