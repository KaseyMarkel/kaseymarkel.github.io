# 📋 Deployment Checklist

Use this checklist to deploy your dashboard step-by-step.

## ✅ Pre-Deployment

### Get Your Credentials
- [ ] BMS API key
  - Login to BMS Pro
  - Go to Settings → API Access
  - Generate new API key
  - Copy and save securely

- [ ] BMS Program ID
  - Find your breeding program ID in BMS
  - Usually visible in program settings
  - Note it down

- [ ] GitHub account
  - Create account at https://github.com if needed
  - Free account works fine

### Prepare Team List
- [ ] List all team members who need **editor** access
  - Get their GitHub usernames
  - Most people only need **viewer** access (no login required)

## 🚀 Deployment Steps

### Step 1: Configure the Dashboard (5 minutes)

- [ ] Open `index.html` in text editor
- [ ] Find line ~60, update BMS API config:
  ```javascript
  const BMS_API_CONFIG = {
      baseUrl: 'https://bmspro.io/api',
      apiKey: 'YOUR_BMS_API_KEY',      // ← Paste your key here
      programId: 'YOUR_PROGRAM_ID'      // ← Paste your program ID here
  };
  ```

- [ ] Find line ~150, update allowed editors:
  ```javascript
  const ALLOWED_EDITORS = [
      'kaseymarkel',           // ← Replace with actual GitHub usernames
      'teammate1',
      'teammate2'
  ];
  ```

- [ ] Save the file

### Step 2: Test Locally (2 minutes)

- [ ] Open Terminal/Command Prompt
- [ ] Navigate to dashboard folder:
  ```bash
  cd breeding-dashboard
  ```

- [ ] Start local server:
  ```bash
  python3 -m http.server 8000
  ```
  Or just double-click `index.html`

- [ ] Open browser to `http://localhost:8000`

- [ ] Verify:
  - [ ] Dashboard loads without errors
  - [ ] Metrics are showing (or placeholders if no data yet)
  - [ ] Filters work
  - [ ] No console errors (press F12, check Console tab)

### Step 3: Create GitHub Repository (3 minutes)

- [ ] Go to https://github.com/new
- [ ] Repository name: `breeding-dashboard`
- [ ] Description: "BC Operational & Agronomic Metrics Dashboard"
- [ ] **Important**: Choose **Private** if data is sensitive
- [ ] **Do NOT** check "Add a README file"
- [ ] Click "Create repository"

### Step 4: Push Code to GitHub (2 minutes)

- [ ] Open Terminal in dashboard folder
- [ ] Run these commands:
  ```bash
  git init
  git add .
  git commit -m "Initial dashboard deployment"
  git remote add origin https://github.com/YOUR_USERNAME/breeding-dashboard.git
  git push -u origin main
  ```

- [ ] Refresh GitHub repo page - you should see all files

### Step 5: Enable GitHub Pages (1 minute)

- [ ] In your GitHub repository, click **Settings** (top right)
- [ ] Scroll to **Pages** section (left sidebar)
- [ ] Under **Source**:
  - Branch: `main`
  - Folder: `/ (root)`
- [ ] Click **Save**
- [ ] Wait 1-2 minutes for deployment

### Step 6: Test Live Dashboard (2 minutes)

- [ ] GitHub will show your URL: `https://YOUR_USERNAME.github.io/breeding-dashboard/`
- [ ] Copy the URL
- [ ] Open in browser
- [ ] Verify everything works:
  - [ ] Dashboard loads
  - [ ] Data shows correctly
  - [ ] Filters work
  - [ ] Auto-refresh toggle works
  - [ ] Mobile responsive (test on phone)

## 🔐 Security Check

- [ ] **API Key Security**:
  - [ ] API key is NOT in any public repository
  - [ ] Consider using GitHub Actions secrets (see DEPLOYMENT.md)
  - [ ] Or keep repository private

- [ ] **Access Control**:
  - [ ] Test view-only access (open in incognito window)
  - [ ] Verify no sensitive data exposed in public view
  - [ ] Test editor login with GitHub token

- [ ] **HTTPS**:
  - [ ] Dashboard URL starts with `https://`
  - [ ] No mixed content warnings
  - [ ] Lock icon in browser address bar

## 👥 Team Rollout

### Share with Team
- [ ] Send dashboard URL to team
- [ ] Include quick start guide:
  ```
  Hi team! 👋

  Our new BC breeding metrics dashboard is live:
  https://YOUR_USERNAME.github.io/breeding-dashboard/

  📊 View all metrics - no login required!
  🔄 Enable auto-refresh for real-time updates
  🎯 Use filters to focus on specific locations/schemes

  Questions? See the Quick Start guide:
  https://YOUR_USERNAME.github.io/breeding-dashboard/QUICKSTART.html

  Enjoy! 🌱
  ```

