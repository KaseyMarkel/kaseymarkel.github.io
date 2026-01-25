// BMS Dashboard with Auto-Auth
// This version automatically uses your current BMS session

(function() {
    console.log('🌱 Injecting BC Dashboard with Auto-Auth...');

    // Create dashboard overlay
    const overlay = document.createElement('div');
    overlay.id = 'bc-dashboard';
    overlay.innerHTML = `
        <style>
            #bc-dashboard {
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
            .bc-close {
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
                margin: 0 auto 25px;
                max-width: 1400px;
            }
            h1 { color: #667eea; font-size: 2em; margin-bottom: 10px; }
            h2 { color: #764ba2; border-bottom: 2px solid #667eea; padding-bottom: 10px; margin-bottom: 20px; }
        </style>

        <button class="bc-close" onclick="this.parentElement.remove()">✕ Close</button>

        <div class="bc-card">
            <h1>🌱 BC Operational & Agronomic Metrics</h1>
            <p id="bc-status" style="color: #666;">Connecting to BMS...</p>
        </div>

        <div class="bc-card">
            <h2>📊 Studies Data</h2>
            <div id="bc-data">Loading...</div>
        </div>

        <div class="bc-card">
            <h2>🐛 Debug Log</h2>
            <pre id="bc-log" style="background: #1f2937; color: #10b981; padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px;"></pre>
        </div>
    `;

    document.body.appendChild(overlay);

    const log = (msg) => {
        console.log(msg);
        const logEl = document.getElementById('bc-log');
        logEl.textContent += `${new Date().toLocaleTimeString()} - ${msg}\n`;
    };

    // Fetch data with credentials: 'same-origin' to use existing cookies
    async function fetchData() {
        try {
            const programUUID = 'febb4f0f-b4af-4399-bdec-73e88a5d2223';
            const url = `/bmsapi/crops/maize/programs/${programUUID}/studies`;

            log(`Fetching: ${url}`);
            document.getElementById('bc-status').textContent = 'Fetching studies...';

            const response = await fetch(url, {
                credentials: 'same-origin',  // Use cookies from current session
                headers: {
                    'Accept': 'application/json'
                }
            });

            log(`Response: ${response.status} ${response.statusText}`);

            if (!response.ok) {
                const text = await response.text();
                log(`Error response: ${text}`);
                throw new Error(`${response.status}: ${text}`);
            }

            const data = await response.json();
            log(`Success! Received ${data.length} studies`);

            document.getElementById('bc-status').innerHTML = `
                ✅ Connected to BMS<br>
                <small>Program: ${programUUID}</small>
            `;

            document.getElementById('bc-data').innerHTML = `
                <p><strong>Total Studies:</strong> ${data.length}</p>
                <p><strong>API Endpoint:</strong> ${url}</p>
                <details>
                    <summary>Show raw data</summary>
                    <pre style="background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>
                </details>
            `;

            return data;

        } catch (error) {
            log(`❌ Error: ${error.message}`);
            document.getElementById('bc-status').innerHTML = `
                ❌ Connection failed<br>
                <small>${error.message}</small>
            `;
            document.getElementById('bc-data').innerHTML = `
                <p style="color: #ef4444;"><strong>Error:</strong> ${error.message}</p>
                <p>Check the debug log below for details.</p>
            `;
        }
    }

    log('Dashboard initialized');
    fetchData();
})();
