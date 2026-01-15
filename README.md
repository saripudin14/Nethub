# Simple Python Chat App

A simple Command Line Interface (CLI) chat application using Python `socket` and `threading`.

## Prerequisites
- Python installed on your system.

## How to Run

1. **Start the Server** first:
   Open a terminal and run:
   ```bash
   python server.py
   ```
   You will see: `Server is listening on 127.0.0.1:55555...`

2. **Start a Client**:
   
   **Option A: GUI Client (Recommended)**
   Open a new terminal and run:
   ```bash
   python client_gui.py
   ```
   - A popup will ask for your nickname.
   - The chat window will open.
   
   **Option B: CLI Client**
   Open a new terminal and run:
   ```bash
   python client.py
   ```

3. **Multi-User Chat**:
   - Run `client_gui.py` multiple times to open multiple chat windows.
   - All users (GUI and CLI) can talk to each other.
