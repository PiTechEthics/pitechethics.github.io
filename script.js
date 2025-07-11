// Updated script to fix the date comparison issue
document.addEventListener('DOMContentLoaded', function() {
    // Get all session elements
    const sessionElements = document.querySelectorAll('.session');
    
    // Define session dates (format: YYYY-MM-DD)
    const sessions = [
        { date: '2025-06-12', element: sessionElements[0] },
        { date: '2025-06-26', element: sessionElements[1] },
        { date: '2025-07-10', element: sessionElements[2] },
        { date: '2025-07-17', element: sessionElements[3] },
        { date: '2025-07-24', element: sessionElements[4] },
        { date: '2025-07-31', element: sessionElements[5] },
        { date: '2025-08-07', element: sessionElements[6] },
        { date: '2025-08-14', element: sessionElements[7] }
    ];

    // Use a mock date for testing (Today is June 26, 2025)
    // Remove this line and use the line below it when the site goes live in 2025
    // const today = new Date('2025-06-26T12:00:00');
    const today = new Date();
    
    // Improved helper function to compare dates while normalizing timezone issues
    const isSameDay = (date1, date2) => {
        // Convert both dates to their local date strings in YYYY-MM-DD format
        const d1 = new Date(date1);
        const d2 = new Date(date2);
        
        return d1.getFullYear() === d2.getFullYear() &&
               d1.getMonth() === d2.getMonth() &&
               d1.getDate() === d2.getDate();
    };
    
    // Find today's session if there is one
    let todaySession = null;
    for (const session of sessions) {
        // Create date at noon to avoid timezone issues
        const sessionDate = new Date(session.date + 'T12:00:00');
        if (isSameDay(sessionDate, today)) {
            todaySession = session;
            break;
        }
    }
    
    // Find the next upcoming session (excluding today)
    let nextSession = null;
    let closestDiff = Infinity;
    
    for (const session of sessions) {
        // Create date at noon to avoid timezone issues
        const sessionDate = new Date(session.date + 'T12:00:00');
        
        // Calculate difference in days, not milliseconds
        const todayDateOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const sessionDateOnly = new Date(sessionDate.getFullYear(), sessionDate.getMonth(), sessionDate.getDate());
        const timeDiff = sessionDateOnly - todayDateOnly;
        
        // Only consider future sessions that aren't today
        if (timeDiff > 0 && !isSameDay(sessionDate, today) && timeDiff < closestDiff) {
            closestDiff = timeDiff;
            nextSession = session;
        }
    }
    
    // If there's a session today, highlight it
    if (todaySession) {
        todaySession.element.classList.add('today-session');
    } 
    // If there's no session today but there is an upcoming session, highlight that
    else if (nextSession) {
        nextSession.element.classList.add('next-session');
    } 
    
    // Handle smooth scrolling for the schedule link
    document.addEventListener('click', function(e) {
        const targetLink = e.target.closest('a[href="#schedule"]');
        if (targetLink) {
            e.preventDefault();
            
            // Scroll priority: today's session > next session > schedule heading
            if (todaySession) {
                todaySession.element.scrollIntoView({ behavior: 'smooth' });
            } else if (nextSession) {
                nextSession.element.scrollIntoView({ behavior: 'smooth' });
            } else {
                document.getElementById('schedule').scrollIntoView({ behavior: 'smooth' });
            }
            history.pushState(null, null, '#schedule');
        }
    });
});
