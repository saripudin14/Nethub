import socket
import threading

# Configuration
HOST = '127.0.0.1'  # localhost
PORT = 55555

# Setup client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Prompt for nickname
nickname = input("Choose your nickname: ")

try:
    client.connect((HOST, PORT))
except ConnectionRefusedError:
    print("Could not connect to server. Ensure server.py is running first.")
    exit()

def receive():
    """Listens for incoming messages from the server."""
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    """Sends user input messages to the server."""
    while True:
        try:
            text = input("")
            message = f'{nickname}: {text}'
            client.send(message.encode('ascii'))
        except:
            break

# Start threads for sending and receiving
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
