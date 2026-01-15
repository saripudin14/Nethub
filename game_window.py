import tkinter as tk
from tkinter import messagebox
from config import COLORS, FONT_HEADER, FONT_MAIN

class TicTacToeWindow:
    def __init__(self, root, send_func, username):
        self.top = tk.Toplevel(root)
        self.top.title("Tic Tac Toe")
        self.top.geometry("320x450")
        self.top.resizable(False, False)
        self.top.configure(bg=COLORS["bg_dark"])
        
        self.send_func = send_func
        self.username = username
        self.turn = 'X'
        self.board = [""] * 9
        self.buttons = []
        
        # Player Roles
        self.player_x = None
        self.player_o = None
        
        # Header
        header = tk.Frame(self.top, bg=COLORS["bg_dark"], pady=15)
        header.pack(fill="x")
        tk.Label(header, text="Tic Tac Toe", font=FONT_HEADER, bg=COLORS["bg_dark"], fg=COLORS["text_main"]).pack()
        
        self.lbl_status = tk.Label(header, text=f"Waiting for players...", font=("Segoe UI", 10), bg=COLORS["bg_dark"], fg=COLORS["primary"])
        self.lbl_status.pack(pady=5)
        
        # Game Grid
        frame_outer = tk.Frame(self.top, bg="#2f3136", padx=5, pady=5)
        frame_outer.pack(pady=10)
        
        frame_grid = tk.Frame(frame_outer, bg=COLORS["bg_dark"]) 
        frame_grid.pack()
        
        for i in range(9):
            btn = tk.Button(frame_grid, text="", font=("Segoe UI", 24, "bold"), width=3, height=1,
                            bg=COLORS["bg_lighter"], fg=COLORS["text_main"], 
                            activebackground=COLORS["bg_lighter"], activeforeground=COLORS["text_main"],
                            relief="flat", borderwidth=0, cursor="hand2",
                            command=lambda idx=i: self.on_click(idx))
            
            # Simple grid border effect using padding
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)
            self.buttons.append(btn)
            
        # Footer
        footer = tk.Frame(self.top, bg=COLORS["bg_dark"], pady=15)
        footer.pack(fill="x", side="bottom")
        
        self.btn_reset = tk.Button(footer, text="Restart Game", command=self.reset_game, 
                                   bg=COLORS["danger"], fg="white", font=("Segoe UI", 10, "bold"),
                                   relief="flat", padx=15, pady=5, cursor="hand2")
        self.btn_reset.pack()

    def on_click(self, index):
        # Access Control
        if self.turn == 'X':
            if self.player_x and self.player_x != self.username:
                messagebox.showwarning("Spectator", f"You are watching. Player X is {self.player_x}")
                return
        elif self.turn == 'O':
            if self.player_o and self.player_o != self.username:
                messagebox.showwarning("Spectator", f"You are watching. Player O is {self.player_o}")
                return

        if self.board[index] == "":
            self.send_func(f"GAME|MOVE|{index}|{self.turn}")

    def reset_game(self):
        self.send_func("GAME|RESET")

    def update_status(self):
        px = self.player_x if self.player_x else "?"
        po = self.player_o if self.player_o else "?"
        
        msg = f"Turn: {self.turn} "
        if self.turn == 'X' and self.player_x: msg += f"({self.player_x})"
        elif self.turn == 'O' and self.player_o: msg += f"({self.player_o})"
        
        self.lbl_status.config(text=f"{msg}\nX: {px} vs O: {po}")

    def handle_packet(self, sender, content):
        try:
            if not self.top.winfo_exists(): return
        except: return

        parts = content.split('|')
        action = parts[0]
        
        try:
            if action == "MOVE":
                idx = int(parts[1])
                symbol = parts[2]
                
                # Assign Roles if empty
                if symbol == 'X' and self.player_x is None:
                    self.player_x = sender
                if symbol == 'O' and self.player_o is None:
                    self.player_o = sender
                
                # Validate Consistency
                if symbol == 'X' and self.player_x != sender: return # Ignore invalid X
                if symbol == 'O' and self.player_o != sender: return # Ignore invalid O

                self.board[idx] = symbol
                
                color = COLORS["success"] if symbol == 'X' else COLORS["warning"]
                self.buttons[idx].config(text=symbol, fg=color, bg=COLORS["bg_lighter"])
                
                # Check Win
                if self.check_win(symbol):
                    if sender == self.username:
                        self.send_func(f"GAME|WIN|{symbol}|{sender}")
                    messagebox.showinfo("Game Over", f"Player {symbol} Wins!")
                    self._clear_board()
                elif "" not in self.board:
                    if sender == self.username:
                        self.send_func(f"GAME|DRAW|draw")
                    messagebox.showinfo("Game Over", "It's a Draw!")
                    self._clear_board()
                else:
                    self.turn = 'O' if symbol == 'X' else 'X'
                    self.update_status()
                    
            elif action == "RESET":
                self._clear_board()
        except tk.TclError:
            pass # Window likely closed during update

    def check_win(self, p):
        # Rows, Cols, Diags
        b = self.board
        return ((b[0]==p and b[1]==p and b[2]==p) or
                (b[3]==p and b[4]==p and b[5]==p) or
                (b[6]==p and b[7]==p and b[8]==p) or
                (b[0]==p and b[3]==p and b[6]==p) or
                (b[1]==p and b[4]==p and b[7]==p) or
                (b[2]==p and b[5]==p and b[8]==p) or
                (b[0]==p and b[4]==p and b[8]==p) or
                (b[2]==p and b[4]==p and b[6]==p))

    def _clear_board(self):
        try:
            if not self.top.winfo_exists(): return
            self.board = [""] * 9
            self.turn = 'X'
            self.player_x = None
            self.player_o = None
            self.lbl_status.config(text=f"Waiting for players...")
            for btn in self.buttons:
                btn.config(text="", bg=COLORS["bg_lighter"])
        except tk.TclError:
            pass
