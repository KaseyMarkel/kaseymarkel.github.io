# Deployment Guide

## 🚀 Deploying to GitHub Pages

### Prerequisites
- GitHub account
- Git installed on your computer
- BMS API credentials

### Step-by-Step Deployment

#### 1. Create GitHub Repository

```bash
# Initialize git repository (if not already done)
cd breeding-dashboard
git init

# Create repository on GitHub
# Go to https://github.com/new
# Name it: breeding-dashboard
# Don't initialize with README (we already have one)
```

#### 2. Configure BMS API Credentials

**IMPORTANT**: Do NOT commit your actual API keys to the repository!

Option A: Use a separate config file (recommended):
```bash
# Create a config file that's gitignored
cp index.html index-template.html

# Create config.js (gitignored)
cat > config.js << 'EOF'
const BMS_API_CONFIG = {
    baseUrl: 'https://bmspro.io/api',
    apiKey: 'YOUR_ACTUAL_API_KEY',
    programId: 'YOUR_PROGRAM_ID'
};
EOF

# Update index.html to load config.js
```

Option B: Use GitHub Actions with secrets:
```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure API credentials
        run: |
          sed -i "s/YOUR_BMS_API_KEY/${{ secrets.BMS_API_KEY }}/g" index.html
          sed -i "s/YOUR_PROGRAM_ID/${{ secrets.BMS_PROGRAM_ID }}/g" index.html

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: .
```

Then add secrets in GitHub:
- Go to Settings → Secrets and variables → Actions
- Add `BMS_API_KEY`
- Add `BMS_PROGRAM_ID`

#### 3. Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/breeding-dashboard.git

# Add files
git add .

# Commit
git commit -m "Initial dashboard deployment"

# Push
git push -u origin main
```

#### 4. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings**
3. Scroll to **Pages** section
4. Under **Source**, select:
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

#### 5. Wait for Deployment

- GitHub will build and deploy your site
- Usually takes 1-2 minutes
- Check the Actions tab to see deployment progress

#### 6. Access Your Dashboard

Your dashboard will be available at:
```
https://YOUR_USERNAME.github.io/breeding-dashboard/
```

### Custom Domain (Optional)

If you want to use a custom domain like `dashboard.yourcompany.com`:

1. **Add CNAME file**:
   ```bash
   echo "dashboard.yourcompany.com" > CNAME
   git add CNAME
   git commit -m "Add custom domain"
   git push
   ```

2. **Configure DNS**:
   Add a CNAME record in your DNS provider:
   ```
   CNAME   dashboard   YOUR_USERNAME.github.io
   ```

3. **Update GitHub Pages settings**:
   - Go to Settings → Pages
   - Enter your custom domain
   - Enable "Enforce HTTPS"

## 🔐 Secure Configuration

### Environment-Specific Configuration

For different environments (dev, staging, production):

```javascript
// config.js
const ENV = window.location.hostname === 'localhost' ? 'dev' : 'production';

const CONFIGS = {
    dev: {
        baseUrl: 'https://bmspro-dev.io/api',
        apiKey: 'dev_key',
        programId: 'dev_program'
    },
    production: {
        baseUrl: 'https://bmspro.io/api',
        apiKey: 'prod_key',
        programId: 'prod_program'
    }
};

const BMS_API_CONFIG = CONFIGS[ENV];
```

### Editor Access Control

Update allowed editors in `index.html`:

```javascript
const ALLOWED_EDITORS = [
    'kaseymarkel',
    'teammate1',
    'teammate2'
];

const auth = new DashboardAuth({
    allowedEditors: ALLOWED_EDITORS
});
```

## 📊 Alternative Hosting Options

### Netlify (Alternative to GitHub Pages)

1. **Sign up**: https://netlify.com
2. **Deploy**:
   ```bash
   # Install Netlify CLI
   npm install -g netlify-cli

   # Deploy
   netlify deploy --prod
   ```

3. **Configure**:
   - Set environment variables in Netlify dashboard
   - Enable password protection if needed

### Vercel

1. **Sign up**: https://vercel.com
2. **Deploy**:
   ```bash
   # Install Vercel CLI
   npm install -g vercel

   # Deploy
   vercel --prod
   ```

### Self-Hosted

If you have your own server:

```bash
# Copy files to your web server
scp -r * user@yourserver.com:/var/www/dashboard/

# Configure nginx/apache to serve the files
# Ensure HTTPS is enabled
```

## 🔄 Updating the Dashboard

### Method 1: Direct Git Push

```bash
# Make your changes
git add .
git commit -m "Update dashboard metrics"
git push

# GitHub Pages will auto-deploy
```

### Method 2: GitHub Web Interface

1. Go to your repository on GitHub
2. Click on the file you want to edit
3. Click the pencil icon (Edit)
4. Make changes
5. Commit directly to main branch

### Method 3: Automated Updates

Set up a scheduled GitHub Action to pull latest data:

```yaml
# .github/workflows/update-data.yml
name: Update Dashboard Data

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Fetch latest BMS data
        run: |
          # Your script to fetch and cache data
          node fetch-data.js

      - name: Commit updates
        run: |
          git config user.name "Dashboard Bot"
          git config user.email "bot@example.com"
          git add data/
          git commit -m "Auto-update dashboard data" || exit 0
          git push
```

## 🧪 Testing Before Deployment

### Local Testing

```bash
# Simple HTTP server
python -m http.server 8000

# Or use npm package
npx http-server -p 8000

# Navigate to http://localhost:8000
```

### Test Checklist

- [ ] BMS API connection working
- [ ] All metrics displaying correctly
- [ ] Filters working
- [ ] Auto-refresh functioning
- [ ] Mobile responsive
- [ ] Authentication working
- [ ] No console errors
- [ ] Data updates correctly

## 📈 Monitoring

### GitHub Pages Status

Monitor your deployment:
- Check Actions tab for deployment status
- View deployment history
- See build logs

### Analytics (Optional)

Add Google Analytics:

```html
<!-- Add to index.html before </head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## 🆘 Troubleshooting

### Build Fails

1. Check Actions tab for error messages
2. Verify all files are committed
3. Ensure no syntax errors in HTML/JS

### Dashboard Not Accessible

1. Verify GitHub Pages is enabled
2. Check repository is public (or you have Pages enabled for private repos)
3. Wait a few minutes for DNS propagation

### API Errors

1. Verify API credentials are correct
2. Check CORS settings on BMS API
3. Test API endpoints with curl/Postman

### Authentication Not Working

1. Check GitHub token is valid
2. Verify username in allowedEditors list
3. Clear browser cache and localStorage

## 🔒 Security Best Practices

1. **Never commit API keys**:
   - Use GitHub secrets
   - Or environment-specific config files
   - Add to .gitignore

2. **Use HTTPS**:
   - Always enable "Enforce HTTPS" in GitHub Pages

3. **Access Control**:
   - Regularly review allowed editors list
   - Rotate API keys periodically
   - Monitor audit logs

4. **Rate Limiting**:
   - Implement client-side rate limiting
   - Cache API responses
   - Don't abuse BMS API

## 📞 Support

Issues with deployment?
- Check GitHub Pages documentation: https://docs.github.com/en/pages
- Contact: kaseymarkel@gmail.com
- BMS Support: https://bmspro.io/support

---

Happy deploying! 🚀
