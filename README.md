# LinkedIn Profile Scraper

A simple Python tool I built to extract profile data from LinkedIn for networking and research purposes.

## About

This project allows you to scrape LinkedIn profiles using your own login session. I created it to help with lead generation and professional networking research.

## Features

- 🔐 Secure login with your LinkedIn account
- 📊 Comprehensive data extraction (experience, education, skills, etc.)
- 📄 Export to CSV and Excel formats
- ⚡ Rate limiting to respect LinkedIn's servers
- 🛡️ Ethical scraping practices

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your LinkedIn credentials** to `.env`:
   ```
   LINKEDIN_EMAIL=your_email@gmail.com
   LINKEDIN_PASSWORD=your_password
   ```

3. **Add profile URLs** to `data/profile_urls.txt`

4. **Run the scraper:**
   ```bash
   python main.py
   ```

## Data Extracted

- Basic info (name, headline, location)
- Professional experience (up to 3 positions)
- Education background (up to 3 entries)
- Skills and endorsements
- Contact information (when available)
- Profile picture URL
- And much more...

## Output

Results are saved in `data/output/` as:
- CSV file for easy analysis
- Excel file for better viewing
- JSON file for programmatic use

## Legal Note

This tool is for educational and personal research purposes. Please respect LinkedIn's Terms of Service and use responsibly with appropriate delays between requests.

## 🌐 Live Hosting

### 🚀 Railway (FREE & Easy) - Recommended

**Deploy in 5 minutes:**

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "LinkedIn scraper"
   git remote add origin https://github.com/YOUR_USERNAME/linkedin-scraper.git
   git push -u origin main
   ```

2. **Deploy to Railway:**
   - Sign up at [railway.app](https://railway.app)
   - Connect your GitHub repo
   - Add environment variables:
     - `LINKEDIN_EMAIL` = your email
     - `LINKEDIN_PASSWORD` = your password
   - Deploy automatically!

3. **Access your live scraper:**
   - URL: `your-app.railway.app`
   - Web interface ready to use!

**Benefits:**
- ✅ Completely FREE ($5 monthly credit)
- ✅ Auto Chrome installation
- ✅ No server management
- ✅ Auto-deploy on code changes

📖 **Detailed instructions:** See `RAILWAY_DEPLOY.md`

### Alternative: VPS Hosting

1. **Get a VPS** (if you prefer full control):
   - DigitalOcean: $5/month droplet
   - Linode: $5/month VPS
   - Vultr: $6/month instance
   - AWS EC2: t2.micro (free tier)

2. **Setup your server:**
   ```bash
   # Upload your project files to server
   scp -r linkedinnn/ root@your-server-ip:~/
   
   # SSH into your server
   ssh root@your-server-ip
   
   # Run setup script
   cd linkedinnn
   chmod +x deploy_server.sh start.sh
   ./deploy_server.sh
   ```

3. **Configure your credentials:**
   ```bash
   # Edit .env with your LinkedIn login
   nano .env
   
   # Add profile URLs to scrape
   nano data/profile_urls.txt
   ```

4. **Start the scraper:**
   ```bash
   # Option A: Web interface (recommended)
   xvfb-run -a python3 web_app.py
   # Access at http://your-server-ip:5000
   
   # Option B: Command line
   xvfb-run -a python3 main.py
   
   # Option C: Background mode
   nohup xvfb-run -a python3 main.py > scraper.log 2>&1 &
   ```

### Web Interface Features

- 📱 Browser-based control panel
- ⚡ Start/stop scraping remotely
- 📊 Real-time status monitoring
- 📥 Download results (CSV/JSON)
- 🔄 Progress tracking

### Server Requirements

- Ubuntu 22.04 LTS (recommended)
- 1-2GB RAM minimum
- Chrome browser + dependencies
- Virtual display (Xvfb) for headless operation

### Firewall Setup

```bash
# Allow web interface (optional)
sudo ufw allow 5000

# Allow SSH
sudo ufw allow 22
sudo ufw enable
```

### Troubleshooting

**Chrome issues?**
```bash
# Check Chrome installation
google-chrome --version

# Reinstall if needed
sudo apt remove google-chrome-stable
sudo apt install google-chrome-stable
```

**Display issues?**
```bash
# Check Xvfb is running
ps aux | grep Xvfb

# Start manually if needed
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

## Author

Built with ❤️ for networking research