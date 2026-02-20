// Dashboard JavaScript

// Sidebar Toggle
const sidebarToggle = document.getElementById('sidebarToggle');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const sidebar = document.querySelector('.sidebar');

if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        const icon = sidebarToggle.querySelector('i');
        if (sidebar.classList.contains('collapsed')) {
            icon.classList.remove('fa-chevron-left');
            icon.classList.add('fa-chevron-right');
        } else {
            icon.classList.remove('fa-chevron-right');
            icon.classList.add('fa-chevron-left');
        }
    });
}

// Mobile Menu Toggle
if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });
}

// Navigation Handling
const navItems = document.querySelectorAll('.nav-item[data-page]');
navItems.forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const page = item.getAttribute('data-page');
        
        // Remove active class from all nav items
        navItems.forEach(nav => nav.classList.remove('active'));
        
        // Add active class to clicked item
        item.classList.add('active');
        
        // Handle navigation based on page
        handleNavigation(page);
    });
});

// Quick Actions
const actionCards = document.querySelectorAll('.action-card');
actionCards.forEach(card => {
    card.addEventListener('click', () => {
        const action = card.getAttribute('data-action');
        handleQuickAction(action);
    });
});

// Handle Navigation
function handleNavigation(page) {
    switch(page) {
        case 'dashboard':
            // Already on dashboard
            break;
        case 'timetables':
            // Navigate to timetables page
            window.location.href = 'timetable_page.html';
            break;
        case 'calendar':
            // Navigate to calendar view
            console.log('Navigate to calendar');
            break;
        case 'reports':
            // Navigate to reports
            console.log('Navigate to reports');
            break;
        case 'users':
            // Navigate to users management
            console.log('Navigate to users');
            break;
        case 'master-data':
            // Navigate to master data
            console.log('Navigate to master data');
            break;
        case 'settings':
            // Navigate to settings
            console.log('Navigate to settings');
            break;
        case 'support':
            // Open support
            console.log('Open support');
            break;
        case 'help':
            // Open help docs
            window.open('https://docs.timetablemaster.com', '_blank');
            break;
        case 'demo':
            // Schedule demo
            console.log('Schedule demo');
            break;
    }
}

// Handle Quick Actions
function handleQuickAction(action) {
    switch(action) {
        case 'timetables':
            window.location.href = 'timetable_page.html';
            break;
        case 'reports':
            console.log('Open reports');
            break;
        case 'users':
            console.log('Open users management');
            break;
        case 'calendar':
            console.log('Open calendar');
            break;
    }
}

// Form Submission - Institute Profile
const saveBtn = document.querySelector('.btn-save');
if (saveBtn) {
    saveBtn.addEventListener('click', () => {
        const instituteName = document.getElementById('instituteName').value;
        const instituteType = document.getElementById('instituteType').value;
        const city = document.getElementById('city').value;
        const website = document.getElementById('website').value;
        
        // Validate required fields
        if (!instituteName || !instituteType || !city) {
            alert('Please fill in all required fields (*)');
            return;
        }
        
        // Save profile data (you can integrate with your backend here)
        const profileData = {
            instituteName,
            instituteType,
            city,
            website
        };
        
        console.log('Saving profile:', profileData);
        
        // Show success message
        showNotification('Profile saved successfully!', 'success');
        
        // You can send this to your backend API here
        // fetch('/api/profile', {
        //     method: 'POST',
        //     headers: { 'Content-Type': 'application/json' },
        //     body: JSON.stringify(profileData)
        // });
    });
}

// Request Free Trial
const requestTrialBtn = document.getElementById('requestTrialBtn');
if (requestTrialBtn) {
    requestTrialBtn.addEventListener('click', () => {
        // Handle free trial request
        console.log('Request free trial');
        alert('Thank you for your interest! We will contact you soon about the free trial.');
    });
}

// Upgrade Button
const upgradeBtn = document.querySelector('.upgrade-btn');
if (upgradeBtn) {
    upgradeBtn.addEventListener('click', () => {
        handleUpgrade();
    });
}

// Premium Upgrade Button
const btnPremium = document.querySelector('.btn-premium');
if (btnPremium) {
    btnPremium.addEventListener('click', () => {
        handleUpgrade();
    });
}

function handleUpgrade() {
    console.log('Navigate to upgrade page');
    // You can redirect to upgrade page or show upgrade modal
    alert('Redirecting to upgrade plans...');
}

// Help Buttons
const btnWhatsapp = document.querySelector('.btn-whatsapp');
const btnCall = document.querySelector('.btn-call');

