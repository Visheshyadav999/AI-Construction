const API_URL = ""; 
let currentChart = null; 

function handleGoogleLogin(response) {
    const jwtToken = response.credential;
    const payload = JSON.parse(atob(jwtToken.split('.')[1]));
    const userFullName = payload.name;
    const userEmail = payload.email;
    const userPicture = payload.picture;
    console.log(`Successfully verified via Google: ${userEmail}`);
    const loginScreen = document.getElementById('publicLoginScreen');
    loginScreen.innerHTML = `
        <div class="row justify-content-center mt-5">
            <div class="col-md-5 text-center bg-white p-5 rounded shadow border-success border-top border-4">
                <img src="${userPicture}" class="rounded-circle mb-3 border border-3" width="80">
                <h4>Welcome back, ${userFullName}!</h4>
                <p class="text-success fw-bold">✓ Identity Verified via Google OAuth</p>
                <p class="text-muted small">Loading Secure Ledger...</p>
            </div>
        </div>
    `;
    setTimeout(() => {
        loginScreen.classList.add('d-none');
        document.getElementById('publicDashboard').classList.remove('d-none');
        loadPublicProjects();
    }, 2000);
}

// --- 2. Load the Projects List ---
async function loadPublicProjects() {
    const container = document.getElementById('publicProjectsContainer');
    try {
        const response = await fetch(`${API_URL}/api/projects/public`);
        const result = await response.json();
        
        if (result.status === "success") {
            container.innerHTML = ""; 
            result.data.forEach(project => {
                const html = `
                    <div class="border rounded p-3 mb-3 bg-light" style="cursor: pointer;" onclick="loadTimeline(${project.project_id}, '${project.project_name}')">
                        <h5>${project.project_name}</h5>
                        <p class="mb-1 text-muted"><strong>Contractor:</strong> ${project.contractor_name}</p>
                        <div class="progress mt-2" style="height: 10px;">
                            <div class="progress-bar bg-success" style="width: ${project.health_score}%;"></div>
                        </div>
                        <p class="text-end small mt-2 mb-0 text-primary fw-bold">View Ledger ➔</p>
                    </div>
                `;
                container.innerHTML += html;
            });
        }
    } catch (error) {
        container.innerHTML = `<p class="text-danger">Server Error.</p>`;
    }
}

async function loadTimeline(projectId, projectName) {
    const container = document.getElementById('timelineContainer');
    container.innerHTML = `<p class="text-center">Fetching highly secure data for ${projectName}...</p>`;
    
    try {
        const response = await fetch(`${API_URL}/api/public/updates/${projectId}`);
        const result = await response.json();
        
        if (result.status === "success" && result.data.length > 0) {
            const chartData = [...result.data].reverse(); 
            
            const labels = [];
            const progressData = [];
            const costData = [];
            let cumulativeCost = 0;

            chartData.forEach(update => {
                labels.push(`Update #${update.rowid}`);
                progressData.push(update.claimed_progress);
                
                cumulativeCost += update.cost_incurred_today;
                costData.push(cumulativeCost);
            });

            drawChart(labels, progressData, costData);
            container.innerHTML = `<h5 class="mb-4">${projectName} Activity Log</h5>`;
            
            result.data.forEach(update => {
                const billButton = update.bill_image_path 
                    ? `<a href="${update.bill_image_path}" target="_blank" class="btn btn-sm btn-outline-warning mt-2">📄 View Invoice</a>` 
                    : `<span class="badge bg-secondary mt-2">No Bill Attached</span>`;

                const html = `
                    <div class="timeline-card bg-white p-3 shadow-sm rounded">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="fw-bold text-success">✅ AI Verified</span>
                            <small class="text-muted">Record #${update.rowid}</small>
                        </div>
                        <div class="row">
                            <div class="col-md-5">
                                <img src="${update.image_file_path}" class="img-fluid rounded border">
                            </div>
                            <div class="col-md-7">
                                <p class="mb-1"><strong>Progress Claimed:</strong> ${update.claimed_progress}%</p>
                                <p class="mb-1"><strong>Cost Incurred:</strong> ₹${update.cost_incurred_today.toLocaleString()}</p>
                                ${billButton}
                            </div>
                        </div>
                    </div>
                `;
                container.innerHTML += html;
            });
        } else {
            container.innerHTML = `<p class="text-muted">No verified updates available for this project yet.</p>`;
            if(currentChart) currentChart.destroy(); // Clear the chart if empty
        }
    } catch (error) {
        container.innerHTML = `<p class="text-danger">Error loading timeline.</p>`;
    }
}

// --- 4. The Chart.js Engine ---
function drawChart(labels, progressData, costData) {
    const ctx = document.getElementById('projectChart').getContext('2d');
    
    // Destroy the old chart if you click a different project
    if (currentChart) {
        currentChart.destroy();
    }

    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Progress (%)',
                    data: progressData,
                    borderColor: 'rgba(25, 135, 84, 1)', // Green
                    backgroundColor: 'rgba(25, 135, 84, 0.2)',
                    yAxisID: 'y-progress',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Cumulative Cost (₹)',
                    data: costData,
                    borderColor: 'rgba(13, 110, 253, 1)', // Blue
                    backgroundColor: 'rgba(13, 110, 253, 0.2)',
                    yAxisID: 'y-cost',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                'y-progress': {
                    type: 'linear',
                    position: 'left',
                    title: { display: true, text: 'Completion %' },
                    max: 100,
                    min: 0
                },
                'y-cost': {
                    type: 'linear',
                    position: 'right',
                    title: { display: true, text: 'Rupees (₹)' },
                    grid: { drawOnChartArea: false } 
                }
            }
        }
    });
}
