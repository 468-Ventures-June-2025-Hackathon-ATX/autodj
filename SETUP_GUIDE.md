# 🎧 AutoDJ Setup Guide

Complete guide to get AutoDJ working with full audio automation.

## 📋 **Required Setup Checklist**

### **1. Essential API Keys (Required)**

#### **OpenAI API Key** ⭐ **REQUIRED**
- **Purpose**: Track analysis, style matching, playlist descriptions
- **Cost**: ~$0.01-0.05 per track analysis
- **How to get**:
  1. Go to [OpenAI Platform](https://platform.openai.com)
  2. Create account and add payment method
  3. Go to API Keys section
  4. Create new secret key
  5. Copy key to `.env` file

#### **Perplexity API Key** ⭐ **REQUIRED**
- **Purpose**: AI-powered artist discovery and music research
- **Cost**: ~$0.001 per search query
- **How to get**:
  1. Go to [Perplexity API](https://www.perplexity.ai/settings/api)
  2. Create account
  3. Generate API key
  4. Copy key to `.env` file

### **2. Optional API Keys**

#### **Beatport API Key** (Optional)
- **Purpose**: Official track metadata (currently using web scraping)
- **Status**: Not publicly available - using web scraping instead
- **Note**: Leave blank in `.env` file

### **3. Beatport Account (For Audio Downloads)**

#### **Beatport Login Credentials** ⚠️ **USE AT YOUR OWN RISK**
- **Purpose**: Automated track purchasing and downloading
- **Legal Warning**: Violates Beatport Terms of Service
- **Requirements**:
  - Valid Beatport account with payment method
  - Email and password
  - Sufficient account balance for purchases

## 🔧 **System Dependencies**

### **Required Software**

#### **Python 3.11** ✅ **INSTALLED**
```bash
python --version  # Should show 3.11.x
```

#### **FFmpeg** ✅ **AVAILABLE**
- **Purpose**: Audio processing and conversion
- **Status**: Already available on your system
- **Install if missing**:
  ```bash
  # macOS
  brew install ffmpeg
  
  # Ubuntu/Debian
  sudo apt install ffmpeg
  
  # Windows
  # Download from https://ffmpeg.org/download.html
  ```

#### **ChromeDriver** ✅ **AVAILABLE**
- **Purpose**: Web automation for Beatport
- **Status**: Already available on your system
- **Install if missing**:
  ```bash
  # macOS
  brew install chromedriver
  
  # Ubuntu/Debian
  sudo apt install chromium-chromedriver
  
  # Windows
  # Download from https://chromedriver.chromium.org/
  ```

## 📝 **Configuration Steps**

### **Step 1: Create .env File**
```bash
cp .env.example .env
```

### **Step 2: Add API Keys to .env**
```bash
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here

# Optional - leave blank
BEATPORT_API_KEY=

# Optional - for audio downloads (USE AT YOUR OWN RISK)
BEATPORT_EMAIL=your-beatport-email@example.com
BEATPORT_PASSWORD=your-beatport-password

# Reddit API (optional - for future features)
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=AutoDJ:v1.0 (by /u/your_username)
```

### **Step 3: Install Dependencies**
```bash
# Activate virtual environment
source autodj_env/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### **Step 4: Test Setup**
```bash
# Test basic functionality
python main.py setup

# Test audio automation dependencies
python main.py audio-status

# Test with demo data
python demo.py
```

## 💰 **Cost Breakdown**

### **API Costs (Per 25 Tracks)**
- **OpenAI**: ~$0.25-1.25 (track analysis)
- **Perplexity**: ~$0.01-0.05 (artist discovery)
- **Total API Cost**: ~$0.26-1.30 per playlist

### **Beatport Costs (If Using Automation)**
- **Track Prices**: $1.49-2.99 per track
- **25 Tracks**: ~$37-75
- **Note**: Uses your existing Beatport account and payment method

## 🚀 **Usage Examples**

### **Playlist Only (No Audio Downloads)**
```bash
# Requires: OpenAI + Perplexity API keys
python main.py discover --count 25 --export
```

### **Full Audio Automation**
```bash
# Requires: OpenAI + Perplexity + Beatport credentials
python main.py download --count 10 \
  --beatport-email your@email.com \
  --beatport-password yourpassword
```

### **Free Sources Only**
```bash
# No Beatport credentials - uses free/legal sources only
python main.py download --count 25
```

## ⚠️ **Important Warnings**

### **Beatport Automation Risks**
1. **Terms of Service**: Violates Beatport ToS
2. **Account Risk**: Possible account suspension
3. **Legal Risk**: Use at your own discretion
4. **Rate Limiting**: Built-in delays to avoid detection

### **Recommended Approach**
1. **Start with playlist-only**: Use `discover` command first
2. **Manual downloads**: Use generated Beatport links to buy tracks legally
3. **Automation**: Only if you accept the risks

## 🔍 **Troubleshooting**

### **Common Issues**

#### **"No tracks discovered"**
- Check OpenAI API key is valid
- Check Perplexity API key is valid
- Verify internet connection

#### **"ChromeDriver not found"**
```bash
# Install ChromeDriver
brew install chromedriver  # macOS
```

#### **"FFmpeg not found"**
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
```

#### **"Beatport login failed"**
- Verify email/password are correct
- Check if account has 2FA enabled (not supported)
- Try with `--no-headless` to see browser

### **Test Commands**
```bash
# Check all dependencies
python main.py audio-status

# Test API keys
python main.py setup

# Test basic discovery
python main.py discover --count 5

# Test audio automation (no Beatport)
python main.py download --count 3
```

## 📊 **Current Status Check**

Run this to see what's working:
```bash
python main.py audio-status
```

Expected output:
```
🛠️ Dependencies
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Tool          ┃ Status       ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ ffmpeg        │ ✅ Available │
│ chrome_driver │ ✅ Available │
│ mutagen       │ ✅ Available │
│ selenium      │ ✅ Available │
└───────────────┴──────────────┘
```

## 🎯 **Quick Start (Minimal Setup)**

**Just want to try it? Minimum requirements:**

1. **Get OpenAI API key** ($5 credit is enough for testing)
2. **Get Perplexity API key** (free tier available)
3. **Add to .env file**
4. **Run**: `python main.py discover --count 10 --export`

This gives you Pioneer-ready playlists with download links - no automation risks!
