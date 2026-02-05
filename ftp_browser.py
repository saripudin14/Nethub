"""
FTP Browser Window for NetHub Client
Provides a GUI for browsing, uploading, and downloading files via FTP.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from ftplib import FTP
import os
import base64
import io

class FTPBrowserWindow:
    """FTP Browser GUI Window"""
    
    def __init__(self, root, username, password, host='127.0.0.1', port=2121, send_packet_func=None):
        self.root = root
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.ftp = None
        self.current_path = '/'
        self.send_packet = send_packet_func  # Function to send to chat
        
        # Colors (matching NetHub theme)
        self.colors = {
            "bg_dark": "#36393f",
            "bg_lighter": "#40444b",
            "primary": "#5865F2",
            "text_main": "#dcddde",
            "text_muted": "#72767d",
            "success": "#43b581",
            "danger": "#f04747"
        }
        
        # Create window
        self.top = tk.Toplevel(root)
        self.top.title("NetHub Storage")
        self.top.geometry("700x500")
        self.top.configure(bg=self.colors["bg_dark"])
        
        self._create_ui()
        self._connect()
    
    def _create_ui(self):
        """Create the FTP browser UI"""
        # Header
        header = tk.Frame(self.top, bg=self.colors["bg_dark"], pady=10, padx=15)
        header.pack(fill="x")
        
        tk.Label(header, text="💾 Storage Browser", 
                 font=("Segoe UI", 16, "bold"), 
                 fg="white", bg=self.colors["bg_dark"]).pack(side="left")
        
        self.status_label = tk.Label(header, text="Connecting...", 
                                     font=("Segoe UI", 10),
                                     fg=self.colors["text_muted"], 
                                     bg=self.colors["bg_dark"])
        self.status_label.pack(side="right")
        
        # Internal path tracking (hidden from UI)
        self.path_entry = None
        
        # File list
        list_frame = tk.Frame(self.top, bg=self.colors["bg_dark"], padx=15, pady=10)
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for file listing
        columns = ("name", "type", "size")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        
        self.tree.column("name", width=400)
        self.tree.column("type", width=100)
        self.tree.column("size", width=100)
        
        # Style treeview
        style = ttk.Style()
        style.configure("Treeview", 
                        background=self.colors["bg_lighter"],
                        foreground=self.colors["text_main"],
                        fieldbackground=self.colors["bg_lighter"],
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background=self.colors["bg_dark"],
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Double-click to navigate/download
        self.tree.bind("<Double-1>", self._on_double_click)
        
        # Action buttons
        btn_frame = tk.Frame(self.top, bg=self.colors["bg_dark"], pady=15, padx=15)
        btn_frame.pack(fill="x")
        
        tk.Button(btn_frame, text="📥 Download", 
                  command=self._download,
                  bg=self.colors["success"], fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=15).pack(side="left", padx=(0, 10))
        
        tk.Button(btn_frame, text="📤 Upload", 
                  command=self._upload,
                  bg=self.colors["primary"], fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2", padx=15).pack(side="left", padx=(0, 10))
        
        # Share to Chat button (only if send_packet is available)
        if self.send_packet:
            tk.Button(btn_frame, text="💬 Share to Chat", 
                      command=self._share_to_chat,
                      bg="#00d4ff", fg="white",
                      font=("Segoe UI", 10, "bold"),
                      relief="flat", cursor="hand2", padx=15).pack(side="left", padx=(0, 10))
        
        tk.Button(btn_frame, text="🔄 Refresh", 
                  command=self._refresh,
                  bg=self.colors["bg_lighter"], fg="white",
                  font=("Segoe UI", 10),
                  relief="flat", cursor="hand2", padx=15).pack(side="left", padx=(0, 10))
        
        tk.Button(btn_frame, text="🗑️ Delete", 
                  command=self._delete,
                  bg=self.colors["danger"], fg="white",
                  font=("Segoe UI", 10),
                  relief="flat", cursor="hand2", padx=15).pack(side="right")
    
    def _connect(self):
        """Connect to FTP server"""
        def do_connect():
            try:
                self.ftp = FTP()
                self.ftp.connect(self.host, self.port)
                self.ftp.login(self.username, self.password)
                self.top.after(0, lambda: self.status_label.config(
                    text=f"✅ Connected as {self.username}", 
                    fg=self.colors["success"]))
                self.top.after(0, self._refresh)
            except Exception as e:
                self.top.after(0, lambda: self.status_label.config(
                    text=f"❌ Connection failed", 
                    fg=self.colors["danger"]))
                self.top.after(0, lambda: messagebox.showerror("FTP Error", str(e)))
        
        threading.Thread(target=do_connect, daemon=True).start()
    
    def _refresh(self):
        """Refresh file listing"""
        if not self.ftp:
            return
        
        def do_refresh():
            try:
                self.ftp.cwd(self.current_path)
                files = []
                
                # Get file list with details
                def parse_line(line):
                    parts = line.split()
                    if len(parts) >= 9:
                        is_dir = line.startswith('d')
                        name = " ".join(parts[8:])
                        size = parts[4] if not is_dir else "-"
                        files.append((name, "📁 Folder" if is_dir else "📄 File", size, is_dir))
                
                self.ftp.retrlines('LIST', parse_line)
                
                # Update tree on main thread
                def update_tree():
                    self.tree.delete(*self.tree.get_children())
                    # Sort: folders first, then files
                    files.sort(key=lambda x: (not x[3], x[0].lower()))
                    for name, ftype, size, _ in files:
                        self.tree.insert("", "end", values=(name, ftype, size))
                
                self.top.after(0, update_tree)
            except Exception as e:
                self.top.after(0, lambda: messagebox.showerror("FTP Error", str(e)))
        
        threading.Thread(target=do_refresh, daemon=True).start()
    
    def _navigate(self, path):
        """Navigate to a path"""
        self.current_path = path
        self._refresh()
    
    def _go_up(self):
        """Go to parent directory"""
        if self.current_path != '/':
            parent = '/'.join(self.current_path.rstrip('/').split('/')[:-1])
            self.current_path = parent if parent else '/'
            self._refresh()
    
    def _on_double_click(self, event):
        """Handle double-click on item"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        name = item["values"][0]
        is_folder = "Folder" in item["values"][1]
        
        if is_folder:
            # Navigate into folder
            if self.current_path == '/':
                self.current_path = f"/{name}"
            else:
                self.current_path = f"{self.current_path}/{name}"
            self._refresh()
        else:
            # Download file
            self._download()
    
    def _download(self):
        """Download selected file"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("FTP", "Please select a file to download.")
            return
        
        item = self.tree.item(selection[0])
        name = item["values"][0]
        is_folder = "Folder" in item["values"][1]
        
        if is_folder:
            messagebox.showwarning("FTP", "Cannot download folders. Navigate into it instead.")
            return
        
        save_path = filedialog.asksaveasfilename(initialfile=name)
        if not save_path:
            return
        
        def do_download():
            try:
                with open(save_path, 'wb') as f:
                    remote_path = f"{self.current_path}/{name}".replace("//", "/")
                    self.ftp.retrbinary(f'RETR {remote_path}', f.write)
                self.top.after(0, lambda: messagebox.showinfo("FTP", f"Downloaded: {name}"))
            except Exception as e:
                self.top.after(0, lambda: messagebox.showerror("FTP Error", str(e)))
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def _upload(self):
        """Upload a file"""
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        
        filename = os.path.basename(file_path)
        
        def do_upload():
            try:
                with open(file_path, 'rb') as f:
                    self.ftp.cwd(self.current_path)
                    self.ftp.storbinary(f'STOR {filename}', f)
                self.top.after(0, lambda: messagebox.showinfo("FTP", f"Uploaded: {filename}"))
                self.top.after(0, self._refresh)
            except Exception as e:
                self.top.after(0, lambda: messagebox.showerror("FTP Error", str(e)))
        
        threading.Thread(target=do_upload, daemon=True).start()
    
    def _delete(self):
        """Delete selected file"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("FTP", "Please select a file to delete.")
            return
        
        item = self.tree.item(selection[0])
        name = item["values"][0]
        is_folder = "Folder" in item["values"][1]
        
        if not messagebox.askyesno("Confirm Delete", f"Delete '{name}'?"):
            return
        
        def do_delete():
            try:
                remote_path = f"{self.current_path}/{name}".replace("//", "/")
                if is_folder:
                    self.ftp.rmd(remote_path)
                else:
                    self.ftp.delete(remote_path)
                self.top.after(0, lambda: messagebox.showinfo("FTP", f"Deleted: {name}"))
                self.top.after(0, self._refresh)
            except Exception as e:
                self.top.after(0, lambda: messagebox.showerror("FTP Error", str(e)))
        
        threading.Thread(target=do_delete, daemon=True).start()
    
    def _share_to_chat(self):
        """Share selected file to chat room"""
        if not self.send_packet:
            messagebox.showwarning("FTP", "Share to Chat is not available.")
            return
        
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("FTP", "Please select a file to share.")
            return
        
        item = self.tree.item(selection[0])
        name = item["values"][0]
        is_folder = "Folder" in item["values"][1]
        
        if is_folder:
            messagebox.showwarning("FTP", "Cannot share folders. Select a file instead.")
            return
        
        def do_share():
            try:
                # Download file to memory
                buffer = io.BytesIO()
                remote_path = f"{self.current_path}/{name}".replace("//", "/")
                self.ftp.retrbinary(f'RETR {remote_path}', buffer.write)
                
                # Encode to base64 for chat upload
                file_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Send to chat via the chat protocol
                self.top.after(0, lambda: self.send_packet(f"UPLOAD|{name}|{file_data}"))
                self.top.after(0, lambda: messagebox.showinfo("FTP", f"Shared to chat: {name}"))
            except Exception as e:
                self.top.after(0, lambda: messagebox.showerror("FTP Error", str(e)))
        
        threading.Thread(target=do_share, daemon=True).start()
    
    def close(self):
        """Close FTP connection"""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
        self.top.destroy()