if (btnWhatsapp) {
    btnWhatsapp.addEventListener('click', () => {
        const phoneNumber = '919110449907';
        window.open(`https://wa.me/${phoneNumber}`, '_blank');
    });
}

if (btnCall) {
    btnCall.addEventListener('click', () => {
        window.location.href = 'tel:+919110449907';
    });
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notification if any
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    `;
    
    if (type === 'success') {
        notification.style.background = '#10B981';
    } else if (type === 'error') {
        notification.style.background = '#EF4444';
    } else {
        notification.style.background = '#3B82F6';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Load schedule preview
async function loadSchedulePreview() {
    const schedulePreview = document.getElementById('schedulePreview');
    if (!schedulePreview) return;

    schedulePreview.innerHTML = '<div class="schedule-empty"><i class="fas fa-spinner fa-spin"></i><p>Loading schedule...</p></div>';

    try {
        const response = await fetch('http://localhost:8000/api/timetables/latest');
        if (!response.ok) {
            throw new Error('No timetable found');
        }

        const data = await response.json();
        if (data && data.entries && data.entries.length > 0) {
            // Show a preview of today's schedule
            const today = new Date().toLocaleDateString('en-US', { weekday: 'long' });
            const todaySlots = data.entries.filter(entry => 
                entry.time_slot && entry.time_slot.day === today
            ).slice(0, 3); // Show first 3 slots

            if (todaySlots.length > 0) {
                let previewHTML = '<div class="schedule-preview-content">';
                todaySlots.forEach(slot => {
                    const time = slot.time_slot ? `${slot.time_slot.start_time || 'N/A'}` : 'N/A';
                    const subject = slot.subject?.name || 'Unknown';
                    previewHTML += `
                        <div class="schedule-preview-item">
                            <div class="time">${time}</div>
                            <div class="subject">${subject}</div>
                        </div>
                    `;
                });
                previewHTML += `<a href="timetable_page.html" style="display: block; text-align: center; margin-top: 1rem; color: var(--primary-purple); text-decoration: none; font-weight: 600;">View Full Schedule →</a></div>`;
                schedulePreview.innerHTML = previewHTML;
            } else {
                schedulePreview.innerHTML = `
                    <div class="schedule-empty">
                        <i class="fas fa-calendar-check"></i>
                        <p>No classes scheduled for today.</p>
                        <a href="timetable_page.html" style="display: inline-block; margin-top: 1rem; color: var(--primary-purple); text-decoration: none; font-weight: 600;">View Full Timetable →</a>
                    </div>
                `;
            }
        } else {
            throw new Error('Timetable is empty');
        }
    } catch (error) {
        schedulePreview.innerHTML = `
            <div class="schedule-empty">
                <i class="fas fa-building"></i>
                <p>There is no published timetable at the moment. Your schedule will appear once timetables are published.</p>
                <button class="btn-load-schedule" onclick="loadSchedulePreview()">
                    <i class="fas fa-sync"></i>
                    Try Again
                </button>
            </div>
        `;
    }
}

// Load saved profile data on page load
window.addEventListener('DOMContentLoaded', () => {
    // Optionally auto-load schedule preview
    // loadSchedulePreview();
    // You can load saved profile data from localStorage or API
    const savedProfile = localStorage.getItem('instituteProfile');
    if (savedProfile) {
        try {
            const profile = JSON.parse(savedProfile);
            if (profile.instituteName) {
                document.getElementById('instituteName').value = profile.instituteName;
            }
            if (profile.instituteType) {
                document.getElementById('instituteType').value = profile.instituteType;
            }
            if (profile.city) {
                document.getElementById('city').value = profile.city;
            }
            if (profile.website) {
                document.getElementById('website').value = profile.website;
            }
        } catch (e) {
            console.error('Error loading profile:', e);
        }
    }
});

// Save profile to localStorage when saved
if (saveBtn) {
    const originalClick = saveBtn.onclick;
    saveBtn.addEventListener('click', () => {
        const profileData = {
            instituteName: document.getElementById('instituteName').value,
            instituteType: document.getElementById('instituteType').value,
            city: document.getElementById('city').value,
            website: document.getElementById('website').value
        };
        localStorage.setItem('instituteProfile', JSON.stringify(profileData));
    });
}

// Responsive sidebar handling
function handleResize() {
    if (window.innerWidth <= 768) {
        sidebar.classList.add('mobile');
    } else {
        sidebar.classList.remove('mobile');
    }
}

window.addEventListener('resize', handleResize);
handleResize();

// Close sidebar on mobile when clicking outside
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 && sidebar.classList.contains('mobile')) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});
