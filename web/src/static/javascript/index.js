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
        case 'medium': return 'medium-risk';
        case 'high': return 'high-risk';
        default: return 'low-risk';
    }
}

// Function to create a log entry HTML
function createLogHTML(log) {
    const formattedDate = log.timestamp;
    const riskClass = getRiskClass(log.ai_response.risk_score);
    const riskFactorsText = log.ai_response.risk_factors;
    
    // Create plan items
    const planItems = log.ai_response.plan.map(item => 
        `<li>
            <strong>${item.step}</strong>
            <br><em>Rationale:</em> ${item.rationale}
            <br><em>Source:</em> ${item.source}
        </li>`
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

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, loading logs...');
    
    // Load only logs (user data stays hardcoded)
    loadLogs();
});

// Make toggleLogContent available globally for onclick handlers
window.toggleLogContent = toggleLogContent;