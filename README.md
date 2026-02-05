# NetHub 🌐💬

A real-time chat application with file sharing, FTP storage, and multiplayer games built with Python sockets and Tkinter.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 💬 **Real-time Chat** - Chat rooms with multiple users
- 📁 **File Sharing** - Upload and download files directly in chat
- 🌐 **FTP Storage** - Personal cloud storage with FTP browser
- 🎮 **Multiplayer Games** - Play Tic-Tac-Toe with other users
- 📊 **Speed Test** - Test your network speed
- 👥 **Admin Features** - View user IP addresses (admin only)
- 🔐 **Authentication** - Register and login system

## 📋 Prerequisites

- **Python 3.8+** installed on your system
- **pip** (Python package manager)

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/nethub.git
cd nethub
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install pyftpdlib speedtest-cli
```

### 4. Create initial user data file

Create a `users.json` file in the project root:

```json
{}
```

Or simply run the server - it will create the file automatically.

## 🎯 How to Run

### Step 1: Start the Chat Server

Open a terminal in the project folder and run:

```bash
python server.py
```

You should see:
```
Server is listening on 127.0.0.1:55555
Files directory: server_files
Users file: users.json
```

### Step 2: Start the FTP Server (Optional)

If you want to use the FTP storage feature, open **another terminal** and run:

```bash
python ftp_server.py
```

The FTP server runs on port `2121`.

### Step 3: Start the Client

Open **another terminal** and run:

```bash
python client_gui.py
```

**First time users:**
1. Enter a username and password
2. Click **"Register"** to create an account
3. Click **"Login"** to enter
4. Select a room (e.g., A-1) and click **"Join Room"**

### Step 4: Multi-User Testing

To test with multiple users:
- Run `python client_gui.py` in multiple terminals
- Each client can register/login with different accounts
- Users in the same room can chat with each other

## 📁 Project Structure

```
nethub/
├── server.py          # Main chat server
├── client_gui.py      # GUI client application
├── client.py          # CLI client (alternative)
├── ftp_server.py      # FTP server for file storage
├── ftp_browser.py     # FTP browser window
├── config.py          # Network and theme configuration
├── network_utils.py   # Socket utilities
├── ui_components.py   # Tkinter UI components
├── game_window.py     # Tic-Tac-Toe game window
├── users.json         # User credentials (auto-created)
├── files_metadata.json # File metadata (auto-created)
├── server_files/      # Uploaded files storage (auto-created)
└── ftp_data/          # FTP user directories (auto-created)
```

## ⚙️ Configuration

Edit `config.py` to change network settings:

```python
# Network Configuration
HOST = '127.0.0.1'  # Change to your server IP for LAN
PORT = 55555        # Chat server port
```

### Running on Local Network (LAN)

1. Find your server's IP address:
   ```bash
   # Windows
   ipconfig
   
   # Linux/macOS
   ifconfig
   ```

2. Update `config.py` with your server IP:
   ```python
   HOST = '192.168.1.xxx'  # Your server IP
   ```

3. Make sure firewall allows ports `55555` (chat) and `2121` (FTP)

## 🎮 Usage Guide

### Chat Features
- Type messages and press Enter or click Send
- Click 😊 button to add emojis
- Click 📤 button to upload files to chat

### FTP Storage
- Click **"Storage"** button to open FTP browser
- Browse, upload, and download files from your personal storage
- Share files from FTP directly to chat

### Tic-Tac-Toe Game
- Click **"🎮 Game"** button to open game window
- Play with other users in the same room

### Speed Test
- Click **"📊 Speed"** button to test your network speed

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Could not connect to server" | Make sure `server.py` is running first |
| FTP not working | Make sure `ftp_server.py` is running |
| Can't connect from another PC | Check firewall and update HOST in `config.py` |
| "Username taken" error | Try a different username |

## 📝 Creating an Admin User

Edit `users.json` to set admin role:

```json
{
    "admin_username": {
        "password": "YOUR_HASHED_PASSWORD",
        "role": "admin"
    }
}
```

> ⚠️ Note: Password must be SHA-256 hashed. Register normally first, then change `"role": "user"` to `"role": "admin"` in `users.json`.

## 📄 License

This project is open source and available under the MIT License.

## 👥 Contributors

- [Your Name](https://github.com/YOUR_USERNAME)

---

Made with ❤️ using Python
