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
