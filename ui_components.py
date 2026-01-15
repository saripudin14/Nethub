import tkinter as tk
from tkinter import ttk, scrolledtext
from config import COLORS, FONT_MAIN, FONT_BOLD

class NetHubUI:
    def __init__(self, root):
        self.root = root
        # Widget References (accessed by main app)
        self.entry_user = None
        self.entry_pass = None
        self.combo_letter = None
        self.combo_number = None
        self.chat_area = None
        self.msg_entry = None
        self.lbl_room_title = None

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("TFrame", background=COLORS["bg_dark"])
        style.configure("TLabel", background=COLORS["bg_dark"], foreground=COLORS["text_main"], font=FONT_MAIN)
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="white", background=COLORS["bg_dark"])
        
        style.configure("Primary.TButton", 
                        font=FONT_BOLD, 
                        background=COLORS["primary"], 
                        foreground="white", 
                        borderwidth=0, 
                        relief="flat")
        style.map("Primary.TButton", 
                  background=[('active', COLORS["primary_hover"])])
        
        style.configure("Secondary.TButton", background=COLORS["input_bg"], foreground="white", borderwidth=0)
        style.map("Secondary.TButton", background=[('active', "#404249")]) 

        style.configure("TCombobox", fieldbackground="white", background="white", foreground="black", arrowcolor="black")
        style.map("TCombobox", fieldbackground=[("readonly", "white")], foreground=[("readonly", "black")], 
                 selectbackground=[("readonly", "white")], selectforeground=[("readonly", "black")])

    def create_login_frame(self, parent, on_login, on_register):
        card = tk.Frame(parent, bg=COLORS["bg_lighter"], padx=30, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center", width=340)

        tk.Label(card, text="NetHub", font=("Segoe UI", 22, "bold"), fg="white", bg=COLORS["bg_lighter"]).pack(pady=(0, 5))
        tk.Label(card, text="We're so excited to see you again!", font=("Segoe UI", 10), fg=COLORS["text_muted"], bg=COLORS["bg_lighter"]).pack(pady=(0, 25))
        
        tk.Label(card, text="USERNAME", font=("Segoe UI", 8, "bold"), fg=COLORS["text_muted"], bg=COLORS["bg_lighter"]).pack(anchor="w")
        self.entry_user = tk.Entry(card, bg=COLORS["input_bg"], fg="white", font=FONT_MAIN, insertbackground="white", relief="flat")
        self.entry_user.pack(fill="x", ipady=8, pady=(5, 15))

        tk.Label(card, text="PASSWORD", font=("Segoe UI", 8, "bold"), fg=COLORS["text_muted"], bg=COLORS["bg_lighter"]).pack(anchor="w")
        self.entry_pass = tk.Entry(card, show="*", bg=COLORS["input_bg"], fg="white", font=FONT_MAIN, insertbackground="white", relief="flat")
        self.entry_pass.pack(fill="x", ipady=8, pady=(5, 20))

        tk.Button(card, text="Log In", command=on_login, 
                  bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"], activeforeground="white",
                  font=FONT_BOLD, relief="flat", cursor="hand2").pack(fill="x", ipady=8)
        
        tk.Label(card, text="Need an account?", font=("Segoe UI", 9), fg=COLORS["text_muted"], bg=COLORS["bg_lighter"]).pack(pady=(15,0))
        tk.Button(card, text="Register", command=on_register, 
                  bg=COLORS["bg_lighter"], fg=COLORS["primary"], activebackground=COLORS["bg_lighter"], activeforeground="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", bd=0).pack(pady=2)

    def create_room_frame(self, parent, on_join):
        card = tk.Frame(parent, bg=COLORS["bg_lighter"], padx=40, pady=50)
        card.place(relx=0.5, rely=0.5, anchor="center", width=380)

        tk.Label(card, text="Join a Room", font=("Segoe UI", 24, "bold"), fg="white", bg=COLORS["bg_lighter"]).pack(pady=(0,30))
        
        select_frame = tk.Frame(card, bg=COLORS["bg_lighter"])
        select_frame.pack(fill="x", pady=10)
        
        select_frame.columnconfigure(0, weight=1)
        select_frame.columnconfigure(1, weight=1)

        tk.Label(select_frame, text="SECTION", font=("Segoe UI", 10, "bold"), fg="#b9bbbe", bg=COLORS["bg_lighter"]).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.combo_letter = ttk.Combobox(select_frame, values=[chr(i) for i in range(ord('a'), ord('z')+1)], state="readonly", font=("Segoe UI", 14))
        self.combo_letter.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(5, 0), ipady=5)
        self.combo_letter.current(0)

        tk.Label(select_frame, text="NUMBER", font=("Segoe UI", 10, "bold"), fg="#b9bbbe", bg=COLORS["bg_lighter"]).grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.combo_number = ttk.Combobox(select_frame, values=[str(i) for i in range(1, 11)], state="readonly", font=("Segoe UI", 14))
        self.combo_number.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(5, 0), ipady=5)
        self.combo_number.current(0)
        
        tk.Button(card, text="Join Room", command=on_join, 
                  bg=COLORS["success"], fg="white", activebackground="#1e824c", activeforeground="white",
                  font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2").pack(fill="x", ipady=10, pady=40)

    def create_chat_frame(self, parent, on_speed, on_game, on_upload, on_send, on_emoji):
        header_frame = tk.Frame(parent, bg=COLORS["bg_dark"], height=55, padx=15)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        self.lbl_room_title = tk.Label(header_frame, text="# general", bg=COLORS["bg_dark"], fg="white", font=("Segoe UI", 14, "bold"))
        self.lbl_room_title.pack(side="left")

        btn_frame = tk.Frame(header_frame, bg=COLORS["bg_dark"])
        btn_frame.pack(side="right")

        def create_tool_btn(text, cmd, color="white"):
            return tk.Button(btn_frame, text=text, command=cmd, 
                             bg=COLORS["bg_dark"], fg=color, activebackground=COLORS["bg_lighter"], 
                             activeforeground=color, font=("Segoe UI", 10, "bold"),
                             relief="flat", bd=0, cursor="hand2", padx=10)

        create_tool_btn("📊 Speed", on_speed, COLORS["warning"]).pack(side="left")
        create_tool_btn("🎮 Game", on_game, COLORS["success"]).pack(side="left")
        create_tool_btn("📁 Upload", on_upload, COLORS["primary"]).pack(side="left")

        # Content Area (Chat + Sidebar)
        content_frame = tk.Frame(parent, bg=COLORS["bg_dark"])
        content_frame.pack(fill="both", expand=True)

        # Chat Text
        self.chat_area = scrolledtext.ScrolledText(content_frame, state='disabled', 
                                                   bg=COLORS["bg_lighter"], fg=COLORS["text_main"],
                                                   font=("Segoe UI", 11), borderwidth=0, padx=15, pady=15)
        self.chat_area.pack(side="left", fill="both", expand=True)

        # Sidebar (User List)
        sidebar = tk.Frame(content_frame, bg="#2f3136", width=200) # Slightly darker than chat
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False) # Force width

        tk.Label(sidebar, text="ONLINE USERS", font=("Segoe UI", 8, "bold"), fg=COLORS["text_muted"], bg="#2f3136").pack(pady=(15, 10), padx=10, anchor="w")
        
        self.user_list = tk.Listbox(sidebar, bg="#2f3136", fg=COLORS["text_main"], font=("Segoe UI", 10),
                                    bd=0, highlightthickness=0, selectbackground="#2f3136")
        self.user_list.pack(fill="both", expand=True, padx=10)

        self.chat_area.tag_config("timestamp", foreground=COLORS["text_muted"], font=("Consolas", 8))
        self.chat_area.tag_config("username_self", foreground=COLORS["primary"], font=FONT_BOLD)
        self.chat_area.tag_config("username_other", foreground="white", font=FONT_BOLD)
        self.chat_area.tag_config("bubble", lmargin1=10, lmargin2=10, rmargin=10)
        self.chat_area.tag_config("system", foreground=COLORS["warning"], justify="center", spacing1=10, spacing3=10)

        # Input Area
        input_container = tk.Frame(parent, bg=COLORS["bg_dark"], pady=15, padx=15)
        input_container.pack(fill="x")
        
        # Emoji Button
        tk.Button(input_container, text="😀", command=on_emoji,
                  bg=COLORS["bg_dark"], fg="white", activebackground=COLORS["bg_lighter"],
                  font=("Segoe UI", 12), relief="flat", bd=0, cursor="hand2").pack(side="left", padx=(0, 5))

        self.msg_entry = tk.Entry(input_container, bg=COLORS["input_bg"], fg="white", 
                                  font=("Segoe UI", 11), relief="flat", insertbackground="white")
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
        self.msg_entry.bind('<Return>', lambda e: on_send())

        tk.Button(input_container, text="➤", command=on_send, 
                  bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"], 
                  font=("Arial", 12, "bold"), relief="flat", bd=0, cursor="hand2").pack(side="right", ipady=3, ipadx=10)
