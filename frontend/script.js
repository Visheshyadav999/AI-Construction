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
            // THE FIX: parseInt() forces the text "2" into the math number 2
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
            
            // If you have a function to load projects, you would call it here!
            // loadContractorProjects(loginIdRaw); 
            
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

// --- 2. Fetch and Display Projects ---
async function loadProjects() {
    const container = document.getElementById('projectsContainer');
    try {
        const response = await fetch(`${API_URL}/api/projects`);
        const result = await response.json();
        
        if (result.status === "success") {
            container.innerHTML = ""; 
            result.data.forEach(project => {
                const html = `
                    <div class="border rounded p-3 mb-3 bg-white">
                        <h5>${project.project_name} (ID: ${project.project_id})</h5>
                        <p class="mb-1"><strong>Client:</strong> ${project.client_name} | <strong>Contractor:</strong> ${project.contractor_name}</p>
                        <p class="mb-1"><strong>Budget:</strong> ₹${project.estimated_budget} | <strong>Spent:</strong> ₹${project.actual_spent}</p>
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
    } catch (error) {
        container.innerHTML = `<p class="text-danger">Error connecting to server.</p>`;
    }
}

// --- 3. Handle the Image Upload Form ---
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault(); 
    
    const submitBtn = document.getElementById('submitBtn');
    const resultAlert = document.getElementById('resultAlert');
    
    submitBtn.innerText = "Processing Image via AI...";
    submitBtn.disabled = true;
    
    const formData = new FormData();
    formData.append('project_id', document.getElementById('projectId').value);
    formData.append('stage_id', document.getElementById('stageId').value);
    formData.append('uploaded_by', document.getElementById('uploadedBy').value);
    formData.append('claimed_progress', document.getElementById('claimedProgress').value);
    formData.append('cost_incurred_today', document.getElementById('costIncurred').value);
    formData.append('image', document.getElementById('siteImage').files[0]);
    
    const billFile = document.getElementById('billImage').files[0];
    if (billFile) formData.append('bill_image', billFile);

    try {
        const response = await fetch(`${API_URL}/api/updates`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        resultAlert.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-warning');
        
        if (result.status === "security_rejected") {
            resultAlert.classList.add('alert-danger');
            resultAlert.innerHTML = `<strong>🚨 SECURITY BREACH PREVENTED:</strong> ${result.message}`;
        } else if (result.ai_conclusion === "Verified") {
            resultAlert.classList.add('alert-success');
            resultAlert.innerHTML = `<strong>✅ Success!</strong> Image verified by AI and Data saved.`;
        } else if (result.ai_conclusion === "Flagged") {
            resultAlert.classList.add('alert-warning');
            resultAlert.innerHTML = `<strong>⚠️ Warning:</strong> AI flagged this image for low structural density!`;
        }
        
        loadProjects();
        document.getElementById('uploadForm').reset();
        
        setTimeout(() => { resultAlert.classList.add('d-none'); }, 6000);

    } catch (error) {
        resultAlert.classList.remove('d-none');
        resultAlert.classList.add('alert-danger');
        resultAlert.innerHTML = `Error uploading data. Check terminal.`;
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
        const response = await fetch(`${API_URL}/api/predict/${projectId}`);
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
// --- SECURE PROJECT LOADER ---
// This fetches ONLY the projects assigned to the logged-in contractor
async function loadContractorProjects(contractorId) {
    try {
        // We hit Endpoint #2 on your Python server!
        const response = await fetch(`/api/projects/contractor/${contractorId}`);
        const result = await response.json();
        
        const projectDropdown = document.getElementById('projectId');
        
        if (result.status === "success") {
            // Clear the "Loading..." text
            projectDropdown.innerHTML = '<option value="" disabled selected>Select an assigned project...</option>';
            
            // Loop through their specific projects and add them to the dropdown
            result.data.forEach(project => {
                projectDropdown.innerHTML += `
                    <option value="${project.project_id}">
                        ${project.project_name} (Budget: ₹${project.estimated_budget.toLocaleString()})
                    </option>
                `;
            });
        } else {
            projectDropdown.innerHTML = '<option value="" disabled>Error loading projects</option>';
        }
    } catch (error) {
        console.error("Failed to load secure projects:", error);
    }
}
