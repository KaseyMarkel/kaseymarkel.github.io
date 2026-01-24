# ⚡ Quick Start Guide

Get your dashboard running in 5 minutes!

## 🎯 For Non-Technical Users

### View the Dashboard (No Setup Required)

Once deployed by your team, simply:
1. **Get the link** from your admin (looks like: `https://username.github.io/breeding-dashboard/`)
2. **Open in browser** - Chrome, Firefox, Safari, or Edge
3. **View all metrics** - No login needed!

That's it! The dashboard updates automatically.

### Enable Auto-Refresh

1. Click the **"Auto-refresh OFF"** button in the top-right
2. It will turn green: **"Auto-refresh ON"**
3. Dashboard now updates every 5 minutes automatically

### Use Filters

Click the filter chips at the top to focus on specific data:
- **Location**: Station BC, Oriente, Estación
- **Scheme**: QPM, Zn, Zn+QPM
- **Stage**: BC1F1, BC2F1, BC3F1

### Export Data (Requires Editor Login)

1. Click **"Editor Login"**
2. Ask your admin for a GitHub token
3. Paste the token and login
4. You'll see export options appear

## 👨‍💻 For Technical Users

### 1-Minute Local Preview

```bash
# Download the dashboard
git clone https://github.com/YOUR_USERNAME/breeding-dashboard.git
cd breeding-dashboard

# Open in browser
open index.html
# or
python -m http.server 8000  # then visit http://localhost:8000
```

### 5-Minute GitHub Pages Deployment

```bash
# 1. Create new repo on GitHub (skip if already exists)
# Go to https://github.com/new and create 'breeding-dashboard'

# 2. Push the code
git init
git add .
git commit -m "Initial dashboard"
git remote add origin https://github.com/YOUR_USERNAME/breeding-dashboard.git
git push -u origin main

# 3. Enable GitHub Pages
# Go to Settings → Pages → Source: main branch → Save

# 4. Done! Visit https://YOUR_USERNAME.github.io/breeding-dashboard/
```

### Configure BMS API

Edit `index.html` around line 60:

```javascript
const BMS_API_CONFIG = {
    baseUrl: 'https://bmspro.io/api',
    apiKey: 'YOUR_API_KEY_HERE',      // Get from BMS account settings
    programId: 'YOUR_PROGRAM_ID_HERE'  // Your breeding program ID
};
```

**Security Note**: Don't commit real API keys! See [DEPLOYMENT.md](DEPLOYMENT.md) for secure methods.

## 🔐 Setting Up Access Control

### Configure Allowed Editors

Edit `index.html` around line 150:

```javascript
const ALLOWED_EDITORS = [
    'kaseymarkel',     // GitHub username
    'teammate1',       // Add more usernames
    'teammate2'
];
```

### Generate GitHub Token (For Editors)

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name it: "Dashboard Editor"
4. Select scope: **read:user**
5. Click **"Generate token"**
6. Copy the token (starts with `ghp_`)
7. Share securely with team members who need edit access

### Login as Editor

1. Open the dashboard
2. Click **"Editor Login"**
3. Paste your GitHub token
4. Click **"Login"**
5. You now have edit permissions!

## 📊 Understanding the Dashboard

### Key Metrics at a Glance

**🟢 Green** = Exceeding target
**🟡 Yellow** = Close to target
**🔴 Red** = Below target

### Dashboard Blocks

| Block | What It Shows | Why It Matters |
|-------|--------------|----------------|
| **A: Pipeline Funnel** | Plant progression through breeding stages | Identifies bottlenecks |
| **B: Efficiency Rates** | Success rates at each stage | Spots quality issues |
| **C: Coverage Analysis** | Available vs required plants | Prevents shortfalls |
| **D: Cycle Speed** | Days between key milestones | Tracks pipeline velocity |
| **F: Stack Progress** | Trait pyramiding achievements | Measures breeding goals |
| **Top Issues** | Most impactful problems | Prioritizes interventions |

### Reading the Charts

**Funnel Bars** (Block A):
- Longer bar = More plants/ears at that stage
- Percentage shows efficiency vs target

**Rate Cards** (Block B):
- Big number = Current rate
- Threshold = Minimum acceptable
- Icon shows status

**Coverage Table** (Block C):
- Ratio >1.0 = More plants than needed (good!)
- Ratio <1.0 = Plant shortage (address ASAP)

**Speed Cards** (Block D):
- Days shown vs target
- ✓ = On track
- ⚠ = Delayed

## 🔄 Daily Workflow

### Morning Check
1. Open dashboard
2. Enable auto-refresh
3. Check for red/yellow status indicators
4. Review top operational issues
5. Filter by your location/scheme

### Data Review
1. Compare current vs target in funnel
2. Check efficiency rates
3. Verify coverage ratios
4. Monitor cycle times
5. Track trait pyramiding progress

### Issue Response
1. Sort issues by impact
2. Review affected plant counts
3. Check trend indicators (📈📉➡️)
4. Plan interventions
5. Log actions in comments

## 🚨 Troubleshooting

### "Dashboard not loading"
- **Check internet connection**
- Clear browser cache (Ctrl/Cmd + Shift + R)
- Try different browser

### "No data showing"
- Check if BMS API credentials are configured
- Verify you have data in BMS for selected filters
- Click "Refresh" button manually

### "Login not working"
- Verify GitHub token is valid (they expire!)
- Check your username is in ALLOWED_EDITORS list
- Clear browser data and try again

### "Charts look weird"
- Try zooming out (Ctrl/Cmd + -)
- Refresh the page
- Check on desktop if using mobile

## 💡 Pro Tips

1. **Bookmark your filtered view**: Use browser bookmarks after setting filters
2. **Schedule reviews**: Open dashboard in team meetings
3. **Share screenshots**: Use browser screenshot tools to capture specific blocks
4. **Track trends**: Check dashboard at same time daily to spot patterns
5. **Mobile access**: Dashboard works great on tablets for field reviews

## 📱 Mobile Usage

The dashboard is fully responsive! On mobile:
- Swipe to scroll through blocks
- Tap cards for details
- Use landscape mode for better chart viewing
- Filters stack vertically for easy access

## 🎓 Training Resources

### For Team Members
- [Complete README](README.md) - Full documentation
- [BMS Tutorial](https://bmspro.io/1596/breeding-management-system/tutorials/) - Understanding the data source

### For Administrators
- [Deployment Guide](DEPLOYMENT.md) - How to deploy and maintain
- [BMS API Docs](https://bmspro.io/api/docs) - API integration details

## 📞 Get Help

**View-only access issues**: Ask your team admin for the dashboard URL

**Technical issues**:
- Check the [troubleshooting section](#-troubleshooting)
- Contact: kaseymarkel@gmail.com

**BMS data issues**: Contact your BMS administrator

**Feature requests**: Submit via GitHub Issues (if enabled)

## ✅ Quick Reference

### Dashboard URL
```
https://YOUR_USERNAME.github.io/breeding-dashboard/
```

### Key Thresholds
- Emergence Rate: ≥80%
- Sampling Rate: ≥95%
- Pollination Success: ≥85%
- Rot Loss: ≤5%
- Coverage Ratio: ≥1.0x (ideally ≥1.2x)
- Cycle Time: ≤75 days

### Auto-Refresh
- Default: OFF (manual refresh only)
- When ON: Updates every 5 minutes
- Uses cached data to minimize API calls

---

**Ready to start?** Just open the dashboard URL and explore! 🚀

Questions? We're here to help! 💬
