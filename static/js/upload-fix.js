// Simple, working upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const loadingState = document.getElementById('loadingState');
    const results = document.getElementById('results');
    
    // Initial upload area click handler
    const uploadArea = document.querySelector('.travelers-upload-area');
    if (uploadArea) {
        uploadArea.onclick = function() { fileInput.click(); };
    }
    
    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const file = fileInput.files[0];
            if (!file) {
                alert('Please select a file to upload.');
                return;
            }
            
            // Show loading
            loadingState.classList.remove('travelers-hidden');
            results.classList.add('travelers-hidden');
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                loadingState.classList.add('travelers-hidden');
                
                if (data.success) {
                    displayResults(data);
                } else {
                    displayError(data.error || 'Upload failed');
                }
            } catch (error) {
                loadingState.classList.add('travelers-hidden');
                displayError('Upload failed: ' + error.message);
            }
        });
    }
    
    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                uploadArea.innerHTML = `
                    <div class="travelers-upload-icon">✅</div>
                    <h3 style="margin-bottom: 0.5rem; color: var(--travelers-heading-color);">File Selected: ${file.name}</h3>
                    <p style="color: var(--travelers-medium-gray); margin-bottom: 0;">Size: ${(file.size / 1024 / 1024).toFixed(2)}MB | Click "Analyze Document" to continue</p>
                `;
            }
        });
    }
});

