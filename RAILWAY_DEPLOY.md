# Railway Deployment Instructions

## 🚀 Deploy Your LinkedIn Scraper to Railway (FREE)

### Step 1: Prepare Your Code

```bash
# Navigate to your project
cd C:\Users\harsh\Desktop\linkedinnn

# Initialize Git repository
git init

# Add all files
git add .

# Commit your code
git commit -m "LinkedIn scraper ready for Railway deployment"
```

### Step 2: Push to GitHub

```bash
# Create repository on GitHub (github.com/new)
# Then connect your local repo:

git remote add origin https://github.com/YOUR_USERNAME/linkedin-scraper.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway

1. **Sign up at Railway:**
   - Go to https://railway.app
   - Sign up with GitHub account

2. **Create new project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `linkedin-scraper` repository

3. **Set Environment Variables:**
   - Go to your Railway project dashboard
   - Click "Variables" tab
   - Add these variables:
     ```
     LINKEDIN_EMAIL = your_linkedin_email@gmail.com
     LINKEDIN_PASSWORD = your_linkedin_password
     ```

4. **Deploy:**
   - Railway automatically builds and deploys
   - Wait for deployment to complete (~5 minutes)
   - Get your app URL: `your-app-name.railway.app`

### Step 4: Use Your Live Scraper

1. **Access web interface:**
   ```
   https://your-app-name.railway.app
   ```

2. **Add LinkedIn URLs to scrape**

3. **Start scraping and download results!**

## 💡 Pro Tips

- **Free tier:** Railway gives you $5 credit monthly
- **Auto-sleep:** App sleeps when not used (saves credits)
- **Logs:** Check Railway dashboard for error logs
- **Updates:** Push to GitHub = auto-redeploy

## 🔧 Troubleshooting

**Chrome issues?**
- Check Railway logs for errors
- Chrome should auto-install via railway_start.sh

**Environment variables not working?**
- Double-check spelling in Railway dashboard
- Redeploy after adding variables

**App not starting?**
- Check Railway build logs
- Verify all files are pushed to GitHub