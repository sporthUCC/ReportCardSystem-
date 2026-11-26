import tkinter as tk
from tkinter import ttk

SCHOOL_NAME = "Caribbean High School"
LOGO_PATH = "assets/logo.png"  # change to wherever your logo file is


class LoginScreen(tk.Tk):
    """Login window. Sends the details to AuthService, then opens the
    admin or teacher dashboard depending on the role it gets back."""

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service

        self.title(f"{SCHOOL_NAME} - Login")
        self.geometry("380x500")
        self.resizable(False, False)

        # Logo (stored on self so Tkinter doesn't discard it)
        try:
            self.logo = tk.PhotoImage(file=LOGO_PATH)
            tk.Label(self, image=self.logo).pack(pady=(25, 5))
        except tk.TclError:
            pass  # logo file not found yet

        tk.Label(self, text=SCHOOL_NAME, font=("Segoe UI", 16, "bold")).pack()
        tk.Label(self, text="Report Card Management System").pack(pady=(0, 20))

        tk.Label(self, text="Username").pack(anchor="w", padx=40)
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=(0, 10))

        tk.Label(self, text="Password").pack(anchor="w", padx=40)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=(0, 10))

        self.message = tk.Label(self, text="", fg="red", wraplength=300)
        self.message.pack(pady=5)

        ttk.Button(self, text="Login", command=self.login).pack(pady=5)
        ttk.Button(self, text="Exit", command=self.destroy).pack()

        self.bind("<Return>", lambda event: self.login())
        self.username_entry.focus_set()

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
            self.message.config(text=f"{role} dashboard has not been created yet.")
            return

        self.destroy()
        Dashboard().mainloop()


if __name__ == "__main__":
    from services.auth_service import AuthService  # change to where your AuthService is

    LoginScreen(AuthService()).mainloop()