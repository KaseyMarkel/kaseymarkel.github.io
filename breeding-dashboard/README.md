# BC Operational & Agronomic Metrics Dashboard

A beautiful, real-time dashboard for tracking breeding program performance metrics with BMS API integration.

## 🌟 Features

- **Real-time BMS Integration**: Auto-updates from BMS Pro API every 5 minutes
- **Beautiful Visualizations**: Modern glassmorphism design with interactive charts
- **Comprehensive Metrics**:
  - Block A: Pipeline funnel tracking
  - Block B: Efficiency rates
  - Block C: Coverage analysis
  - Block D: Cycle speed metrics
  - Block F: Trait pyramiding progress
  - Top operational issues tracking
- **Access Control**: View-only by default, GitHub-based authentication for editors
- **Audit Logging**: Track all changes and data refreshes
- **Mobile Responsive**: Works on all devices
- **Zero Cost**: Completely free hosting on GitHub Pages

## 🚀 Quick Start

### Option 1: GitHub Pages (Recommended)

1. **Fork or clone this repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/breeding-dashboard.git
   cd breeding-dashboard
   ```

2. **Configure BMS API credentials**

   Edit `index.html` and update the BMS API configuration:
   ```javascript
   const BMS_API_CONFIG = {
       baseUrl: 'https://bmspro.io/api',
       apiKey: 'YOUR_BMS_API_KEY',
       programId: 'YOUR_PROGRAM_ID'
   };
   ```

3. **Enable GitHub Pages**
   - Go to your repository settings
   - Navigate to "Pages" section
   - Select "main" branch as source
   - Save

4. **Access your dashboard**
   - Your dashboard will be available at: `https://YOUR_USERNAME.github.io/breeding-dashboard/`

### Option 2: Local Development

1. **Simply open the HTML file**
   ```bash
   open index.html
   # or
   python -m http.server 8000
   # then navigate to http://localhost:8000
   ```

## 🔐 Authentication & Access Control

### View Access
- **No login required** - Anyone with the URL can view the dashboard
- All metrics are read-only by default
- Data auto-refreshes when enabled

### Editor Access
To enable editing permissions:

1. **Create a GitHub Personal Access Token**
   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scopes: `read:user`
   - Generate and copy the token

2. **Configure allowed editors**
   Edit `index.html` and add GitHub usernames:
   ```javascript
   const auth = new DashboardAuth({
       allowedEditors: ['kaseymarkel', 'teammate1', 'teammate2']
   });
   ```

3. **Login**
   - Click "Editor Login" button
   - Paste your GitHub token
   - You'll have edit permissions if your username is in the allowed list

### Audit Trail
All actions are logged with:
- Timestamp
- User (authenticated or anonymous)
- Action performed
- View logs in the dashboard footer

## 📊 Dashboard Blocks

### Block A: Pipeline Funnel
Tracks progression through breeding pipeline stages:
- Seeds planted → Plants at V4-V6 → Sampled → Valid genotypes → Selected → Pollinated → Successful ears → Harvested

### Block B: Efficiency Rates
Key performance indicators:
- Emergence rate (target: ≥80%)
- V4-V6 survival rate (target: ≥85%)
- Sampling rate (target: ≥95%)
- Valid genotype rate (target: ≥90%)
- Pollination success rate (target: ≥85%)
- Rot loss rate (target: ≤5%)
- Lab evaluation rate (target: ≥95%)
- Lab pass rate (target: ≥90%)

### Block C: Coverage Analysis
Tracks availability vs. requirements by scheme/stage:
- 🟢 Green: Coverage ratio ≥1.2x
- 🟡 Yellow: Coverage ratio 1.0-1.2x
- 🔴 Red: Coverage ratio <1.0x

### Block D: Cycle Speed
Monitors turnaround times:
- Planting → Sampling (target: ≤40 days)
- Sampling → Genotyping (target: ≤14 days)
- Genotyping → Next planting (target: ≤21 days)
- Total cycle time (target: ≤75 days)

### Block F: Trait Pyramiding Progress
Zn + QPM stacking achievements:
- ≥60% threshold
- ≥70% threshold
- ≥80% threshold + o2 homozygous

### Top Operational Issues
Ranked by impact with trend indicators:
- Spiroplasma/virus infections
- Climate/temperature stress
- Pollination effectiveness
- Ear mold diseases
- And more...

## 🔧 Configuration

### BMS API Integration

The dashboard uses the BMS Pro API to fetch real-time data. You'll need:

1. **BMS API credentials**
   - API key from your BMS account
   - Program ID for your breeding program

2. **Update configuration**
   ```javascript
   // In index.html
   const BMS_API_CONFIG = {
       baseUrl: 'https://bmspro.io/api',
       apiKey: 'YOUR_API_KEY_HERE',
       programId: 'YOUR_PROGRAM_ID'
   };
   ```

3. **Configure auto-refresh**
   - Toggle "Auto-refresh" button in dashboard
   - Default: Updates every 5 minutes
   - Customize interval in code if needed

### Filters

Available filters:
- **Location**: All, Station BC, Oriente, Estación
- **Scheme**: All, QPM, Zn, Zn+QPM
- **Stage**: All, BC1F1, BC2F1, BC3F1
- **Date Range**: Configurable

### Thresholds

All metric thresholds are configurable in the code:
```javascript
const THRESHOLDS = {
    emergenceRate: 80,
    samplingRate: 95,
    pollinationSuccess: 85,
    // etc.
};
```

## 📱 Mobile & Responsive

The dashboard is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🎨 Customization

### Colors & Branding
Edit the CSS variables in `index.html`:
```css
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --status-green: #10b981;
    --status-yellow: #f59e0b;
    --status-red: #ef4444;
}
```

### Metrics
Add or modify metrics by editing the data structure and visualization components.

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to public repositories
   - Use environment variables
   - Or use GitHub Actions secrets for automated deployments

2. **Access Control**:
   - View access is public by default
   - Editor access requires GitHub authentication
   - Consider IP whitelisting for sensitive data

3. **Data Privacy**:
   - All data is transmitted over HTTPS
   - No sensitive data stored in browser beyond session
   - Audit logs stored locally (move to backend for production)

## 📈 Performance

- Lightweight: ~200KB total (including libraries)
- Fast load times: <2 seconds
- Efficient caching: 5-minute cache for API responses
- Minimal server load: Static hosting on GitHub Pages

## 🐛 Troubleshooting

### Dashboard not loading?
- Check browser console for errors
- Verify BMS API credentials are correct
- Ensure GitHub Pages is enabled

### Data not updating?
- Check BMS API connection
- Verify API key has correct permissions
- Check browser network tab for failed requests

### Authentication issues?
- Verify GitHub token is valid
- Check username is in allowedEditors list
- Clear browser cache and try again

## 🤝 Contributing

This is an internal tool, but improvements are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

Internal use only - Add your organization's license here

## 🆘 Support

For issues or questions:
- Contact: kaseymarkel@gmail.com
- BMS Documentation: https://bmspro.io/1596/breeding-management-system/tutorials/

## 🎯 Roadmap

Future enhancements:
- [ ] Export to PDF/Excel
- [ ] Historical trend analysis
- [ ] Alert notifications
- [ ] Multi-program comparison
- [ ] Advanced filtering
- [ ] Custom report builder
- [ ] Integration with other systems

---

Built with ❤️ using React, Recharts, and the BMS API
