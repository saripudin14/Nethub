import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox,  ttk, filedialog
import base64
import os
import speedtest
from datetime import datetime

# Custom modules
from config import HOST, PORT, COLORS
from network_utils import SocketBuffer
from game_window import TicTacToeWindow
from ui_components import NetHubUI

class NetHubApp:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        try:
            self.client.connect((HOST, PORT))
            self.connected = True
        except:
            messagebox.showerror("Connection Error", "Could not connect to server.")
            exit()

        self.root = tk.Tk()
        self.root.title("NetHub")
        self.root.geometry("450x700")
        self.root.configure(bg=COLORS["bg_dark"])
        
        # Initialize UI Components
        self.ui = NetHubUI(self.root)
        self.ui.setup_styles()

        self.username = None
        self.current_room = None
        self.running = True
        self.sock_buffer = SocketBuffer(self.client)
        self.game_window = None 

        # UI Frames
        self.login_frame = ttk.Frame(self.root)
        self.room_frame = ttk.Frame(self.root)
        self.chat_frame = ttk.Frame(self.root)

        # Build UI using Helper Class
        self.ui.create_login_frame(self.login_frame, self.do_login, self.do_register)
        self.ui.create_room_frame(self.room_frame, self.do_join_room)
        self.ui.create_chat_frame(self.chat_frame, 
                                  on_speed=self.check_speed, 
                                  on_game=self.open_game, 
                                  on_upload=self.upload_file, 
                                  on_send=self.send_message,
                                  on_emoji=self.open_emoji_picker)

        # Start with Login
        self.show_frame(self.login_frame)

        # Network Thread
        self.thread = threading.Thread(target=self.receive)
        self.thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def show_frame(self, frame):
        self.login_frame.pack_forget()
        self.room_frame.pack_forget()
        self.chat_frame.pack_forget()
        frame.pack(fill="both", expand=True)

    # --- Actions ---
    def open_emoji_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Emojis")
        picker.geometry("250x200")
        picker.config(bg=COLORS["bg_dark"])
        
        emojis = ["😀", "😂", "🤩", "😍", "🥰", 
                  "😎", "😭", "😤", "😡", "🤡",
                  "👻", "💀", "👍", "👎", "👋",
                  "🔥", "❤️", "✨", "💯", "✅"]
        
        cols = 5
        for i, em in enumerate(emojis):
            btn = tk.Button(picker, text=em, font=("Segoe UI", 14), 
                            bg=COLORS["bg_lighter"], fg="white", bd=0, activebackground=COLORS["primary"],
                            command=lambda e=em: [self.ui.msg_entry.insert('end', e), picker.destroy()])
            btn.grid(row=i//cols, column=i%cols, padx=2, pady=2, sticky="nsew")
        
        for i in range(cols): picker.columnconfigure(i, weight=1)
        for i in range(len(emojis)//cols + 1): picker.rowconfigure(i, weight=1)
    def send_packet(self, text):
        try:
            self.client.send((text + "\n").encode('utf-8'))
        except:
             messagebox.showerror("Error", "Connection lost.")
             self.on_close()

    def do_login(self):
        u = self.ui.entry_user.get()
        p = self.ui.entry_pass.get()
        if u and p:
            self.send_packet(f"LOGIN|{u}|{p}")

    def do_register(self):
        u = self.ui.entry_user.get()
        p = self.ui.entry_pass.get()
        if u and p:
            self.send_packet(f"REGISTER|{u}|{p}")

    def do_join_room(self):
        letter = self.ui.combo_letter.get()
        number = self.ui.combo_number.get()
        room_id = f"{letter}-{number}"
        self.send_packet(f"JOIN_ROOM|{room_id}")

    def send_message(self):
        msg = self.ui.msg_entry.get()
        if msg:
            self.send_packet(f"MSG|{msg}")
            self.ui.msg_entry.delete(0, 'end')

    def upload_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            filename = os.path.basename(filepath)
            threading.Thread(target=self._upload_thread, args=(filepath, filename)).start()

    def _upload_thread(self, filepath, filename):
        try:
            with open(filepath, "rb") as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
                self.root.after(0, lambda: self.send_packet(f"UPLOAD|{filename}|{file_data}"))
            self.root.after(0, lambda: messagebox.showinfo("Upload", "File uploaded successfully!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Upload failed: {e}"))

    def request_download(self, filename):
        self.send_packet(f"DOWNLOAD|{filename}")

    def save_file(self, filename, b64_data):
        save_path = filedialog.asksaveasfilename(initialfile=filename)
        if save_path:
            threading.Thread(target=self._save_thread, args=(save_path, b64_data)).start()
    
    def _save_thread(self, save_path, b64_data):
        try:
            with open(save_path, "wb") as f:
                f.write(base64.b64decode(b64_data))
            self.root.after(0, lambda: messagebox.showinfo("Download", "File saved successfully!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Save failed: {e}"))
    
    # --- Speed Test ---
    def check_speed(self):
        self.add_local_msg("running network speed test...", "system")
        threading.Thread(target=self.run_speedtest).start()

    def run_speedtest(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            dl = st.download() / 1_000_000
            ul = st.upload() / 1_000_000
            msg = f"Speed Test Finished:\nDownload: {dl:.2f} Mbps\nUpload: {ul:.2f} Mbps"
            self.root.after(0, lambda: self.add_local_msg(msg, "system"))
        except Exception as e:
            self.root.after(0, lambda: self.add_local_msg(f"Speed Test Failed: {e}", "system"))

    # --- Game Logic ---
    def open_game(self):
        if self.game_window is None or not tk.Toplevel.winfo_exists(self.game_window.top):
            self.game_window = TicTacToeWindow(self.root, self.send_packet, self.username)
        else:
            self.game_window.top.lift()

    # --- Display Logic ---
    def add_chat(self, user, content, type="msg"):
        self.ui.chat_area.config(state='normal')
        
        if type == "server":
            self.ui.chat_area.insert('end', f"\n---------------- {content} ----------------\n", "system")
        else:
            is_me = (user == self.username)
            username_tag = "username_self" if is_me else "username_other"
            timestamp = datetime.now().strftime("%H:%M")
            
            self.ui.chat_area.insert('end', f"\n{user}", username_tag)
            self.ui.chat_area.insert('end', f" [{timestamp}] says:\n", "timestamp") 
            self.ui.chat_area.insert('end', f"{content}\n", "bubble")
            
        self.ui.chat_area.yview('end')
        self.ui.chat_area.config(state='disabled')

    def add_local_msg(self, content, type="msg"):
        self.ui.chat_area.config(state='normal')
        if type == "system":
             self.ui.chat_area.insert('end', f"\n--- {content} ---\n", "system")
        self.ui.chat_area.yview('end')
        self.ui.chat_area.config(state='disabled')

    def add_file_link(self, user, filename):
        self.ui.chat_area.config(state='normal')
        
        is_me = (user == self.username)
        username_tag = "username_self" if is_me else "username_other"

        self.ui.chat_area.insert('end', f"\n{user}", username_tag)
        self.ui.chat_area.insert('end', " shared a file:\n")
        
        btn = tk.Button(self.ui.chat_area, text=f"📄 {filename}", command=lambda f=filename: self.request_download(f), 
                        font=("Segoe UI", 10), bg=COLORS["bg_dark"], fg=COLORS["primary"], 
                        activebackground=COLORS["input_bg"], activeforeground="white",
                        bd=0, cursor="hand2")
        self.ui.chat_area.window_create('end', window=btn)
        self.ui.chat_area.insert('end', "\n")
        
        self.ui.chat_area.yview('end')
        self.ui.chat_area.config(state='disabled')

    def on_close(self):
        self.running = False
        try:
            self.client.close()
        except:
            pass
        self.root.destroy()
        exit()

    # --- Network Loop ---
    def receive(self):
        while self.running:
            try:
                message = self.sock_buffer.read_line()
                if message is None:
                    break
                
                parts = message.split('|')
                cmd = parts[0]

                if cmd == "REGISTER_SUCCESS":
                    messagebox.showinfo("Success", "Registered! You can now login.")
                elif cmd == "REGISTER_FAIL":
                    messagebox.showerror("Error", parts[1])
                elif cmd == "LOGIN_SUCCESS":
                    self.username = parts[1]
                    self.root.after(0, lambda: self.show_frame(self.room_frame))
                elif cmd == "LOGIN_FAIL":
                    messagebox.showerror("Error", parts[1])
                elif cmd == "ROOM_JOINED":
                    self.current_room = parts[1]
                    self.root.after(0, lambda: self.ui.lbl_room_title.config(text=f"# {self.current_room}"))
                    self.root.after(0, lambda: self.show_frame(self.chat_frame))
                elif cmd == "USERLIST":
                    # USERLIST|user1,user2,...
                    if len(parts) > 1:
                        raw_list = parts[1]
                        self.ui.user_list.delete(0, 'end')
                        if raw_list:
                            users = raw_list.split(',')
                            for u in users:
                                self.ui.user_list.insert('end', f"🟢 {u}")

                elif cmd == "USERLIST_ADMIN":
                    # USERLIST_ADMIN|u1#ip1,u2#ip2,...
                    if len(parts) > 1:
                        raw_list = parts[1]
                        self.ui.user_list.delete(0, 'end')
                        if raw_list:
                            entries = raw_list.split(',')
                            for entry in entries:
                                # format: username#ip:port
                                if '#' in entry:
                                    u, ip = entry.split('#')
                                    self.ui.user_list.insert('end', f"👁️ {u}")
                                    self.ui.user_list.insert('end', f"   └ {ip}")
                                else:
                                    self.ui.user_list.insert('end', f"🟢 {entry}")

                elif cmd == "MSG":
                    sender = parts[1]
                    content = parts[2]
                    self.root.after(0, lambda s=sender, c=content: self.add_chat(s, c))
                elif cmd == "SERVER":
                    content = parts[1]
                    self.root.after(0, lambda c=content: self.add_chat("System", c, type="server"))
                elif cmd == "FILE_NOTIF":
                    sender = parts[1]
                    fname = parts[2]
                    self.root.after(0, lambda s=sender, f=fname: self.add_file_link(s, f))
                elif cmd == "FILE_DATA":
                    fname = parts[1]
                    data = parts[2]
                    self.root.after(0, lambda f=fname, d=data: self.save_file(f, d))
                elif cmd == "GAME":
                    sender = parts[1]
                    # Check for WIN/DRAW packets first to display in chat
                    # Structure: GAME|sender|WIN|X|WinnerName
                    if len(parts) >= 5 and parts[2] == "WIN":
                        winner_symbol = parts[3]
                        winner_name = parts[4]
                        self.root.after(0, lambda: self.add_local_msg(f"🏆 Game Over! {winner_name} ({winner_symbol}) won the match!", "system"))
                    elif len(parts) >= 3 and parts[2] == "DRAW":
                        self.root.after(0, lambda: self.add_local_msg(f"🤝 Game Over! It's a Draw!", "system"))

                    # Always forward to game window for board updates
                    content = "|".join(parts[2:])
                    if self.game_window and tk.Toplevel.winfo_exists(self.game_window.top):
                        self.root.after(0, lambda s=sender, c=content: self.game_window.handle_packet(s, c))

            except Exception as e:
                print("Error:", e)
                break
        
        if self.running:
            self.root.after(0, lambda: messagebox.showerror("Connection Lost", "Server closed connection."))
            self.on_close()

if __name__ == "__main__":
    NetHubApp()
