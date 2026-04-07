const API_URL = ""; 

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Grab the values from the input boxes
    const loginIdRaw = document.getElementById('loginId').value;
    const loginPassword = document.getElementById('loginPassword').value;
    const alertBox = document.getElementById('loginAlert');
    const loginBtn = document.getElementById('loginBtn');
    
    // Change button text to show it's loading
    loginBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Authenticating...';
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                user_id: parseInt(loginIdRaw), 
                password: loginPassword 
            })
        });

        const result = await response.json();

        if (response.ok) {
            // Success! Hide login screen and show the dashboard
            document.getElementById('loginScreen').classList.add('d-none');
            document.getElementById('secureDashboard').classList.remove('d-none');
            
            // Put their real name in the sidebar
            document.getElementById('contractorNameDisplay').innerText = result.user.name;
            
            // Secretly save their ID into the hidden input for the Upload Form
            document.getElementById('uploadedBy').value = loginIdRaw;
            
            // 🔥 THE FIX: Trigger the unified loader to build the entire dashboard
            loadContractorDashboard(loginIdRaw); 
            
        } else {
            // Show the red error box
            alertBox.innerText = "❌ " + (result.detail || "Invalid Credentials");
            alertBox.classList.remove('d-none');
            loginBtn.innerText = 'Authenticate to Server';
        }
    } catch (error) {
        alertBox.innerText = "🚨 Server connection failed. Is Uvicorn running?";
        alertBox.classList.remove('d-none');
        loginBtn.innerText = 'Authenticate to Server';
    }
});

// 🔥 THE FIX: Unified function to securely load BOTH the Dropdown AND the Right Panel
async function loadContractorDashboard(contractorId) {
    const container = document.getElementById('projectsContainer');
    const projectDropdown = document.getElementById('projectId');

    try {
        // Fetch ONLY the projects assigned to this specific contractor
        const response = await fetch(`/api/projects/contractor/${contractorId}`);
        const result = await response.json();
        
        if (result.status === "success") {
            
            // 1. Populate the Upload Dropdown
            if (projectDropdown) {
                projectDropdown.innerHTML = '<option value="" disabled selected>Select an assigned project...</option>';
                result.data.forEach(project => {
                    projectDropdown.innerHTML += `
                        <option value="${project.project_id}">
                            ${project.project_name} (Budget: ₹${project.estimated_budget.toLocaleString()})
                        </option>
                    `;
                });
            }

            // 2. Populate the "Active Portfolios" Right Panel
            if (container) {
                container.innerHTML = ""; 
                result.data.forEach(project => {
                    const html = `
                        <div class="border rounded p-3 mb-3 bg-white shadow-sm">
                            <h5>${project.project_name}</h5>
                            <p class="mb-1 text-muted">Project ID: ${project.project_id}</p>
                            <p class="mb-1"><strong>Budget:</strong> ₹${project.estimated_budget.toLocaleString()} | <strong>Spent:</strong> ₹${project.actual_spent.toLocaleString()}</p>
                            <div class="progress mt-2 mb-3" style="height: 20px;">
                                <div class="progress-bar ${project.health_score < 50 ? 'bg-danger' : 'bg-success'}" 
                                     role="progressbar" style="width: ${project.health_score}%;" 
                                     aria-valuenow="${project.health_score}" aria-valuemin="0" aria-valuemax="100">
                                    Health Score: ${project.health_score}%
                                </div>
                            </div>
                            <button class="btn btn-sm btn-outline-primary w-100" onclick="runMLPrediction(${project.project_id})">
                                🔮 Run ML Cost Prediction
                            </button>
                            <div id="mlResult-${project.project_id}" class="mt-2 text-center text-primary fw-bold"></div>
                        </div>
                    `;
                    container.innerHTML += html;
                });
            }
        }
    } catch (error) {
        if(container) container.innerHTML = `<p class="text-danger">Error loading secure dashboard.</p>`;
    }
}

// --- 3. Handle the Image Upload Form ---
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault(); 
    
    const submitBtn = document.getElementById('submitBtn');
    const resultAlert = document.getElementById('resultAlert');
    const contractorId = document.getElementById('uploadedBy').value;
    
    submitBtn.innerText = "Processing Image via AI...";
    submitBtn.disabled = true;
    
    const formData = new FormData();
    formData.append('project_id', document.getElementById('projectId').value);
    formData.append('stage_id', document.getElementById('stageId').value);
    formData.append('uploaded_by', contractorId);
    formData.append('claimed_progress', document.getElementById('claimedProgress').value);
    formData.append('cost_incurred_today', document.getElementById('costIncurred').value);
    
    // 🔥 THE FIX: Changed 'image' to 'site_image' to match your FastAPI server!
    formData.append('site_image', document.getElementById('siteImage').files[0]);
    
    const billFile = document.getElementById('billImage').files[0];
    if (billFile) formData.append('bill_image', billFile);

    try {
        const response = await fetch(`/api/updates`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        resultAlert.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-warning');
        
        if (response.ok) {
            resultAlert.classList.add('alert-success');
            resultAlert.innerHTML = `<strong>✅ Success!</strong> ${result.message || "Data saved."}`;
        } else {
            resultAlert.classList.add('alert-danger');
            resultAlert.innerHTML = `<strong>🚨 Error:</strong> ${result.detail || "Upload failed."}`;
        }
        
        // Refresh the dashboard with the new data
        loadContractorDashboard(contractorId);
        document.getElementById('uploadForm').reset();
        
        setTimeout(() => { resultAlert.classList.add('d-none'); }, 6000);

    } catch (error) {
        resultAlert.classList.remove('d-none', 'alert-success');
        resultAlert.classList.add('alert-danger');
        resultAlert.innerHTML = `Error uploading data. Check console.`;
    } finally {
        submitBtn.innerText = "Upload & Verify via AI";
        submitBtn.disabled = false;
    }
});

// --- 4. Run Machine Learning Prediction ---
async function runMLPrediction(projectId) {
    const resultDiv = document.getElementById(`mlResult-${projectId}`);
    resultDiv.innerHTML = "<em>Running Scikit-Learn Model...</em>";
    try {
        const response = await fetch(`/api/predict/${projectId}`);
        const result = await response.json();
        if (result.status === "success") {
            resultDiv.innerHTML = `🔮 AI Prediction: Final Cost will be ₹${result.predicted_final_cost.toLocaleString()}`;
        } else if (result.status === "insufficient_data") {
            resultDiv.innerHTML = `⚠️ ${result.message}`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<span class="text-danger">ML Engine Error</span>`;
    }
}
