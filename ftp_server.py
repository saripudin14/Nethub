"""
NetHub FTP Server
FTP server yang terintegrasi dengan sistem autentikasi NetHub.
Menggunakan pyftpdlib untuk implementasi FTP protocol.
"""

import os
import json
import hashlib
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Configuration
FTP_HOST = '127.0.0.1'
FTP_PORT = 2121
FTP_DATA_DIR = 'ftp_data'
USERS_FILE = 'users.json'

# Create FTP data directory if not exists
if not os.path.exists(FTP_DATA_DIR):
    os.makedirs(FTP_DATA_DIR)

def hash_password(password):
    """Hash password using SHA-256 (same as main server)"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def create_user_directory(username):
    """Create a personal directory for each user"""
    user_dir = os.path.join(FTP_DATA_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return os.path.abspath(user_dir)

class NetHubAuthorizer(DummyAuthorizer):
    """Custom authorizer that validates against users.json"""
    
    def validate_authentication(self, username, password, handler):
        """Validate username/password against stored credentials"""
        users = load_users()
        
        if username not in users:
            raise AuthenticationFailed("Invalid username or password.")
        
        user_data = users[username]
        hashed_input = hash_password(password)
        
        # Handle both old format (string) and new format (dict)
        if isinstance(user_data, str):
            stored_hash = user_data
        else:
            stored_hash = user_data.get("password", "")
        
        if hashed_input != stored_hash:
            raise AuthenticationFailed("Invalid username or password.")
        
        # Create user directory and add to authorizer dynamically
        user_dir = create_user_directory(username)
        
        # Check if user role is admin
        is_admin = False
        if isinstance(user_data, dict):
            is_admin = user_data.get("role") == "admin"
        
        # Add user with permissions
        if is_admin:
            # Admin: full access to entire FTP directory
            perm = "elradfmw"
            home = os.path.abspath(FTP_DATA_DIR)
        else:
            # Regular user: access to own folder only
            perm = "elradfmw"
            home = user_dir
        
        if not self.has_user(username):
            self.add_user(username, password, home, perm=perm)
        
        return True

    def has_user(self, username):
        """Check if user exists"""
        return username in self.user_table

    def get_home_dir(self, username):
        """Return the user's home directory"""
        if username in self.user_table:
            return self.user_table[username]['home']
        # Default to user's personal folder
        return create_user_directory(username)

    def get_perms(self, username):
        """Return user permissions"""
        if username in self.user_table:
            return self.user_table[username]['perm']
        return "elradfmw"

    def get_msg_login(self, username):
        """Return login greeting message"""
        return f"Welcome to NetHub FTP Server, {username}!"

    def get_msg_quit(self, username):
        """Return quit message"""
        return "Goodbye from NetHub FTP Server!"


class AuthenticationFailed(Exception):
    """Exception for authentication failures"""
    pass


class NetHubFTPHandler(FTPHandler):
    """Custom FTP handler with NetHub authentication"""
    
    def on_connect(self):
        print(f"[FTP] Connection from {self.remote_ip}:{self.remote_port}")
    
    def on_disconnect(self):
        print(f"[FTP] Disconnected: {self.remote_ip}:{self.remote_port}")
    
    def on_login(self, username):
        print(f"[FTP] User logged in: {username}")
    
    def on_logout(self, username):
        print(f"[FTP] User logged out: {username}")
    
    def on_file_received(self, file):
        print(f"[FTP] File uploaded: {file}")
    
    def on_file_sent(self, file):
        print(f"[FTP] File downloaded: {file}")


def main():
    """Start the FTP server"""
    # Create authorizer
    authorizer = NetHubAuthorizer()
    
    # Add anonymous access (read-only to public folder)
    public_dir = os.path.join(FTP_DATA_DIR, 'public')
    if not os.path.exists(public_dir):
        os.makedirs(public_dir)
    authorizer.add_anonymous(public_dir, perm='elr')
    
    # Setup handler
    handler = NetHubFTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = range(60000, 60100)  # Passive mode ports
    
    # Banner
    handler.banner = "Welcome to NetHub FTP Server. Login with your NetHub credentials."
    
    # Create and start server
    server = FTPServer((FTP_HOST, FTP_PORT), handler)
    server.max_cons = 50
    server.max_cons_per_ip = 5
    
    print("=" * 50)
    print("NetHub FTP Server")
    print("=" * 50)
    print(f"Host: {FTP_HOST}")
    print(f"Port: {FTP_PORT}")
    print(f"Data Directory: {os.path.abspath(FTP_DATA_DIR)}")
    print(f"Users File: {USERS_FILE}")
    print("=" * 50)
    print("FTP Commands:")
    print("  - Connect: ftp://127.0.0.1:2121")
    print("  - Login with your NetHub username/password")
    print("  - Anonymous access: read-only to /public")
    print("=" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[FTP] Server shutting down...")
        server.close_all()


if __name__ == "__main__":
    main()