### For Editors Only
- [ ] Send editor instructions to authorized users:
  ```
  To get edit access:
  1. Generate GitHub token: https://github.com/settings/tokens
  2. Select scope: read:user
  3. Click "Editor Login" on dashboard
  4. Paste your token
  ```

## 📱 Optional Enhancements

### Custom Domain
- [ ] Purchase domain (e.g., dashboard.yourcompany.com)
- [ ] Add CNAME file to repository
- [ ] Configure DNS settings
- [ ] Update GitHub Pages settings

### Notifications
- [ ] Set up email alerts for issues
- [ ] Configure Slack/Teams integration
- [ ] Add webhook for BMS data updates

### Analytics
- [ ] Add Google Analytics (optional)
- [ ] Track usage patterns
- [ ] Monitor performance

## 🧪 Testing Checklist

### Functionality
- [ ] All blocks display correctly (A, B, C, D, F)
- [ ] Funnel metrics show progression
- [ ] Rate cards show percentages
- [ ] Coverage table displays ratios
- [ ] Speed metrics show days
- [ ] Top issues ranked correctly
- [ ] Stack progress shows counts

### Interactions
- [ ] Refresh button works
- [ ] Auto-refresh toggle works
- [ ] Filters apply correctly
- [ ] Login modal opens/closes
- [ ] GitHub authentication works
- [ ] Audit log displays

### Performance
- [ ] Page loads in <2 seconds
- [ ] Charts render smoothly
- [ ] No lag when interacting
- [ ] Data updates within 5 minutes when auto-refresh on

### Compatibility
- [ ] Chrome ✅
- [ ] Firefox ✅
- [ ] Safari ✅
- [ ] Edge ✅
- [ ] Mobile Safari ✅
- [ ] Mobile Chrome ✅

## 📊 Data Verification

### Verify BMS Integration
- [ ] Funnel counts match BMS data
- [ ] Rates calculated correctly
- [ ] Coverage ratios accurate
- [ ] Cycle times match records
- [ ] Issue counts correct

### Check Thresholds
- [ ] Emergence rate: ≥80% = green
- [ ] Sampling rate: ≥95% = green
- [ ] Pollination success: ≥85% = green
- [ ] Coverage ratio: ≥1.2x = green
- [ ] Cycle time: ≤75d = green

## 🐛 Troubleshooting

If something doesn't work:

### Dashboard won't load
- [ ] Check GitHub Pages is enabled
- [ ] Verify repository is public or you're logged in
- [ ] Wait a few minutes for deployment
- [ ] Check Actions tab for deployment errors

### No data showing
- [ ] Verify BMS API key is correct
- [ ] Check program ID is valid
- [ ] Open browser console (F12) for errors
- [ ] Test BMS API directly with curl
- [ ] Check CORS settings on BMS

### Filters not working
- [ ] Clear browser cache
- [ ] Check for JavaScript errors
- [ ] Verify filter values match your data

### Authentication issues
- [ ] GitHub token is valid (not expired)
- [ ] Username in ALLOWED_EDITORS list
- [ ] Token has correct scope (read:user)
- [ ] Clear localStorage and try again

## ✅ Final Checks

Before announcing to team:

- [ ] Dashboard is accessible via public URL
- [ ] All metrics display correctly
- [ ] BMS data is current
- [ ] Auto-refresh works
- [ ] Mobile view is good
- [ ] No console errors
- [ ] README is updated
- [ ] Team has access instructions
- [ ] Backup of API keys saved securely
- [ ] Audit log is working

## 🎉 Launch!

- [ ] Send announcement email
- [ ] Share in team Slack/Teams
- [ ] Demo in next team meeting
- [ ] Collect initial feedback
- [ ] Monitor usage first week

## 📈 Post-Launch

### Week 1
- [ ] Monitor for errors
- [ ] Collect user feedback
- [ ] Answer questions
- [ ] Make quick fixes if needed

### Month 1
- [ ] Review metrics accuracy
- [ ] Check performance
- [ ] Gather improvement ideas
- [ ] Plan enhancements

### Ongoing
- [ ] Monthly review of audit logs
- [ ] Quarterly threshold adjustments
- [ ] Update documentation as needed
- [ ] Add new metrics as requested

---

## Quick Reference

**Dashboard URL**: `https://YOUR_USERNAME.github.io/breeding-dashboard/`

**Support Email**: kaseymarkel@gmail.com

**Documentation**: See README.md, QUICKSTART.md, DEPLOYMENT.md

**BMS Docs**: https://bmspro.io/1596/breeding-management-system/tutorials/

---

🎯 **Current Status**: _____ / _____ items complete

Last updated: _____________

Deployed by: _____________

Launch date: _____________

**Ready to launch?** When all critical items are checked, you're good to go! 🚀
