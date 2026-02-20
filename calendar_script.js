// Calendar Script
let currentDate = new Date();
let timetableData = [];
let classGroups = [];

// Initialize calendar
async function initCalendar() {
    await loadTimetableData();
    await loadClassGroups();
    renderCalendar();
}

// Load timetable data from API
async function loadTimetableData() {
    try {
        const response = await fetch('http://localhost:8000/api/timetables/latest');
        if (response.ok) {
            const data = await response.json();
            timetableData = data.entries || [];
            console.log('Loaded timetable entries:', timetableData.length);
        }
    } catch (error) {
        console.error('Error loading timetable:', error);
    }
}

// Load class groups for filter
async function loadClassGroups() {
    try {
        const response = await fetch('http://localhost:8000/api/class-groups/');
        if (response.ok) {
            classGroups = await response.json();
            populateClassFilter();
        }
    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

// Populate class filter dropdown
function populateClassFilter() {
    const select = document.getElementById('classFilter');
    classGroups.forEach(group => {
        const option = document.createElement('option');
        option.value = group.id;
        option.textContent = group.name;
        select.appendChild(option);
    });
}

// Render calendar
function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Update month display
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('currentMonth').textContent = `${monthNames[month]} ${year}`;
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    // Get previous month's last days
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    
    const calendarDays = document.getElementById('calendarDays');
    calendarDays.innerHTML = '';
    
    // Add previous month's days
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
        const day = prevMonthLastDay - i;
        const dayDiv = createDayElement(day, true, new Date(year, month - 1, day));
        calendarDays.appendChild(dayDiv);
    }
    
    // Add current month's days
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const isToday = isDateToday(date);
        const dayDiv = createDayElement(day, false, date, isToday);
        calendarDays.appendChild(dayDiv);
    }
    
    // Add next month's days to fill grid
    const totalCells = calendarDays.children.length;
    const remainingCells = 42 - totalCells; // 6 rows × 7 days
    for (let day = 1; day <= remainingCells; day++) {
        const dayDiv = createDayElement(day, true, new Date(year, month + 1, day));
        calendarDays.appendChild(dayDiv);
    }
}

// Create day element
function createDayElement(dayNumber, isOtherMonth, date, isToday = false) {
    const dayDiv = document.createElement('div');
    dayDiv.className = 'calendar-day';
    if (isOtherMonth) dayDiv.classList.add('other-month');
    if (isToday) dayDiv.classList.add('today');
    
    const dayNumberDiv = document.createElement('div');
    dayNumberDiv.className = 'day-number';
    dayNumberDiv.textContent = dayNumber;
    dayDiv.appendChild(dayNumberDiv);
    
    // Get events for this day
    const events = getEventsForDate(date);
    
    if (events.length > 0) {
        const eventsDiv = document.createElement('div');
        eventsDiv.className = 'day-events';
        
        // Show first 3 events
        events.slice(0, 3).forEach(event => {
            const badge = document.createElement('div');
            badge.className = 'event-badge';
            if (event.subject && event.subject.is_lab) {
                badge.classList.add('class-event');
            }
            badge.textContent = event.class_group ? event.class_group.name : 'Event';
            badge.title = `${event.subject?.name || 'Unknown'} - ${event.teacher?.name || 'TBA'}`;
            eventsDiv.appendChild(badge);
        });
        
        // Show "more" indicator
        if (events.length > 3) {
            const moreDiv = document.createElement('div');
            moreDiv.className = 'event-more';
            moreDiv.textContent = `+${events.length - 3} more`;
            eventsDiv.appendChild(moreDiv);
        }
        
        dayDiv.appendChild(eventsDiv);
    }
    
    // Click handler to show day details
    dayDiv.onclick = () => showDayDetail(date, events);
    
    return dayDiv;
}

// Get events for a specific date
function getEventsForDate(date) {
    const dayOfWeek = date.getDay();
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayName = dayNames[dayOfWeek];
    
    // Filter timetable entries for this day
    return timetableData.filter(entry => {
        return entry.time_slot && entry.time_slot.day_of_week === dayName;
    });
}

// Check if date is today
function isDateToday(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
}

// Show day detail modal
function showDayDetail(date, events) {
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    
    const dateStr = `${dayNames[date.getDay()]}, ${monthNames[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
    document.getElementById('modalDate').textContent = dateStr;
    
    const scheduleList = document.getElementById('scheduleList');
    scheduleList.innerHTML = '';
    
    if (events.length === 0) {
        scheduleList.innerHTML = '<p style="text-align: center; color: #9ca3af; padding: 40px;">No classes scheduled for this day</p>';
    } else {
        // Sort events by time
        events.sort((a, b) => {
            const timeA = a.time_slot?.start_time || '';
            const timeB = b.time_slot?.start_time || '';
            return timeA.localeCompare(timeB);
        });
        
        events.forEach(event => {
            const item = document.createElement('div');
            item.className = 'schedule-item';
            
            const timeDiv = document.createElement('div');
            timeDiv.className = 'schedule-time';
            timeDiv.innerHTML = `<i class="fas fa-clock"></i> ${event.time_slot?.start_time || 'TBA'} - ${event.time_slot?.end_time || 'TBA'}`;
            item.appendChild(timeDiv);
            
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'schedule-details';
            detailsDiv.innerHTML = `
                <div><strong>Subject:</strong> ${event.subject?.name || 'Unknown'}</div>
                <div><strong>Class:</strong> ${event.class_group?.name || 'Unknown'}</div>
                <div><strong>Teacher:</strong> ${event.teacher?.name || 'TBA'}</div>
                <div><strong>Room:</strong> ${event.room?.name || 'TBA'}</div>
            `;
            item.appendChild(detailsDiv);
            
            scheduleList.appendChild(item);
        });
    }
    
    document.getElementById('dayDetailModal').style.display = 'flex';
}

// Close day detail modal
function closeDayDetail() {
    document.getElementById('dayDetailModal').style.display = 'none';
}

// Navigation functions
function previousMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1);
    renderCalendar();
}

function nextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1);
    renderCalendar();
}

function goToToday() {
    currentDate = new Date();
    renderCalendar();
}

// Filter calendar
function filterCalendar() {
    // For now, just re-render
    // In future, implement actual filtering
    renderCalendar();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initCalendar);

// Close modal when clicking outside
document.getElementById('dayDetailModal').addEventListener('click', (e) => {
    if (e.target.id === 'dayDetailModal') {
        closeDayDetail();
    }
});
