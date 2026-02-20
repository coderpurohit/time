// Quick fix to test if teachers load
console.log('Testing teacher loading...');

fetch('http://localhost:8000/api/teachers/')
    .then(r => r.json())
    .then(teachers => {
        console.log('Teachers loaded:', teachers.length);
        console.log('First teacher:', teachers[0]);
        
        // Check if container exists
        const container = document.getElementById('teachersListContainer');
        console.log('Container found:', !!container);
        
        if (container) {
            container.innerHTML = `<div style="padding: 20px;">Found ${teachers.length} teachers!</div>`;
        }
    })
    .catch(err => console.error('Error:', err));
