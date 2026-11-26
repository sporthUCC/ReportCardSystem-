import math
import random
import tkinter as tk

SCHOOL_NAME = "Monster High School"
LOGO_PATH = "assets/logo.png"  # change to wherever your logo file is

THEME = {
    "bg_root": "#120B18",
    "bg_surface": "#1D1226",
    "accent_pink": "#FF1E8A",
    "text_main": "#F8F2FC",
}

WIDTH, HEIGHT = 420, 680
SKY_TOP = "#3B1552"  # spooky purple at the top, fading into bg_root


def blend(color1, color2, t):
    """Mix two hex colours. t=0 gives color1, t=1 gives color2."""
    a = [int(color1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(color2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class LoginScreen(tk.Tk):
    """Login window. Sends the details to AuthService, then opens the
    admin or teacher dashboard depending on the role it gets back."""

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service

        self.title(f"{SCHOOL_NAME} - Login")
        self.resizable(False, False)

        # Everything is drawn on a canvas so the background can be spooky
        self.canvas = tk.Canvas(self, width=WIDTH, height=HEIGHT, highlightthickness=0)
        self.canvas.pack()
        self.draw_background()

        # Card in the middle of the window
        card = tk.Frame(self.canvas, bg=THEME["bg_surface"], padx=35, pady=25,
                        highlightbackground=THEME["accent_pink"], highlightthickness=1)
        self.canvas.create_window(WIDTH // 2, HEIGHT // 2 + 25, window=card)

        # Logo sits inside the card, just above the school name
        self.make_logo(card).pack(pady=(0, 8))

        tk.Label(card, text=SCHOOL_NAME, font=("Segoe UI", 16, "bold"),
                 bg=THEME["bg_surface"], fg=THEME["accent_pink"]).pack()
        tk.Label(card, text="Report Card Management System",
                 bg=THEME["bg_surface"], fg=THEME["text_main"]).pack(pady=(0, 20))

        tk.Label(card, text="Username", bg=THEME["bg_surface"],
                 fg=THEME["text_main"]).pack(anchor="w")
        self.username_entry = tk.Entry(card, width=30, font=("Segoe UI", 11),
                                       bg=THEME["bg_root"], fg=THEME["text_main"],
                                       insertbackground=THEME["text_main"], relief="flat")
        self.username_entry.pack(pady=(2, 12), ipady=5)

        tk.Label(card, text="Password", bg=THEME["bg_surface"],
                 fg=THEME["text_main"]).pack(anchor="w")
        self.password_entry = tk.Entry(card, width=30, font=("Segoe UI", 11), show="*",
                                       bg=THEME["bg_root"], fg=THEME["text_main"],
                                       insertbackground=THEME["text_main"], relief="flat")
        self.password_entry.pack(pady=(2, 12), ipady=5)

        self.message = tk.Label(card, text="", bg=THEME["bg_surface"],
                                fg=THEME["accent_pink"], wraplength=280, height=2)
        self.message.pack()

        tk.Button(card, text="Login", command=self.login, width=26,
                  bg=THEME["accent_pink"], fg=THEME["text_main"],
                  activebackground=THEME["text_main"], activeforeground=THEME["bg_root"],
                  font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=(5, 8), ipady=4)
        tk.Button(card, text="Exit", command=self.destroy, width=26,
                  bg=THEME["bg_root"], fg=THEME["text_main"],
                  activebackground=THEME["accent_pink"], activeforeground=THEME["text_main"],
                  font=("Segoe UI", 10), relief="flat").pack(ipady=4)

        self.bind("<Return>", lambda event: self.login())
        self.username_entry.focus_set()

    def make_logo(self, parent):
        """Uses your logo file if it exists, otherwise draws a little monster logo."""
        try:
            self.logo = tk.PhotoImage(file=LOGO_PATH)  # stored on self so Tkinter keeps it
            return tk.Label(parent, image=self.logo, bg=THEME["bg_surface"])
        except tk.TclError:
            pass

        pink, dark, bone = THEME["accent_pink"], THEME["bg_root"], THEME["text_main"]
        c = tk.Canvas(parent, width=110, height=110, bg=THEME["bg_surface"], highlightthickness=0)

        # Badge ring
        c.create_oval(3, 3, 107, 107, outline=pink, width=3, fill=dark)
        c.create_oval(9, 9, 101, 101, outline="#5A1B6B", width=1)

        # Skull: cranium and jaw
        c.create_oval(25, 18, 85, 70, fill=bone, outline="")
        c.create_polygon(38, 60, 72, 60, 70, 80, 62, 87, 48, 87, 40, 80, fill=bone, outline="")
        