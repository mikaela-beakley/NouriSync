console.log('index.js loaded');

// Function to format date from timestamp (not needed bc server already formats it but if we WERE using unix timestamp)
// function formatDate(timestamp) {
//     const date = new Date(timestamp);
//     const options = { weekday: 'long', month: 'long', day: 'numeric' };
//     return date.toLocaleDateString('en-US', options);
// }

// Function to get risk indicator class
function getRiskClass(riskScore) {
    switch(riskScore.toLowerCase()) {
        case 'low': return 'low-risk';
        case 'moderate': return 'medium-risk';
        case 'high': return 'high-risk';
        default: return 'low-risk';
    }
}

// Function to create a log entry HTML
function createLogHTML(log) {
    const formattedDate = log.timestamp;
    const riskClass = getRiskClass(log.ai_response.risk_score);
    const riskFactorsText = log.ai_response.risk_factors.join('<br>');

    // Create plan items
    const planItems = log.ai_response.plan.map(item => 
        `<li>
            <strong>${item.step}</strong>
            <br><em>Rationale:</em> ${item.rationale}
            <br><em>Source:</em> ${item.source}
        </li>`
    ).join('');

    const emotionsList = log.ai_response.emotions_list.map(emotion => 
        `<li>${emotion}</li>`
    ).join('');
    
    return `
        <div class="log">
            <div class="log-top-info">
                <h5>${formattedDate}</h5>
            </div>
            <div class="log-bottom-info">
                <div class="risk-indicator ${riskClass}">${log.ai_response.risk_score.charAt(0).toUpperCase() + log.ai_response.risk_score.slice(1)} Risk</div>
                <p>${riskFactorsText}</p>
                
                <button class="collapsable" onclick="toggleLogContent(this)">
                    <svg width="28" height="18" viewBox="0 0 28 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M26.0577 16.25L14.0385 3.75L2.01928 16.25" stroke="black" stroke-width="5"/>
                    </svg>
                </button>
            </div>
            <div class="log-content" style="display: none;">
                <h5> Emotions </h5>
                <ol class="emotions">
                    ${emotionsList}
                </ol>
                <h5>Recommended plan</h5>
                <ol class="log-plan">
                    ${planItems}
                </ol>
            </div>
        </div>
    `;
}

// Function to toggle log content visibility
function toggleLogContent(button) {
    const logContent = button.closest('.log').querySelector('.log-content');
    const svg = button.querySelector('svg path');
    
    if (logContent.style.display === 'none') {
        logContent.style.display = 'block';
        // Rotate arrow down
        svg.setAttribute('d', 'M27.5 2.75L15 15.25L2.5 2.75');
    } else {
        logContent.style.display = 'none';
        // Rotate arrow up
        svg.setAttribute('d', 'M26.0577 16.25L14.0385 3.75L2.01928 16.25');
    }
}

// Function to load and display logs
async function loadLogs() {
    try {
        const response = await fetch('/logs');
        const logs = await response.json();
        console.log(logs);
        const logsContainer = document.getElementById('logs-container');
        
        if (logs.length === 0) {
            logsContainer.innerHTML = '<div class="no-logs-message">No logs yet. <a href="/questionnaire">Create your first log!</a></div>';
            return;
        }
        
        // Sort logs by ID in descending order (newest first)
        logs.sort((a, b) => b.id - a.id);
        
        // Generate HTML for all logs
        const logsHTML = logs.map(log => createLogHTML(log)).join('');
        logsContainer.innerHTML = logsHTML;
        
    } catch (error) {
        console.error('Error loading logs:', error);
        const logsContainer = document.getElementById('logs-container');
        logsContainer.innerHTML = '<div class="error-message">Error loading logs. Please try again.</div>';
    }
}

// Function to load and display streak information
async function loadStreak() {
    try {
        const response = await fetch('/streak');
        const streakData = await response.json();
        console.log('Streak data:', streakData);
        
        updateStreakDisplay(streakData);
        
    } catch (error) {
        console.error('Error loading streak:', error);
        // Set default/error state
        updateStreakDisplay({
            current_streak: 0,
            logged_today: false,
            last_7_days: [false, false, false, false, false, false, false]
        });
    }
}

// Function to update the streak display
function updateStreakDisplay(streakData) {
    const streakContainer = document.getElementById('streak-container');
    const streakNumber = document.getElementById('streak-number');
    const streakMessage = document.getElementById('streak-message');
    const streakDays = document.getElementById('streak-days');
    
    // Update streak number
    streakNumber.textContent = streakData.current_streak;
    
    // Update message and styling based on whether logged today
    if (streakData.logged_today) {
        // Active state - orange/fire colors
        streakContainer.classList.remove('inactive');
        if (streakData.current_streak === 0) {
            streakMessage.textContent = "Great start! Keep it up!";
        } else if (streakData.current_streak === 1) {
            streakMessage.textContent = "1 day streak! You got this!";
        } else {
            streakMessage.textContent = `${streakData.current_streak} day streak! You got this!`;
        }
    } else {
        // Inactive state - gray colors
        streakContainer.classList.add('inactive');
        streakMessage.textContent = "Add a log today to keep your streak going!";
    }
    
    // Update day bubbles
    const dayElements = streakDays.querySelectorAll('.day');
    const dayLabels = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    
    dayElements.forEach((dayElement, index) => {
        dayElement.textContent = dayLabels[index];
        if (streakData.last_7_days[index]) {
            dayElement.classList.add('completed');
        } else {
            dayElement.classList.remove('completed');
        }
    });
}

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, loading data...');
    
    // Load logs and streak data
    loadLogs();
    loadStreak();
});

// Make toggleLogContent available globally for onclick handlers
window.toggleLogContent = toggleLogContent;

function exportLogs() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    const logs = document.querySelectorAll('.log');
    let y = 20; 

    const date = new Date().toLocaleDateString('en-US', {
        month: 'long',
        day: '2-digit',
        year: 'numeric'
    }).replace(/ /g, '-');

    logs.forEach((logElem, i) => {
        if (i != 0) {
            doc.addPage();
            y = 20;
        }

        const dateText = logElem.querySelector('.log-top-info h5')?.innerText || 'Date unknown';
        const riskText = logElem.querySelector('.risk-indicator')?.innerText || 'Risk unknown';
        const riskFactorsElem = logElem.querySelector('.log-bottom-info p');
        const riskFactors = riskFactorsElem?.innerText?.trim() || 'No risk factors listed';
        const planItems = logElem.querySelectorAll('.log-plan li');

        doc.setFont("Helvetica", "bold");
        doc.text(`${dateText} — ${riskText}`, 10, y);
        y += 10;

        doc.setFont("Helvetica", "normal");
        const riskFactorLines = doc.splitTextToSize(`Risk Factors: ${riskFactors}`, 180);
        doc.text(riskFactorLines, 10, y);
        y += riskFactorLines.length * 6;

        y+=20;

        if (planItems.length > 0) {
            doc.setFont("Helvetica", "normal");
            doc.text("Recommended Plan:", 10, y);
            y += 6;

            doc.setFont("Helvetica", "normal");
            planItems.forEach(item => {
                const text = item.innerText;
                const lines = doc.splitTextToSize(text, 180);
                doc.text(lines, 14, y);
                y += lines.length * 6;
            });
        }

        y += 10; 

    });

    doc.save(`logs-${date}.pdf`);
}

