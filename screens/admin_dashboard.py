
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from config.settings import THEME, LOGO_FILE, MONSTER_HIGH_BACKGROUND
from services.student_service import StudentService
from services.teacher_service import TeacherService
from services.subject_service import SubjectService


class AdminDashboard:

    def __init__(self, root):
        self.root = root

        # bring in our data services so we can grab live counts from the json files
        # note: subject_service needs teacher_service passed in to link instructors
        self.student_service = StudentService()
        self.teacher_service = TeacherService()
        self.subject_service = SubjectService(self.teacher_service)

        # basic window setup
        self.root.title("Monster High Academy | Administrator Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg=THEME["bg_root"])

        # build the screen piece by piece
        self.create_sidebar()
        self.create_main_content()
        self.create_dashboard_heading()
        self.create_summary_cards()
        self.create_directory_shortcuts()

    def create_sidebar(self):
        # left navigation bar container
        self.sidebar = tk.Frame(
            self.root,
            bg=THEME["bg_surface"],
            width=230
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # logo section at the top of the sidebar
        logo_frame = tk.Frame(
            self.sidebar,
            bg=THEME["bg_surface"],
            height=135
        )
        logo_frame.pack(fill="x", pady=(12, 15))
        logo_frame.pack_propagate(False)

        try:
            logo_image = Image.open(LOGO_FILE)

            # resize the logo while keeping its original proportions
            logo_image.thumbnail((165, 105), Image.Resampling.LANCZOS)

            self.logo_photo = ImageTk.PhotoImage(logo_image)

            tk.Label(
                logo_frame,
                image=self.logo_photo,
                bg=THEME["bg_surface"],
                borderwidth=0
            ).pack(expand=True)

        except Exception as err:
            print(f"Could not load school logo: {err}")

        # separator underneath the logo
        tk.Frame(
            self.sidebar,
            bg=THEME["accent_pink"],
            height=1
        ).pack(fill="x", padx=20, pady=(0, 20))

        # navigation options
        self.nav_buttons = {}

        navigation_items = [
            ("Dashboard", "Dashboard"),
            ("Manage Students", "Students"),
            ("Manage Teachers", "Teachers"),
            ("Manage Subjects", "Subjects"),
            ("Manage Grades", "Grades"),
            ("Generate Reports", "Reports")
        ]

        for button_text, page_name in navigation_items:

            button = tk.Button(
                self.sidebar,
                text=button_text,
                command=lambda page=page_name: self.select_navigation(page),
                bg=THEME["accent_pink"] if page_name == "Dashboard" else THEME["bg_surface"],
                fg="#FFFFFF" if page_name == "Dashboard" else THEME["text_purple"],
                activebackground=THEME["accent_pink"],
                activeforeground="#FFFFFF",
                font=("Georgia", 10, "bold"),
                relief="flat",
                anchor="w",
                padx=25,
                pady=12,
                cursor="hand2",
                bd=0
            )

            button.pack(fill="x", padx=12, pady=3)

            self.nav_buttons[page_name] = button

        # logout button at the bottom of the sidebar
        tk.Frame(
            self.sidebar,
            bg=THEME["text_purple"],
            height=1
        ).pack(fill="x", padx=20, pady=(15, 10), side="bottom")

        logout_button = tk.Button(
            self.sidebar,
            text="Logout",
            command=self.root.destroy,
            bg=THEME["bg_surface"],
            fg=THEME["accent_pink"],
            activebackground=THEME["accent_pink"],
            activeforeground="#FFFFFF",
            font=("Georgia", 10, "bold"),
            relief="flat",
            anchor="w",
            padx=25,
            pady=12,
            cursor="hand2",
            bd=0
        )
        logout_button.pack(fill="x", padx=12, pady=(0, 15), side="bottom")

    def select_navigation(self, page_name):
        # highlight the selected navigation option
        for name, button in self.nav_buttons.items():

            if name == page_name:
                button.configure(
                    bg=THEME["accent_pink"],
                    fg="#FFFFFF"
                )
            else:
                button.configure(
                    bg=THEME["bg_surface"],
                    fg=THEME["text_purple"]
                )

    def create_main_content(self):
        # right side workspace where the cards and tables will load
        self.main_content = tk.Frame(
            self.root,
            bg=THEME["bg_root"]
        )
        self.main_content.pack(
            side="left",
            fill="both",
            expand=True  # let this area stretch to fill whatever space is left
        )

        # load and place the Monster High background image behind main_content
        self.bg_label = tk.Label(self.main_content, bg=THEME["bg_root"], borderwidth=0)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            self.raw_bg_image = Image.open(MONSTER_HIGH_BACKGROUND)
            # initial fit for the main workspace (1100 - 230 sidebar = 870x700)
            resized = self.raw_bg_image.resize((870, 700), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.bg_label.configure(image=self.bg_photo)

            # keep the wallpaper scaled if the user resizes the window
            self.main_content.bind("<Configure>", self._resize_main_background)
        except Exception as err:
            print(f"Could not load Monster High background ({MONSTER_HIGH_BACKGROUND}): {err}")

    def _resize_main_background(self, event):
        if event.width > 1 and event.height > 1 and hasattr(self, "raw_bg_image"):
            resized = self.raw_bg_image.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.bg_label.configure(image=self.bg_photo)

    def create_dashboard_heading(self):
        # align the welcome header with the centered cards container
        header_row = tk.Frame(
            self.main_content,
            bg=THEME["bg_root"]
        )
        header_row.pack(
            fill="x",
            padx=145,
            pady=(24, 6)
        )

        # stack title and welcome message cleanly on the left
        title_box = tk.Frame(header_row, bg=THEME["bg_root"])
        title_box.pack(side="left", anchor="w")

        self.heading = tk.Label(
            title_box,
            text="Welcome Back, Admin",
            bg=THEME["bg_root"],
            fg=THEME["text_main"],
            font=("Georgia", 22, "bold"),
            padx=0,
            pady=1
        )
        self.heading.pack(anchor="w")

        tk.Label(
            title_box,
            text="Monster High Academy Overview & Quick Controls",
            bg=THEME["bg_root"],
            fg=THEME["text_purple"],
            font=("Georgia", 10, "italic"),
            padx=0
        ).pack(anchor="w")

    def create_summary_cards(self):
        # centered section holding "+ Quick Add Student" right above our 2x2 stat cards
        self.cards_container = tk.Frame(
            self.main_content,
            bg=THEME["bg_root"]
        )

        # pack before shortcuts_wrapper if it already exists so shortcuts always stay at the bottom
        if hasattr(self, "shortcuts_wrapper") and self.shortcuts_wrapper.winfo_exists():
            self.cards_container.pack(
                fill="x",
                padx=145,
                pady=(4, 8),
                before=self.shortcuts_wrapper
            )
        else:
            self.cards_container.pack(
                fill="x",
                padx=145,
                pady=(4, 8)
            )

        # quick add button bar sitting directly above the centered cards
        action_bar = tk.Frame(self.cards_container, bg=THEME["bg_root"])
        action_bar.pack(fill="x", padx=12, pady=(0, 6))

        self.quick_add_btn = tk.Button(
            action_bar,
            text="+ Quick Add Student",
            command=self.open_quick_add_student,
            bg=THEME["accent_pink"],
            fg="#FFFFFF",
            activebackground=THEME["accent_pink"],
            activeforeground="#FFFFFF",
            font=("Georgia", 11, "bold"),
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2"
        )
        self.quick_add_btn.pack(side="right")

        # inner grid frame so the 2x2 cards stay centered in the middle of the dashboard
        cards_grid = tk.Frame(self.cards_container, bg=THEME["bg_root"])
        cards_grid.pack(fill="x")

        # make both grid columns share width equally
        cards_grid.columnconfigure(0, weight=1, uniform="card_col")
        cards_grid.columnconfigure(1, weight=1, uniform="card_col")

        # get current totals from our backend services
        student_total = len(self.student_service.get_all_students())
        teacher_total = len(self.teacher_service.get_all_teachers())
        subject_total = len(self.subject_service.get_all_subjects())
        reports_total = 0  # still need to wire this up to the pdf export folder later

        # layout setup: (row, col, icon, label, number) -> 2 cards on top, 2 on bottom
        cards = [
            (0, 0, "🎓", "Total Students", student_total),
            (0, 1, "📚", "Total Subjects", subject_total),
            (1, 0, "👩‍🏫", "Total Teachers", teacher_total),
            (1, 1, "📄", "Reports Generated", reports_total)
        ]

        # loop through the list above and build each stat box
        for row, col, icon, title, total in cards:
            card = tk.Frame(
                cards_grid,
                bg=THEME["bg_surface"],
                highlightbackground=THEME["accent_pink"],
                highlightthickness=2,
                padx=16,
                pady=14
            )
            card.grid(
                row=row,
                column=col,
                sticky="nsew",
                padx=12,
                pady=8
            )

            # top row inside the card: title on the left, icon pushed to the right
            top_row = tk.Frame(card, bg=THEME["bg_surface"])
            top_row.pack(fill="x")

            tk.Label(
                top_row,
                text=title,
                bg=THEME["bg_surface"],
                fg=THEME["text_purple"],
                font=("Georgia", 12, "bold")
            ).pack(side="left")

            tk.Label(
                top_row,
                text=icon,
                bg=THEME["bg_surface"],
                fg="#FFFFFF",  # pure white so the icon pops against the dark purple card
                font=("Segoe UI Emoji", 18)
            ).pack(side="right")

            # big count number underneath the title
            tk.Label(
                card,
                text=str(total),
                bg=THEME["bg_surface"],
                fg=THEME["text_main"],
                font=("Georgia", 24, "bold")
            ).pack(anchor="w", pady=(8, 0))

    def create_directory_shortcuts(self):
        # compact bottom panel aligned with the centered cards so it never clips on smaller screens
        self.shortcuts_wrapper = tk.Frame(
            self.main_content,
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=1,
            padx=16,
            pady=10
        )
        self.shortcuts_wrapper.pack(
            fill="x",
            padx=157,
            pady=(4, 16)
        )

        tk.Label(
            self.shortcuts_wrapper,
            text="Directory Shortcuts",
            bg=THEME["bg_surface"],
            fg=THEME["text_main"],
            font=("Georgia", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))

        # 3 equal columns for Manage Students, Manage Teachers, Manage Subjects
        grid_row = tk.Frame(self.shortcuts_wrapper, bg=THEME["bg_surface"])
        grid_row.pack(fill="x")

        for col_idx in range(3):
            grid_row.columnconfigure(col_idx, weight=1, uniform="shortcut_col")

        shortcuts = [
            ("Manage Students", "View, edit & reports"),
            ("Manage Teachers", "Assigned classes"),
            ("Manage Subjects", "Add, edit and remove")
        ]

        for col_idx, (title, subtitle) in enumerate(shortcuts):
            # darker card background inside the surface panel so each shortcut stands out
            box = tk.Frame(
                grid_row,
                bg=THEME["bg_root"],
                highlightbackground=THEME["text_purple"],
                highlightthickness=1,
                padx=12,
                pady=8,
                cursor="hand2"
            )
            box.grid(
                row=0,
                column=col_idx,
                sticky="nsew",
                padx=6
            )

            tk.Label(
                box,
                text=title,
                bg=THEME["bg_root"],
                fg=THEME["accent_pink"],
                font=("Georgia", 10, "bold")
            ).pack(anchor="w")

            tk.Label(
                box,
                text=subtitle,
                bg=THEME["bg_root"],
                fg=THEME["text_purple"],
                font=("Georgia", 8),
                wraplength=140,
                justify="left"
            ).pack(anchor="w", pady=(2, 0))

    def open_quick_add_student(self):
        # dim the background window while the modal is open
        self.root.update_idletasks()
        overlay = tk.Toplevel(self.root)
        overlay.overrideredirect(True)
        overlay.configure(bg="#09050D")
        overlay.attributes("-alpha", 0.65)
        overlay.geometry(
            f"{self.root.winfo_width()}x{self.root.winfo_height()}"
            f"+{self.root.winfo_rootx()}+{self.root.winfo_rooty()}"
        )

        # pop up a centered modal window on top of the dimmed overlay
        popup = tk.Toplevel(overlay)
        popup.title("Quick Add Student")
        popup_w, popup_h = 390, 420
        center_x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (popup_w // 2)
        center_y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (popup_h // 2)
        popup.geometry(f"{popup_w}x{popup_h}+{center_x}+{center_y}")
        popup.configure(bg=THEME["bg_surface"], highlightbackground=THEME["accent_pink"], highlightthickness=2)
        popup.transient(overlay)
        popup.grab_set()  # keeps focus locked on the popup until closed

        def close_modal():
            if popup.winfo_exists():
                popup.destroy()
            if overlay.winfo_exists():
                overlay.destroy()

        popup.protocol("WM_DELETE_WINDOW", close_modal)

        tk.Label(
            popup,
            text="Add New Student",
            bg=THEME["bg_surface"],
            fg=THEME["text_main"],
            font=("Georgia", 16, "bold")
        ).pack(anchor="w", padx=24, pady=(20, 14))

        # style the grade dropdown to match our Monster High dark theme
        combo_style = ttk.Style()
        combo_style.theme_use("clam")
        combo_style.configure(
            "MH.TCombobox",
            fieldbackground=THEME["bg_root"],
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            arrowcolor=THEME["accent_pink"],
            bordercolor=THEME["text_purple"],
            lightcolor=THEME["bg_root"],
            darkcolor=THEME["bg_root"]
        )

        # build the form inputs
        fields = {}
        form_rows = [
            ("First Name", "first_name"),
            ("Last Name", "last_name"),
            ("Email", "email"),
            ("Grade Level", "grade")
        ]

        for label_text, key in form_rows:
            tk.Label(
                popup,
                text=label_text,
                bg=THEME["bg_surface"],
                fg=THEME["text_purple"],
                font=("Georgia", 10, "bold")
            ).pack(anchor="w", padx=24, pady=(6, 2))

            if key == "grade":
                grade_combo = ttk.Combobox(
                    popup,
                    values=["7", "8", "9", "10", "11"],
                    state="readonly",
                    font=("Georgia", 11),
                    style="MH.TCombobox"
                )
                grade_combo.set("7")
                grade_combo.pack(fill="x", padx=24, ipady=4)
                fields[key] = grade_combo

            else:
                entry = tk.Entry(
                    popup,
                    bg=THEME["bg_root"],
                    fg=THEME["text_main"],
                    insertbackground="#FFFFFF",
                    font=("Georgia", 11),
                    relief="flat"
                )
                entry.pack(fill="x", padx=24, ipady=5)
                fields[key] = entry

        def save_student():
            first_name = fields["first_name"].get().strip()
            last_name = fields["last_name"].get().strip()
            email = fields["email"].get().strip()
            grade = fields["grade"].get().strip()

            if not first_name or not last_name or not grade:
                messagebox.showerror(
                    "Missing Information",
                    "Please enter the student's first name, last name and grade level.",
                    parent=popup
                )
                return

            grade_level = int(grade)

            # call your backend service to write the new student to students.json
            result = self.student_service.add_student(
                first_name,
                last_name,
                email or None,
                grade_level
            )

            if result == "Student added successfully.":
                messagebox.showinfo(
                    "Success",
                    result,
                    parent=popup
                )

                # refresh the cards so the Total Students number updates right away
                self.cards_container.destroy()
                self.create_summary_cards()

                close_modal()

            else:
                messagebox.showerror(
                    "Unable to Add Student",
                    result,
                    parent=popup
                )

        tk.Button(
            popup,
            text="Save Student",
            command=save_student,
            bg=THEME["accent_pink"],
            fg="#FFFFFF",
            font=("Georgia", 11, "bold"),
            relief="flat",
            pady=8,
            cursor="hand2"
        ).pack(fill="x", padx=24, pady=(20, 10))


# lets us test this dashboard screen directly without running the login page first
if __name__ == "__main__":
    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()