function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const analysis = data.analysis || {};
    const quote = data.quote;
    
    let html = `
        <div class="results-grid">
            <div class="travelers-card" style="background: linear-gradient(135deg, #002d4b 0%, #131517 100%); color: white;">
                <h3 style="color: white; margin-bottom: 1rem;">📋 Current Policy Analysis</h3>
                <div>
                    <div style="margin-bottom: 1rem;">
                        <strong style="color: #007395;">Policy Type:</strong><br>
                        <span style="font-size: 1.1rem;">${analysis.policy_type || 'Unknown'}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong style="color: #007395;">Current Premium:</strong><br>
                        <span style="font-size: 1.3rem; font-weight: 600;">$${analysis.current_premium || '0'}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong style="color: #007395;">Insurance Carrier:</strong><br>
                        <span style="font-size: 1.1rem;">${analysis.carrier || 'Not detected'}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong style="color: #007395;">Analysis Confidence:</strong><br>
                        <span style="font-size: 1.1rem;">${Math.round((analysis.confidence || 0) * 100)}%</span>
                    </div>
                </div>
            </div>
            
            <div class="travelers-card" style="background: linear-gradient(135deg, #e01719 0%, #c01315 100%); color: white;">
                <h3 style="color: white; margin-bottom: 1rem;">💰 Our Competitive Quote</h3>
                ${quote ? `
                <div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Our Quote:</strong><br>
                        <span style="font-size: 2rem; font-weight: 700;">$${quote.new_quote}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Your Savings:</strong><br>
                        <span style="font-size: 1.8rem; font-weight: 600; color: #90EE90;">$${quote.savings}</span>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Savings Percentage:</strong><br>
                        <span style="font-size: 1.5rem; font-weight: 600; color: #90EE90;">${quote.savings_percent}%</span>
                    </div>
                </div>
                ` : `
                <div style="text-align: center; padding: 2rem 0;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
                    <p>Analyzing your policy...</p>
                </div>
                `}
            </div>
        </div>
    `;
    
    // Coverage comparison table
    if (quote && quote.current_coverage && quote.our_coverage) {
        html += `
            <div class="travelers-card" style="margin-bottom: 2rem;">
                <h3 style="color: #002d4b; margin-bottom: 1.5rem;">🔍 Detailed Coverage Comparison</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
                        <thead>
                            <tr style="background: linear-gradient(135deg, #f2f5f7 0%, #e8eef2 100%);">
                                <th style="padding: 12px; text-align: left; color: #002d4b; font-weight: 600;">Coverage Type</th>
                                <th style="padding: 12px; text-align: center; color: #002d4b; font-weight: 600;">Current Policy</th>
                                <th style="padding: 12px; text-align: center; color: #002d4b; font-weight: 600;">Our Quote</th>
                                <th style="padding: 12px; text-align: center; color: #002d4b; font-weight: 600;">Improvement</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        Object.keys(quote.current_coverage).forEach(coverageType => {
            const current = quote.current_coverage[coverageType];
            const our = quote.our_coverage[coverageType];
            const currentLimit = parseInt(current.limit.replace(/[$,]/g, ''));
            const ourLimit = parseInt(our.limit.replace(/[$,]/g, ''));
            const isImprovement = ourLimit > currentLimit;
            
            html += `
                <tr style="border-bottom: 1px solid #e0e0e0;">
                    <td style="padding: 12px; font-weight: 600; color: #002d4b;">
                        ${coverageType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </td>
                    <td style="padding: 12px; text-align: center;">
                        <div style="font-weight: 600; color: #66869a;">${current.limit}</div>
                        <div style="font-size: 0.8rem; color: #66869a;">$${current.premium}/year</div>
                    </td>
                    <td style="padding: 12px; text-align: center;">
                        <div style="font-weight: 600; color: #e01719;">${our.limit}</div>
                        <div style="font-size: 0.8rem; color: #e01719;">$${our.premium}/year</div>
                    </td>
                    <td style="padding: 12px; text-align: center;">
                        ${isImprovement ? 
                            `<span style="color: #27ae60; font-weight: 600;">↗️ +$${(ourLimit - currentLimit).toLocaleString()}</span>` :
                            `<span style="color: #66869a;">Same Coverage</span>`
                        }
                    </td>
                </tr>
            `;
        });
        
        html += `</tbody></table></div></div>`;
    }
    
    // Upload another button
    html += `
        <div class="travelers-card" style="text-align: center; background: linear-gradient(135deg, #f2f5f7 0%, #ffffff 100%); border: 2px solid #007395;">
            <h4 style="color: #002d4b; margin-bottom: 1rem;">Need to analyze another policy?</h4>
            <button onclick="resetForNewUpload()" class="travelers-btn travelers-btn-primary" style="font-size: 1.1rem; padding: 1rem 2rem;">
                <i class="fas fa-upload" style="margin-right: 0.5rem;"></i>
                Upload Another Document
            </button>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    resultsDiv.classList.remove('travelers-hidden');
}

function displayError(error) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `
        <div class="travelers-card" style="border-left: 4px solid #e01719;">
            <h3 style="color: #e01719;">❌ Upload Error</h3>
            <p><strong>Error:</strong> ${error}</p>
            <div style="margin-top: 1rem; text-align: center;">
                <button onclick="resetForNewUpload()" class="travelers-btn travelers-btn-secondary">Try Another File</button>
            </div>
        </div>
    `;
    resultsDiv.classList.remove('travelers-hidden');
}

// SIMPLE reset function that WILL work
function resetForNewUpload() {
    // Clear file input
    document.getElementById('fileInput').value = '';
    
    // Reset upload area with DIRECT onclick
    const uploadArea = document.querySelector('.travelers-upload-area');
    uploadArea.innerHTML = `
        <div class="travelers-upload-icon">📄</div>
        <h3 style="margin-bottom: 0.5rem; color: var(--travelers-heading-color);">Drop your file here or click to browse</h3>
        <p style="color: var(--travelers-medium-gray); margin-bottom: 0;">Supports PDF, JPG, PNG, HEIC files up to 16MB</p>
    `;
    
    // DIRECT assignment - this WILL work
    uploadArea.onclick = function() { 
        document.getElementById('fileInput').click(); 
    };
    
    // Hide results
    document.getElementById('results').classList.add('travelers-hidden');
    document.getElementById('loadingState').classList.add('travelers-hidden');
    
    // Scroll to upload
    document.getElementById('upload-section').scrollIntoView({ behavior: 'smooth' });
}
