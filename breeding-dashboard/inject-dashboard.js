// BMS Dashboard Injector
// Copy and paste this entire script into the browser console while on semillanueva.bmspro.io

(function() {
    console.log('🌱 Injecting BC Dashboard...');
    
    // Create dashboard container
    const dashboardDiv = document.createElement('div');
    dashboardDiv.id = 'bc-dashboard-overlay';
    dashboardDiv.innerHTML = `
        <style>
            #bc-dashboard-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                z-index: 99999;
                overflow-y: auto;
                padding: 20px;
            }
            .bc-close-btn {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                background: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                z-index: 100000;
            }
            .bc-card {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 16px;
                padding: 25px;
                margin-bottom: 25px;
                max-width: 1400px;
                margin-left: auto;
                margin-right: auto;
            }
            .bc-funnel-bar {
                height: 40px;
                background: #f8f9fa;
                border-radius: 8px;
                overflow: hidden;
                margin: 10px 0;
            }
            .bc-funnel-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                display: flex;
                align-items: center;
                padding: 0 15px;
                color: white;
                font-weight: 600;
            }
        </style>
        
        <button class="bc-close-btn" onclick="document.getElementById('bc-dashboard-overlay').remove()">
            ✕ Close Dashboard
        </button>
        
        <div class="bc-card">
            <h1 style="color: #667eea; font-size: 2em; margin-bottom: 20px;">
                🌱 BC Operational & Agronomic Metrics
            </h1>
            <p style="color: #666;">Connected to BMS - Program: ${window.location.href.match(/programUUID=([^&]+)/)?.[1] || 'Unknown'}</p>
        </div>
        
        <div class="bc-card">
            <h2 style="color: #764ba2; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px;">
                📊 Pipeline Funnel
            </h2>
            <div id="bc-funnel-data">Loading from BMS...</div>
        </div>
        
        <div class="bc-card">
            <h2 style="color: #764ba2; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                📈 Efficiency Rates
            </h2>
            <div id="bc-rates-data">Loading from BMS...</div>
        </div>
    `;
    
    document.body.appendChild(dashboardDiv);
    
    // Fetch BMS data using the existing session
    async function fetchBMSData() {
        try {
            const programUUID = 'febb4f0f-b4af-4399-bdec-73e88a5d2223';
            const response = await fetch(`/bmsapi/crops/maize/programs/${programUUID}/studies`);
            const studies = await response.json();
            
            console.log('✅ Fetched studies:', studies);
            
            // Display basic info
            document.getElementById('bc-funnel-data').innerHTML = `
                <p>Found ${studies.length} studies in BMS</p>
                <p>Total trials: ${studies.length}</p>
            `;
            
            document.getElementById('bc-rates-data').innerHTML = `
                <p>Successfully connected to BMS API!</p>
                <p>Studies loaded: ${studies.length}</p>
            `;
            
        } catch (error) {
            console.error('Error fetching BMS data:', error);
            document.getElementById('bc-funnel-data').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    }
    
    fetchBMSData();
    
    console.log('✅ Dashboard injected! Click X to close.');
})();
