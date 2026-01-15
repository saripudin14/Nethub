import socket
import threading
import json
import hashlib
import os
import base64

# Configuration
HOST = '127.0.0.1'
PORT = 55555
FILES_DIR = 'server_files'
USERS_FILE = 'users.json'

if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

FILES_METADATA_FILE = 'files_metadata.json'

# --- File Metadata Management ---
def load_files_metadata():
    if not os.path.exists(FILES_METADATA_FILE):
        return {}
    try:
        with open(FILES_METADATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_files_metadata(metadata):
    with open(FILES_METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4)

def register_file(filename, room):
    metadata = load_files_metadata()
    metadata[filename] = room
    save_files_metadata(metadata)

def can_access_file(filename, user_room):
    metadata = load_files_metadata()
    if filename not in metadata:
        return False # OR True if we want global legacy files, but safer to default False
    return metadata[filename] == user_room

# --- User Management (JSON) ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    # New format with role
    users[username] = {
        "password": hash_password(password),
        "role": "user"
    }
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, None
    
    hashed = hash_password(password)
    user_obj = users[username]
    
    # Backward compatibility
    if isinstance(user_obj, str):
        stored_pass = user_obj
        role = "user"
    else:
        stored_pass = user_obj["password"]
        role = user_obj["role"]

    if hashed == stored_pass:
        return True, role
    return False, None

# --- Global State ---
clients = {} # socket -> {'username': str, 'room': str, 'role': str, 'addr': tuple}
lock = threading.Lock()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

def broadcast_to_room(room, message):
    with lock:
        to_remove = []
        for client_sock, data in clients.items():
            if data.get('room') == room:
                try:
                    client_sock.send((message + "\n").encode('utf-8'))
                except:
                    to_remove.append(client_sock)
        
        for sock in to_remove:
            # We don't call remove_client here to avoid recursion loop, just close
            try:
                del clients[sock]
                sock.close()
            except: pass

def broadcast_user_list(room):
    simple_list = []
    admin_list = []
    
    with lock:
        # Collect data
        temp_users = [] 
        for c, v in clients.items():
            if v['room'] == room:
                username = v.get('username', 'Unknown')
                addr = v.get('addr', ('?', '?'))
                ip_info = f"{addr[0]}:{addr[1]}"
                temp_users.append((username, ip_info))
        
        if not temp_users: return

        temp_users.sort(key=lambda x: x[0])
        simple_list = [u[0] for u in temp_users]
        # Admin format: "username#IP:Port" (Using # to avoid pipe conflict)
        admin_list = [f"{u[0]}#{u[1]}" for u in temp_users] 
        
        print(f"DEBUG: Room {room} Users: {simple_list}")

    simple_payload = "USERLIST|" + ",".join(simple_list)
    admin_payload = "USERLIST_ADMIN|" + ",".join(admin_list)

    # Send appropriately
    with lock:
        for c, v in clients.items():
            if v['room'] == room:
                role = v.get('role', 'user')
                try:
                    if role == 'admin':
                        c.send((admin_payload + "\n").encode('utf-8'))
                    else:
                        c.send((simple_payload + "\n").encode('utf-8'))
                except:
                    pass

def remove_client(client):
    username = None
    room = None
    with lock:
        if client in clients:
            username = clients[client].get('username')
            room = clients[client].get('room')
            del clients[client]
            client.close()
    
    if room and username:
        broadcast_to_room(room, f"SERVER|{username} left the room.")
        broadcast_user_list(room)

# Buffer class
class SocketBuffer:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = ""

    def read_line(self):
        while "\n" not in self.buffer:
            try:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    return None
                self.buffer += data
            except:
                return None
        
        line, self.buffer = self.buffer.split("\n", 1)
        return line

def handle_client(client, addr):
    buf = SocketBuffer(client)
    
    try:
        while True:
            message = buf.read_line()
            if message is None:
                break
            
            parts = message.split('|')
            command = parts[0]

            if command == 'REGISTER':
                if len(parts) >= 3:
                    u = parts[1]
                    p = parts[2]
                    if register_user(u, p):
                        client.send("REGISTER_SUCCESS\n".encode('utf-8'))
                    else:
                        client.send("REGISTER_FAIL|Username taken\n".encode('utf-8'))

            elif command == 'LOGIN':
                if len(parts) >= 3:
                    u = parts[1]
                    p = parts[2]
                    success, role = login_user(u, p)
                    if success:
                        with lock:
                            clients[client] = {'username': u, 'room': None, 'role': role, 'addr': addr}
                        client.send(f"LOGIN_SUCCESS|{u}\n".encode('utf-8'))
                    else:
                        client.send("LOGIN_FAIL|Invalid credentials\n".encode('utf-8'))
    
            elif command == 'JOIN_ROOM':
                if len(parts) >= 2:
                    room_name = parts[1]
                    username = ""
                    with lock:
                        if client in clients:
                            clients[client]['room'] = room_name
                            username = clients[client]['username']
                    
                    if username:
                        client.send(f"ROOM_JOINED|{room_name}\n".encode('utf-8'))
                        broadcast_to_room(room_name, f"SERVER|{username} joined the room.")
                        broadcast_user_list(room_name)

            elif command == 'MSG':
                if len(parts) >= 2:
                    content = parts[1]
                    user, room = "", ""
                    with lock:
                        if client in clients:
                            user = clients[client]['username']
                            room = clients[client]['room']
                    
                    if room:
                        msg_to_send = f"MSG|{user}|{content}"
                        broadcast_to_room(room, msg_to_send)

            elif command == 'GAME':
                # Join all remaining parts to capture full payload
                content = "|".join(parts[1:])
                user, room = "", ""
                with lock:
                    if client in clients:
                        user = clients[client]['username']
                        room = clients[client]['room']
                
                if room:
                    msg_to_send = f"GAME|{user}|{content}"
                    broadcast_to_room(room, msg_to_send)

            elif command == 'UPLOAD':
                parts_upload = message.split('|', 3)
                if len(parts_upload) >= 3:
                    filename = parts_upload[1]
                    file_data = parts_upload[2]
                    
                    user, room = "", ""
                    with lock:
                        if client in clients:
                            user = clients[client]['username']
                            room = clients[client]['room']

                    if room:
                        filepath = os.path.join(FILES_DIR, filename)
                        register_file(filename, room)

                        with open(filepath, "wb") as f:
                            f.write(base64.b64decode(file_data))
                        
                        broadcast_to_room(room, f"FILE_NOTIF|{user}|{filename}")

            elif command == 'DOWNLOAD':
                if len(parts) >= 2:
                    filename = parts[1]
                    user_room = None
                    with lock:
                        if client in clients:
                            user_room = clients[client].get('room')

                    if user_room and can_access_file(filename, user_room):
                        filepath = os.path.join(FILES_DIR, filename)
                        if os.path.exists(filepath):
                            with open(filepath, "rb") as f:
                                b64_data = base64.b64encode(f.read()).decode('utf-8')
                                client.send(f"FILE_DATA|{filename}|{b64_data}\n".encode('utf-8'))
                    else:
                         client.send(f"SERVER|Access Denied or File Not Found.\n".encode('utf-8'))

    except Exception as e:
        print(f"Error handling client: {e}")
    
    remove_client(client)

def receive():
    print(f"Server is listening on {HOST}:{PORT}")
    print(f"Files directory: {FILES_DIR}")
    print(f"Users file: {USERS_FILE}")
    
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        # Pass address to handle_client
        thread = threading.Thread(target=handle_client, args=(client, address))
        thread.start()

if __name__ == "__main__":
    receive()
