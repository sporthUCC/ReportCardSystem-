import tkinter as tk
from pathlib import Path

SCHOOL_NAME = "Monster High School"
# assets/school_logo.png, found relative to this file so it works from any folder
LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "school_logo.png"

THEME = {
    "bg_root": "#120B18",
    "bg_surface": "#1D1226",
    "accent_pink": "#FF1E8A",
    "text_main": "#F8F2FC",
}

PURPLE = "#3B1552"  # colour of the left-hand panel
LEFT_W, HEIGHT = 340, 480


def make_logo(parent, bg):
    """Uses your logo file if it exists, otherwise draws a skull-and-bow badge."""
    try:
        try:
            # Pillow (pip install pillow) shrinks big logos smoothly
            from PIL import Image, ImageTk
            img = Image.open(LOGO_PATH).convert("RGBA")
            img = img.crop(img.getchannel("A").getbbox() or (0, 0, *img.size))
            img.thumbnail((300, 230))
            parent.logo = ImageTk.PhotoImage(img)  # kept on parent so Tkinter keeps it
        except ImportError:
            # Without Pillow: load the PNG and shrink it by a whole-number factor
            full = tk.PhotoImage(file=str(LOGO_PATH))
            parent.logo = full.subsample(max(1, full.width() // 300))
        return tk.Label(parent, image=parent.logo, bg=bg)
    except (tk.TclError, FileNotFoundError, OSError):
        pass  # no logo file found, so draw the skull badge below

    pink, dark, bone = THEME["accent_pink"], THEME["bg_root"], THEME["text_main"]
    c = tk.Canvas(parent, width=110, height=110, bg=bg, highlightthickness=0)
    c.create_oval(3, 3, 107, 107, outline=pink, width=3, fill=dark)
    c.create_oval(25, 18, 85, 70, fill=bone, outline="")
    c.create_polygon(38, 60, 72, 60, 70, 80, 62, 87, 48, 87, 40, 80, fill=bone, outline="")
    c.create_oval(33, 40, 52, 62, fill=dark, outline="")
    c.create_oval(58, 40, 77, 62, fill=dark, outline="")
    c.create_oval(39, 45, 45, 51, fill=pink, outline="")
    c.create_oval(64, 45, 70, 51, fill=pink, outline="")
    c.create_polygon(50, 65, 60, 65, 55, 73, fill=dark, outline="")
    for x in (47, 55, 63):
        c.create_line(x, 78, x, 87, fill=dark, width=2)
    c.create_polygon(66, 24, 51, 15, 51, 33, fill=pink, outline="")
    c.create_polygon(66, 24, 81, 15, 81, 33, fill=pink, outline="")
    c.create_oval(61, 19, 71, 29, fill="#C2005E", outline="")
    return c


class LoginScreen(tk.Tk):
    """Split-screen login. Sends the details to AuthService, then opens the
    admin or teacher dashboard depending on the role it gets back."""

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service

        self.title(f"{SCHOOL_NAME} - Login")
        self.geometry(f"{LEFT_W + 420}x{HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=THEME["bg_surface"])

        self.build_left_panel()
        self.build_right_panel()

        self.bind("<Return>", lambda event: self.login())
        self.username_entry.focus_set()

    # ---------- Left side: spooky banner ----------
    def build_left_panel(self):
        c = tk.Canvas(self, width=LEFT_W, height=HEIGHT, bg=PURPLE, highlightthickness=0)
        c.pack(side="left", fill="y")

        # Pink slime dripping from the top
        pink = THEME["accent_pink"]
        c.create_rectangle(0, 0, LEFT_W, 14, fill=pink, outline="")
        for x, length in [(30, 34), (85, 20), (150, 44), (215, 24), (270, 38), (320, 18)]:
            c.create_rectangle(x - 6, 14, x + 6, 14 + length, fill=pink, outline="")
            c.create_oval(x - 6, 8 + length, x + 6, 20 + length, fill=pink, outline="")

        # Bats
        for x, y, size in [(45, 395, 12), (295, 380, 14), (170, 425, 8)]:
            self.draw_bat(c, x, y, size)

        # Logo (it already contains the school name) and subtitle
        c.create_window(LEFT_W // 2, 195, window=make_logo(c, PURPLE))
        c.create_text(LEFT_W // 2, 340, text="Report Card\nManagement System",
                      fill="#CDB8E0", font=("Segoe UI", 12), justify="center")

        # Eyes peeking from the bottom
        for eye_x in (110, 230):
            c.create_oval(eye_x - 10, HEIGHT - 40, eye_x + 10, HEIGHT - 22,
                          fill="#B6FF3B", outline="")
            c.create_oval(eye_x - 2, HEIGHT - 40, eye_x + 2, HEIGHT - 22,
                          fill="black", outline="")

    def draw_bat(self, canvas, x, y, size):
        shape = [(0, -0.3), (0.5, -0.9), (0.7, -0.5), (1.5, -0.8), (2.2, -0.1),
                 (1.7, 0.4), (1.2, 0.1), (0.7, 0.7), (0, 0.3),
                 (-0.7, 0.7), (-1.2, 0.1), (-1.7, 0.4), (-2.2, -0.1),
                 (-1.5, -0.8), (-0.7, -0.5), (-0.5, -0.9)]
        points = []
        for px, py in shape:
            points += [x + px * size, y + py * size]
        canvas.create_polygon(points, fill="#0B0610", outline="")

    # ---------- Right side: the form ----------
    def build_right_panel(self):
        panel = tk.Frame(self, bg=THEME["bg_surface"])
        panel.pack(side="left", fill="both", expand=True)

        form = tk.Frame(panel, bg=THEME["bg_surface"])
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form, text="Welcome back", font=("Segoe UI", 22, "bold"),
                 bg=THEME["bg_surface"], fg=THEME["text_main"]).pack(anchor="w")
        tk.Label(form, text="Log in to continue", bg=THEME["bg_surface"],
                 fg="#CDB8E0").pack(anchor="w", pady=(0, 22))

        self.username_entry = self.make_field(form, "Username", show="")
        self.password_entry = self.make_field(form, "Password", show="*")

        self.message = tk.Label(form, text="", bg=THEME["bg_surface"],
                                fg=THEME["accent_pink"], wraplength=300,
                                justify="left", height=2)
        self.message.pack(anchor="w")

        tk.Button(form, text="LOGIN", command=self.login, width=30,
                  bg=THEME["accent_pink"], fg=THEME["text_main"],
                  activebackground=THEME["text_main"], activeforeground=THEME["bg_root"],
                  font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=(4, 0), ipady=6)

    def make_field(self, parent, label, show):
        """A label, a text box and a pink line under it."""
        tk.Label(parent, text=label, bg=THEME["bg_surface"], fg=THEME["text_main"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        entry = tk.Entry(parent, width=34, font=("Segoe UI", 12), show=show,
                         bg=THEME["bg_root"], fg=THEME["text_main"],
                         insertbackground=THEME["text_main"], relief="flat")
        entry.pack(pady=(3, 0), ipady=6)
        tk.Frame(parent, bg=THEME["accent_pink"], height=2).pack(fill="x", pady=(0, 14))
        return entry

    # ---------- Login ----------
    def login(self):
        role, message = self.auth_service.login(
            self.username_entry.get(), self.password_entry.get()
        )

        if role is None:
            self.message.config(text=message)
            self.password_entry.delete(0, tk.END)
            return

        # Pick the dashboard that matches the role
        try:
            if role == "Administrator":
                from screens.admin_dashboard import AdminDashboard as Dashboard
            else:
                from screens.teacher_dashboard import TeacherDashboard as Dashboard
        except ImportError:
            self.message.config(text=f"Could not open the {role} dashboard.")
            return

        self.destroy()
        Dashboard().mainloop()


if __name__ == "__main__":
    from services.auth_service import AuthService  # change to where your AuthService is

    LoginScreen(AuthService()).mainloop()