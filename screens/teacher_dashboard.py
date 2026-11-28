"""
Teacher Dashboard for Monster High Academy's Report Card Management System.
Allows the teacher to view student records, see each student's grades by subject,
and enter or update coursework, project, midterm, and final exam grades.

All student, subject, and grade information comes from the existing services.
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from PIL import Image, ImageTk

# Import the school theme and logo
try:
    from config.settings import THEME as _CONFIG_THEME, LOGO_FILE
except ImportError:
    _CONFIG_THEME = {}
    LOGO_FILE = None


MH_THEME = {
    "bg_black": _CONFIG_THEME.get("bg_root", "#0D0B12"),
    "bg_sidebar": "#14101D",
    "bg_card": _CONFIG_THEME.get("bg_surface", "#1B1528"),
    "bg_input": "#241C35",
    "accent_pink": _CONFIG_THEME.get("accent_pink", "#FF2A85"),
    "accent_pink_hover": "#FF569E",
    "accent_purple": _CONFIG_THEME.get("text_purple", "#A855F7"),
    "border_purple": "#4C2A75",
    "text_white": _CONFIG_THEME.get("text_main", "#FFFFFF"),
    "text_muted": "#D4C7E8",
}


class RoundedCard(tk.Canvas):
    """Creates a rounded card with a frame inside it."""

    def __init__(
        self,
        parent,
        bg_color=MH_THEME["bg_card"],
        border_color=MH_THEME["border_purple"],
        radius=18,
        border_width=2,
        padding=18,
        **kwargs,
    ):
        parent_bg = kwargs.pop("bg", parent.cget("bg"))

        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )

        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.border_width = border_width
        self.padding = padding

        self.inner = tk.Frame(self, bg=self.bg_color)

        self._window_id = self.create_window(
            self.padding,
            self.padding,
            window=self.inner,
            anchor="nw",
        )

        self.bind("<Configure>", self._on_resize)

    def _round_rect_points(self, x1, y1, x2, y2, r):
        r = max(2, min(r, (x2 - x1) // 2, (y2 - y1) // 2))

        return [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]

    def _on_resize(self, event):
        width = max(event.width, 40)
        height = max(event.height, 40)

        self.delete("card_shape")

        inset = self.border_width / 2

        points = self._round_rect_points(
            inset,
            inset,
            width - inset,
            height - inset,
            self.radius,
        )

        self.create_polygon(
            points,
            smooth=True,
            fill=self.bg_color,
            outline=self.border_color,
            width=self.border_width,
            tags="card_shape",
        )

        self.tag_lower("card_shape")

        inner_width = max(width - (self.padding * 2), 20)
        inner_height = max(height - (self.padding * 2), 20)

        self.itemconfigure(
            self._window_id,
            width=inner_width,
            height=inner_height,
        )


def draw_corner_web(canvas, x0, y0, size=64, flip_x=False):
    """Draws a small spiderweb decoration."""

    sx = -1 if flip_x else 1
    cx = x0 + (size if flip_x else 0)
    cy = y0
    color = "#3B2459"

    radii = [size * 0.35, size * 0.65, size * 0.95]
    angles = [0, 22, 45, 67, 90]

    for degree in angles:
        rad = degree * math.pi / 180

        end_x = cx + sx * size * 0.95 * math.cos(rad)
        end_y = cy + size * 0.95 * math.sin(rad)

        canvas.create_line(
            cx, cy, end_x, end_y,
            fill=color,
            width=1,
        )

    for radius in radii:
        points = []

        for degree in angles:
            rad = degree * math.pi / 180

            point_x = cx + sx * radius * math.cos(rad)
            point_y = cy + radius * math.sin(rad)

            points.extend([point_x, point_y])

        canvas.create_line(
            points,
            fill=color,
            width=1,
        )


class TeacherDashboard:
    """
    Main Teacher Dashboard.

    Student, subject, and grade information is retrieved through
    the existing services instead of using demo records.

    If teacher_id is given, only the subjects taught by that teacher (and the
    grades recorded for those subjects) are shown. If it is left as None,
    every subject and grade is shown.
    """

    def __init__(
        self,
        parent,
        student_service,
        subject_service,
        grade_service,
        teacher_name="",
        on_logout=None,
        on_open_grades=None,
        teacher_id=None,
        auth_service=None,
    ):

        self.parent = parent
        self.student_service = student_service
        self.subject_service = subject_service
        self.grade_service = grade_service
        self.auth_service = auth_service

        self.teacher_name = teacher_name
        self.teacher_id = teacher_id
        self.on_logout = on_logout
        self.on_open_grades = on_open_grades

        # These lists and lookups are filled using the services
        self.students = []
        self.subjects = []
        self.grades_records = []
        self.student_lookup = {}
        self.subject_lookup = {}
        self.grade_lookup = {}

        self.nav_buttons = {}
        self.active_tab = "dashboard"

        self._load_dashboard_data()
        self._configure_styles()
        self._build_layout()

        self.show_section("dashboard")

    # ---------------------------------------------------------
    # LOAD DATA FROM SERVICES
    # ---------------------------------------------------------

    def _load_dashboard_data(self):
        """Loads the latest records from the backend services."""

        try:
            students = self.student_service.get_all_students() or []
            subjects = self.subject_service.get_all_subjects() or []
            grades = self.grade_service.get_all_grades() or []

            # a teacher only sees the subjects they teach and the grades for them
            if self.teacher_id:
                subjects = [
                    s for s in subjects
                    if s.get("teacher_id") == self.teacher_id
                ]

                allowed_ids = {s.get("subject_id") for s in subjects}

                grades = [
                    g for g in grades
                    if g.get("subject_id") in allowed_ids
                ]

            self.students = students
            self.subjects = subjects
            self.grades_records = grades

        except Exception as err:
            messagebox.showerror(
                "Loading Error",
                f"Unable to load dashboard information.\n\n{err}",
            )

            self.students = []
            self.subjects = []
            self.grades_records = []

        # quick lookups so IDs can be turned into names and records
        self.student_lookup = {
            s.get("person_id"): s for s in self.students
        }
        self.subject_lookup = {
            s.get("subject_id"): s for s in self.subjects
        }
        self.grade_lookup = {
            g.get("grade_id"): g for g in self.grades_records
        }

    def _refresh_dashboard_data(self):
        """Refreshes the records before displaying a section."""

        self._load_dashboard_data()

    # ---------------------------------------------------------
    # SMALL HELPERS
    # ---------------------------------------------------------

    def _student_name(self, student_id):
        """Turns a student ID into a full name."""

        student = self.student_lookup.get(student_id)

        if not student:
            return student_id or ""

        return (
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}"
        ).strip()

    def _subject_name(self, subject_id):
        """Turns a subject ID into a subject name."""

        subject = self.subject_lookup.get(subject_id)

        if not subject:
            return subject_id or ""

        return subject.get("subject_name", subject_id)

    def _final_grade(self, grade):
        """Calculates the weighted final grade using GradeService."""

        try:
            return self.grade_service.calculate_final_grade(grade)
        except Exception:
            return None

    def _letter_grade(self, final_grade):
        """Gets the letter grade using GradeService."""

        if final_grade is None:
            return ""

        try:
            letter, _level = self.grade_service.get_grade_classification(
                final_grade
            )
            return letter
        except Exception:
            return ""

    def _student_average(self, student_id):
        """Averages the weighted final grades of one student, or None."""

        finals = []

        for grade in self.grades_records:
            if grade.get("student_id") == student_id:
                value = self._final_grade(grade)

                if value is not None:
                    finals.append(value)

        if not finals:
            return None

        return round(sum(finals) / len(finals), 2)

    def _default_year_and_term(self):
        """Picks a starting academic year and term for the grade form."""

        # reuse the most recent saved grade if there is one
        if self.grades_records:
            last = self.grades_records[-1]
            year = last.get("academic_year")
            term = last.get("academic_term")

            if year and term:
                return str(year), str(term)

        today = datetime.now()

        if today.month >= 8:
            year = f"{today.year}-{today.year + 1}"
        else:
            year = f"{today.year - 1}-{today.year}"

        return year, "Term 1"

    # ---------------------------------------------------------
    # STYLING
    # ---------------------------------------------------------

    def _configure_styles(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "MH.Treeview",
            background=MH_THEME["bg_card"],
            foreground=MH_THEME["text_white"],
            fieldbackground=MH_THEME["bg_card"],
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0,
        )

        style.configure(
            "MH.Treeview.Heading",
            background="#261A3B",
            foreground=MH_THEME["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )

        style.map(
            "MH.Treeview",
            background=[("selected", MH_THEME["accent_pink"])],
            foreground=[("selected", MH_THEME["text_white"])],
        )
        
        style.configure(
            "MH.TCombobox",
            fieldbackground=MH_THEME["bg_input"],
            background=MH_THEME["bg_input"],
            foreground=MH_THEME["text_white"],
            arrowcolor=MH_THEME["accent_pink"],
            selectbackground=MH_THEME["bg_input"],
            selectforeground=MH_THEME["text_white"],
        )

        style.map(
            "MH.TCombobox",
            fieldbackground=[("readonly", MH_THEME["bg_input"])],
            foreground=[("readonly", MH_THEME["text_white"])],
            selectbackground=[("readonly", MH_THEME["bg_input"])],
            selectforeground=[("readonly", MH_THEME["text_white"])],
        )

        # Pop-out dropdown list: light background with black text
        self.parent.option_add("*TCombobox*Listbox.background", "#F3E8FF")
        self.parent.option_add("*TCombobox*Listbox.foreground", "#000000")
        self.parent.option_add("*TCombobox*Listbox.selectBackground", MH_THEME["accent_pink"])
        self.parent.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
        
    # ---------------------------------------------------------
    # MAIN LAYOUT
    # ---------------------------------------------------------

    def _build_layout(self):

        self.root_frame = tk.Frame(
            self.parent,
            bg=MH_THEME["bg_black"],
        )

        self.root_frame.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(
            self.root_frame,
            bg=MH_THEME["bg_sidebar"],
            width=240,
            highlightbackground=MH_THEME["border_purple"],
            highlightthickness=1,
        )

        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(
            self.root_frame,
            bg=MH_THEME["bg_black"],
        )

        self.main_area.pack(
            side="right",
            fill="both",
            expand=True,
        )

        self._build_sidebar()

        self.content_host = tk.Frame(
            self.main_area,
            bg=MH_THEME["bg_black"],
        )

        self.content_host.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=22,
        )

    def _build_sidebar(self):

        brand_box = tk.Frame(
            self.sidebar,
            bg=MH_THEME["bg_sidebar"],
            padx=18,
            pady=22,
        )

        brand_box.pack(fill="x")

        # Try loading the school logo
        logo_loaded = False

        try:
            if LOGO_FILE:
                logo_image = Image.open(LOGO_FILE)
                logo_image.thumbnail((160, 90))

                self.logo_photo = ImageTk.PhotoImage(logo_image)

                tk.Label(
                    brand_box,
                    image=self.logo_photo,
                    bg=MH_THEME["bg_sidebar"],
                ).pack(anchor="w")

                logo_loaded = True

        except Exception as err:
            print("Could not load school logo:", err)

        if not logo_loaded:
            tk.Label(
                brand_box,
                text="☠ MONSTER HIGH",
                bg=MH_THEME["bg_sidebar"],
                fg=MH_THEME["accent_pink"],
                font=("Trebuchet MS", 15, "bold"),
                anchor="w",
            ).pack(fill="x")

        tk.Label(
            brand_box,
            text="ACADEMY • TEACHER PORTAL",
            bg=MH_THEME["bg_sidebar"],
            fg=MH_THEME["accent_purple"],
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(3, 0))

        tk.Frame(
            self.sidebar,
            bg=MH_THEME["border_purple"],
            height=1,
        ).pack(fill="x", padx=16, pady=(0, 14))

        nav_items = [
            ("dashboard", "❖  Dashboard"),
            ("students", "🎓  Student Records"),
            ("grades", "📋  Grade Management"),
        ]

        for key, label in nav_items:

            btn = tk.Button(
                self.sidebar,
                text=label,
                command=lambda k=key: self.show_section(k),
                bg=MH_THEME["bg_sidebar"],
                fg=MH_THEME["text_white"],
                activebackground=MH_THEME["bg_input"],
                activeforeground=MH_THEME["accent_pink"],
                font=("Segoe UI", 11, "bold"),
                relief="flat",
                anchor="w",
                padx=18,
                pady=12,
                cursor="hand2",
            )

            btn.pack(fill="x", padx=10, pady=4)
            self.nav_buttons[key] = btn

        # Add the spiderweb decoration
        web_canvas = tk.Canvas(
            self.sidebar,
            bg=MH_THEME["bg_sidebar"],
            height=70,
            highlightthickness=0,
            bd=0,
        )

        web_canvas.pack(side="bottom", fill="x")

        draw_corner_web(web_canvas, 0, 0, size=62)
        draw_corner_web(web_canvas, 178, 0, size=62, flip_x=True)

        logout_btn = tk.Button(
            self.sidebar,
            text="⎋  Logout",
            command=self._handle_logout,
            bg="#261426",
            fg=MH_THEME["text_white"],
            activebackground=MH_THEME["accent_pink"],
            activeforeground=MH_THEME["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            anchor="w",
            padx=18,
            pady=10,
            cursor="hand2",
        )

        logout_btn.pack(
            side="bottom",
            fill="x",
            padx=14,
            pady=12,
        )

    def _highlight_nav(self, active_key):

        self.active_tab = active_key

        for key, btn in self.nav_buttons.items():

            if key == active_key:
                btn.configure(
                    bg=MH_THEME["bg_input"],
                    fg=MH_THEME["accent_pink"],
                )

            else:
                btn.configure(
                    bg=MH_THEME["bg_sidebar"],
                    fg=MH_THEME["text_white"],
                )

    def _clear_content(self):

        for widget in self.content_host.winfo_children():
            widget.destroy()

    def _handle_logout(self):
        if not messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            return

        if callable(self.on_logout):
            self.root_frame.destroy()
            self.on_logout()
        else:
            from screens.monster_login import LoginScreen
            auth = self.auth_service
            if auth is None:
                from services.auth_service import AuthService
                auth = AuthService()
            self.parent.destroy()
            app = LoginScreen(auth)
            app.mainloop()

    def show_section(self, section_key):
        """Changes between the dashboard sections."""

        # Reload the records when changing sections
        self._refresh_dashboard_data()

        # an outside grade screen can still be plugged in through on_open_grades
        if section_key == "grades" and callable(self.on_open_grades):
            self.on_open_grades()
            return

        self._highlight_nav(section_key)
        self._clear_content()

        if section_key == "dashboard":
            self._render_dashboard_home()

        elif section_key == "students":
            self._render_student_records()

        elif section_key == "grades":
            self._render_grade_management()

    # ---------------------------------------------------------
    # DASHBOARD HOME
    # ---------------------------------------------------------

    def _render_dashboard_home(self):

        self._build_header(
            title="Welcome Back, Teacher!",
            subtitle="View student information and manage academic records.",
        )

        stats_row = tk.Frame(
            self.content_host,
            bg=MH_THEME["bg_black"],
        )

        stats_row.pack(fill="x", pady=(0, 22))

        stats_row.columnconfigure(
            (0, 1, 2),
            weight=1,
            uniform="stats",
        )

        stats_data = [
            (
                "TOTAL STUDENTS",
                str(len(self.students)),
                MH_THEME["accent_pink"],
            ),
            (
                "TOTAL SUBJECTS",
                str(len(self.subjects)),
                MH_THEME["accent_purple"],
            ),
            (
                "GRADES RECORDED",
                str(len(self.grades_records)),
                MH_THEME["accent_pink"],
            ),
        ]

        for idx, (label, value, accent) in enumerate(stats_data):

            card = RoundedCard(
                stats_row,
                bg_color=MH_THEME["bg_card"],
                border_color=MH_THEME["border_purple"],
                radius=18,
                padding=18,
                height=100,
            )

            card.grid(
                row=0,
                column=idx,
                padx=(0 if idx == 0 else 10, 0 if idx == 2 else 10),
                sticky="ew",
            )

            top_line = tk.Frame(
                card.inner,
                bg=MH_THEME["bg_card"],
            )

            top_line.pack(fill="x")

            tk.Label(
                top_line,
                text=label,
                bg=MH_THEME["bg_card"],
                fg=MH_THEME["text_muted"],
                font=("Segoe UI", 9, "bold"),
            ).pack(side="left")

            tk.Label(
                top_line,
                text="☠",
                bg=MH_THEME["bg_card"],
                fg=accent,
                font=("Segoe UI", 11),
            ).pack(side="right")

            tk.Label(
                card.inner,
                text=value,
                bg=MH_THEME["bg_card"],
                fg=accent,
                font=("Trebuchet MS", 28, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

        # Navigation cards
        sections_row = tk.Frame(
            self.content_host,
            bg=MH_THEME["bg_black"],
        )

        sections_row.pack(fill="both", expand=True)

        sections_row.columnconfigure(
            (0, 1),
            weight=1,
            uniform="main_cards",
        )

        sections_row.rowconfigure(0, weight=1)

        self._build_section_card(
            parent=sections_row,
            col=0,
            icon="🎓",
            title="Student Records",
            description="View and search students, with their grades by subject.",
            btn_text="View Students",
            command=lambda: self.show_section("students"),
            accent=MH_THEME["accent_purple"],
        )

        self._build_section_card(
            parent=sections_row,
            col=1,
            icon="📋",
            title="Grade Management",
            description="Enter and update coursework, project, midterm, and final exam grades.",
            btn_text="Manage Grades",
            command=lambda: self.show_section("grades"),
            accent=MH_THEME["accent_pink"],
        )

    def _build_header(self, title, subtitle):

        header_card = RoundedCard(
            self.content_host,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["border_purple"],
            radius=18,
            padding=18,
            height=104,
        )

        header_card.pack(fill="x", pady=(0, 20))

        left = tk.Frame(
            header_card.inner,
            bg=MH_THEME["bg_card"],
        )

        left.pack(side="left", fill="both", expand=True)

        tk.Label(
            left,
            text=title,
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Trebuchet MS", 20, "bold"),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            left,
            text=subtitle,
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_muted"],
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(fill="x", pady=(4, 0))

        right = tk.Frame(
            header_card.inner,
            bg=MH_THEME["bg_card"],
        )

        right.pack(side="right", anchor="ne")

        if self.teacher_name:
            tk.Label(
                right,
                text=f"Teacher: {self.teacher_name}",
                bg=MH_THEME["bg_card"],
                fg=MH_THEME["accent_pink"],
                font=("Segoe UI", 10, "bold"),
                anchor="e",
            ).pack(anchor="e")

        today = datetime.now().strftime("%B %d, %Y")

        tk.Label(
            right,
            text=f"Date: {today}",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_muted"],
            font=("Segoe UI", 10),
            anchor="e",
        ).pack(anchor="e", pady=(3, 0))

    def _build_section_card(
        self,
        parent,
        col,
        icon,
        title,
        description,
        btn_text,
        command,
        accent,
    ):

        card = RoundedCard(
            parent,
            bg_color=MH_THEME["bg_card"],
            border_color=accent,
            radius=20,
            padding=24,
        )

        card.grid(
            row=0,
            column=col,
            padx=(0 if col == 0 else 10, 0 if col == 1 else 10),
            sticky="nsew",
        )

        tk.Label(
            card.inner,
            text=icon,
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Segoe UI", 30),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            card.inner,
            text=title,
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Trebuchet MS", 17, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 6))

        tk.Label(
            card.inner,
            text=description,
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_muted"],
            font=("Segoe UI", 10),
            wraplength=320,
            justify="left",
            anchor="w",
        ).pack(fill="x", pady=(0, 18))

        tk.Button(
            card.inner,
            text=btn_text,
            command=command,
            bg=MH_THEME["accent_pink"],
            fg=MH_THEME["text_white"],
            activebackground=MH_THEME["accent_pink_hover"],
            activeforeground=MH_THEME["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2",
        ).pack(anchor="w")

    # ---------------------------------------------------------
    # STUDENT RECORDS
    # ---------------------------------------------------------

    def _render_student_records(self):
        """Displays student records from StudentService."""

        self._build_header(
            title="Student Records",
            subtitle="Search and view student profiles (read-only access).",
        )

        search_card = RoundedCard(
            self.content_host,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["border_purple"],
            radius=16,
            padding=14,
            height=74,
        )

        search_card.pack(fill="x", pady=(0, 14))

        tk.Label(
            search_card.inner,
            text="Search (ID, Name, or Grade):",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(0, 10))

        self.student_search_var = tk.StringVar()

        search_entry = tk.Entry(
            search_card.inner,
            textvariable=self.student_search_var,
            bg=MH_THEME["bg_input"],
            fg=MH_THEME["text_white"],
            insertbackground=MH_THEME["accent_pink"],
            font=("Segoe UI", 10),
            relief="flat",
            width=30,
        )

        search_entry.pack(side="left", ipady=5, padx=(0, 10))

        search_entry.bind(
            "<KeyRelease>",
            lambda _event: self._populate_student_table(),
        )

        tk.Button(
            search_card.inner,
            text="Clear",
            command=self._reset_student_search,
            bg=MH_THEME["bg_input"],
            fg=MH_THEME["text_white"],
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            search_card.inner,
            text="View Selected Student",
            command=self._view_selected_student,
            bg=MH_THEME["accent_pink"],
            fg=MH_THEME["text_white"],
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
        ).pack(side="right")

        table_card = RoundedCard(
            self.content_host,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["border_purple"],
            radius=18,
            padding=14,
        )

        table_card.pack(fill="both", expand=True)

        # These columns match the actual Student data, plus the average grade
        columns = (
            "id",
            "name",
            "grade",
            "gender",
            "email",
            "average",
        )

        self.student_tree = ttk.Treeview(
            table_card.inner,
            columns=columns,
            show="headings",
            style="MH.Treeview",
            selectmode="browse",
        )

        headings = {
            "id": ("Student ID", 90, "center"),
            "name": ("Student Name", 190, "w"),
            "grade": ("Grade Level", 90, "center"),
            "gender": ("Gender", 80, "center"),
            "email": ("Email", 210, "w"),
            "average": ("Average", 80, "center"),
        }

        for col_id, (text, width, anchor) in headings.items():

            self.student_tree.heading(
                col_id,
                text=text,
            )

            self.student_tree.column(
                col_id,
                width=width,
                anchor=anchor,
            )

        scrollbar = ttk.Scrollbar(
            table_card.inner,
            orient="vertical",
            command=self.student_tree.yview,
        )

        self.student_tree.configure(
            yscrollcommand=scrollbar.set,
        )

        self.student_tree.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.student_tree.bind(
            "<Double-1>",
            lambda _event: self._view_selected_student(),
        )

        self._populate_student_table()

    def _reset_student_search(self):

        self.student_search_var.set("")
        self._populate_student_table()

    def _populate_student_table(self):
        """Displays students and filters the records when searching."""

        for row in self.student_tree.get_children():
            self.student_tree.delete(row)

        query = self.student_search_var.get().strip().lower()

        for student in self.students:

            # Use person_id because that is the ID field in Student
            student_id = student.get("person_id", "")

            first_name = student.get("first_name", "")
            last_name = student.get("last_name", "")

            full_name = f"{first_name} {last_name}".strip()

            grade_level = student.get("grade_level", "")
            gender = student.get("gender") or ""
            email = student.get("email") or ""

            average = self._student_average(student_id)
            average_text = f"{average:.1f}%" if average is not None else "No grades"

            search_text = (
                f"{student_id} {full_name} "
                f"{grade_level} {gender} {email}"
            ).lower()

            if not query or query in search_text:

                self.student_tree.insert(
                    "",
                    "end",
                    iid=student_id,
                    values=(
                        student_id,
                        full_name,
                        grade_level,
                        gender,
                        email,
                        average_text,
                    ),
                )

    def _view_selected_student(self):
        """Opens the selected student's record inside the dashboard (no popup window)."""

        selected = self.student_tree.selection()

        if not selected:
            messagebox.showinfo(
                "Select a Student",
                "Please select a student row first.",
            )
            return

        self._render_student_detail(selected[0])

    def _render_student_detail(self, student_id):
        """Shows one student's information and grades on the dashboard itself."""

        # Retrieve the latest student record using StudentService
        try:
            student = self.student_service.get_student_by_id(student_id)

        except ValueError:
            messagebox.showerror(
                "Student Not Found",
                "The selected student record could not be found.",
            )
            return

        except Exception as err:
            messagebox.showerror(
                "Error",
                f"Unable to retrieve student information.\n\n{err}",
            )
            return

        # Retrieve this student's grades using GradeService
        try:
            student_grades = self.grade_service.get_grades_by_student(student_id)

            # a teacher only sees grades for the subjects they teach
            if self.teacher_id:
                student_grades = [
                    g for g in student_grades
                    if g.get("subject_id") in self.subject_lookup
                ]

        except Exception:
            student_grades = []

        # Work out the student's age using StudentService
        try:
            age = self.student_service.calculate_student_age(student_id)
        except Exception:
            age = "Not available"

        full_name = (
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}"
        ).strip()

        # swap the student table for the detail screen
        self._highlight_nav("students")
        self._clear_content()

        self._build_header(
            title=full_name,
            subtitle="Read-only student record.",
        )

        # back button returns to the student table
        back_row = tk.Frame(self.content_host, bg=MH_THEME["bg_black"])
        back_row.pack(fill="x", pady=(0, 12))

        tk.Button(
            back_row,
            text="←  Back to Student Records",
            command=lambda: self.show_section("students"),
            bg=MH_THEME["bg_input"],
            fg=MH_THEME["text_white"],
            activebackground=MH_THEME["accent_pink"],
            activeforeground=MH_THEME["text_white"],
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        ).pack(side="left")

        body = tk.Frame(self.content_host, bg=MH_THEME["bg_black"])
        body.pack(fill="both", expand=True)

        # left card: the student's information
        info_card = RoundedCard(
            body,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["accent_pink"],
            radius=18,
            padding=18,
            width=310,
        )
        info_card.pack(side="left", fill="y", padx=(0, 14))

        tk.Label(
            info_card.inner,
            text="Student Information",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Trebuchet MS", 13, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        details = [
            ("Student ID", student.get("person_id", "")),
            ("Grade Level", student.get("grade_level", "")),
            ("Gender", student.get("gender") or "Not provided"),
            ("Email", student.get("email") or "Not provided"),
            ("Parent Contact", student.get("parent_contact") or "Not provided"),
            ("Date of Birth", student.get("date_of_birth") or "Not provided"),
            ("Age", age),
        ]

        for label, value in details:

            tk.Label(
                info_card.inner,
                text=label.upper(),
                bg=MH_THEME["bg_card"],
                fg=MH_THEME["accent_purple"],
                font=("Segoe UI", 8, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(6, 0))

            tk.Label(
                info_card.inner,
                text=str(value),
                bg=MH_THEME["bg_card"],
                fg=MH_THEME["text_white"],
                font=("Segoe UI", 10),
                anchor="w",
                justify="left",
                wraplength=250,
            ).pack(fill="x")

        # right card: grades by subject
        grades_card = RoundedCard(
            body,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["border_purple"],
            radius=18,
            padding=18,
        )
        grades_card.pack(side="left", fill="both", expand=True)

        tk.Label(
            grades_card.inner,
            text="Grades by Subject",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Trebuchet MS", 13, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        # the overall average sits at the bottom of the card
        overall_label = tk.Label(
            grades_card.inner,
            text="",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["accent_pink"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        overall_label.pack(side="bottom", fill="x", pady=(10, 0))

        table_frame = tk.Frame(grades_card.inner, bg=MH_THEME["bg_card"])
        table_frame.pack(fill="both", expand=True)

        grade_columns = ("subject", "period", "final", "letter")

        grades_tree = ttk.Treeview(
            table_frame,
            columns=grade_columns,
            show="headings",
            style="MH.Treeview",
            selectmode="none",
        )

        grade_headings = {
            "subject": ("Subject", 170, "w"),
            "period": ("Year / Term", 140, "w"),
            "final": ("Final Grade", 90, "center"),
            "letter": ("Grade", 60, "center"),
        }

        for col_id, (text, width, anchor) in grade_headings.items():
            grades_tree.heading(col_id, text=text)
            grades_tree.column(col_id, width=width, anchor=anchor)

        grades_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=grades_tree.yview,
        )

        grades_tree.configure(yscrollcommand=grades_scroll.set)

        grades_tree.pack(side="left", fill="both", expand=True)
        grades_scroll.pack(side="right", fill="y")

        finals = []

        for grade in student_grades:

            final_value = self._final_grade(grade)

            if final_value is not None:
                finals.append(final_value)

            grades_tree.insert(
                "",
                "end",
                values=(
                    self._subject_name(grade.get("subject_id")),
                    f"{grade.get('academic_year', '')} | {grade.get('academic_term', '')}",
                    f"{final_value:.1f}%" if final_value is not None else "N/A",
                    self._letter_grade(final_value),
                ),
            )

        if finals:
            overall = round(sum(finals) / len(finals), 2)
            overall_label.config(
                text=f"Overall Average: {overall:.1f}%  ({self._letter_grade(overall)})"
            )
        else:
            overall_label.config(
                text="No grades have been recorded for this student yet."
            )

    # ---------------------------------------------------------
    # GRADE MANAGEMENT
    # ---------------------------------------------------------

    def _render_grade_management(self):
        """Lets the teacher pick a student and subject, then enter or update grades."""

        self._build_header(
            title="Grade Management",
            subtitle="Enter and update coursework, project, midterm, and final exam grades.",
        )

        form_card = RoundedCard(
            self.content_host,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["accent_pink"],
            radius=18,
            padding=18,
        )

        form_card.pack(fill="x", pady=(0, 14))

        student_choices = [
            f"{s.get('person_id')} - {self._student_name(s.get('person_id'))}"
            for s in self.students
        ]

        subject_choices = [
            f"{s.get('subject_id')} - {s.get('subject_name', '')}"
            for s in self.subjects
        ]

        default_year, default_term = self._default_year_and_term()

        # Row 1: student and subject
        top_grid = tk.Frame(form_card.inner, bg=MH_THEME["bg_card"])
        top_grid.pack(fill="x", pady=(0, 12))
        top_grid.columnconfigure((0, 1), weight=1, uniform="sel")

        s_box = tk.Frame(top_grid, bg=MH_THEME["bg_card"])
        s_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        tk.Label(
            s_box,
            text="Select Student",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.grade_student_cb = ttk.Combobox(
            s_box,
            values=student_choices,
            state="readonly",
            style="MH.TCombobox",
        )
        self.grade_student_cb.pack(fill="x", ipady=4, pady=(4, 0))

        if student_choices:
            self.grade_student_cb.current(0)

        sub_box = tk.Frame(top_grid, bg=MH_THEME["bg_card"])
        sub_box.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        tk.Label(
            sub_box,
            text="Select Subject",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.grade_subject_cb = ttk.Combobox(
            sub_box,
            values=subject_choices,
            state="readonly",
            style="MH.TCombobox",
        )
        self.grade_subject_cb.pack(fill="x", ipady=4, pady=(4, 0))

        if subject_choices:
            self.grade_subject_cb.current(0)

        # Row 2: academic year, term, and the four assessment scores
        scores_grid = tk.Frame(form_card.inner, bg=MH_THEME["bg_card"])
        scores_grid.pack(fill="x", pady=(0, 14))
        scores_grid.columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="scores")

        # academic year
        year_box = tk.Frame(scores_grid, bg=MH_THEME["bg_card"])
        year_box.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        tk.Label(
            year_box,
            text="Academic Year",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.year_var = tk.StringVar(value=default_year)

        year_entry = tk.Entry(
            year_box,
            textvariable=self.year_var,
            bg=MH_THEME["bg_input"],
            fg=MH_THEME["text_white"],
            insertbackground=MH_THEME["accent_pink"],
            font=("Segoe UI", 10),
            relief="flat",
        )
        year_entry.pack(fill="x", ipady=5, pady=(4, 0))

        # academic term (can be typed if the school uses different names)
        term_box = tk.Frame(scores_grid, bg=MH_THEME["bg_card"])
        term_box.grid(row=0, column=1, padx=6, sticky="ew")

        tk.Label(
            term_box,
            text="Academic Term",
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.term_cb = ttk.Combobox(
            term_box,
            values=["Term 1", "Term 2", "Term 3"],
            style="MH.TCombobox",
        )
        self.term_cb.set(default_term)
        self.term_cb.pack(fill="x", ipady=4, pady=(4, 0))

        # the four assessment scores
        self.score_vars = {}

        fields = [
            ("coursework", "Coursework"),
            ("project", "Project"),
            ("midterm", "Midterm"),
            ("final_exam", "Final Exam"),
        ]

        for idx, (key, title) in enumerate(fields):

            box = tk.Frame(scores_grid, bg=MH_THEME["bg_card"])
            box.grid(
                row=0,
                column=idx + 2,
                padx=6 if idx < 3 else (6, 0),
                sticky="ew",
            )

            tk.Label(
                box,
                text=f"{title} (0-100)",
                bg=MH_THEME["bg_card"],
                fg=MH_THEME["text_muted"],
                font=("Segoe UI", 9, "bold"),
                anchor="w",
            ).pack(fill="x")

            var = tk.StringVar()
            self.score_vars[key] = var

            tk.Entry(
                box,
                textvariable=var,
                bg=MH_THEME["bg_input"],
                fg=MH_THEME["text_white"],
                insertbackground=MH_THEME["accent_pink"],
                font=("Segoe UI", 10),
                relief="flat",
            ).pack(fill="x", ipady=5, pady=(4, 0))

        # reload saved scores whenever the student, subject, year, or term changes
        self.grade_student_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._load_existing_scores(),
        )
        self.grade_subject_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._load_existing_scores(),
        )
        self.term_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: self._load_existing_scores(),
        )
        self.term_cb.bind(
            "<KeyRelease>",
            lambda _e: self._load_existing_scores(),
        )
        year_entry.bind(
            "<KeyRelease>",
            lambda _e: self._load_existing_scores(),
        )

        self._load_existing_scores()

        btn_row = tk.Frame(form_card.inner, bg=MH_THEME["bg_card"])
        btn_row.pack(fill="x")

        tk.Button(
            btn_row,
            text="Save / Update Grades",
            command=self._save_grades,
            bg=MH_THEME["accent_pink"],
            fg=MH_THEME["text_white"],
            activebackground=MH_THEME["accent_pink_hover"],
            activeforeground=MH_THEME["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            btn_row,
            text="Clear Scores",
            command=self._clear_score_inputs,
            bg=MH_THEME["bg_input"],
            fg=MH_THEME["text_white"],
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
        ).pack(side="left", padx=(10, 0))

        # Recorded grades table
        list_card = RoundedCard(
            self.content_host,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["border_purple"],
            radius=18,
            padding=14,
        )

        list_card.pack(fill="both", expand=True)

        columns = (
            "student",
            "subject",
            "year",
            "term",
            "coursework",
            "project",
            "midterm",
            "final_exam",
            "final",
            "letter",
        )

        self.grades_tree = ttk.Treeview(
            list_card.inner,
            columns=columns,
            show="headings",
            style="MH.Treeview",
            selectmode="browse",
        )

        g_headings = {
            "student": ("Student", 150, "w"),
            "subject": ("Subject", 130, "w"),
            "year": ("Year", 80, "center"),
            "term": ("Term", 65, "center"),
            "coursework": ("Coursework", 85, "center"),
            "project": ("Project", 65, "center"),
            "midterm": ("Midterm", 65, "center"),
            "final_exam": ("Exam", 60, "center"),
            "final": ("Final", 70, "center"),
            "letter": ("Grade", 50, "center"),
        }

        for col_id, (text, width, anchor) in g_headings.items():
            self.grades_tree.heading(col_id, text=text)
            self.grades_tree.column(col_id, width=width, anchor=anchor)

        g_scroll = ttk.Scrollbar(
            list_card.inner,
            orient="vertical",
            command=self.grades_tree.yview,
        )

        self.grades_tree.configure(yscrollcommand=g_scroll.set)

        self.grades_tree.pack(side="left", fill="both", expand=True)
        g_scroll.pack(side="right", fill="y")

        self.grades_tree.bind("<<TreeviewSelect>>", self._on_grade_row_selected)

        self._refresh_grades_table()

    def _selected_student_id(self):

        raw = self.grade_student_cb.get()
        return raw.split(" - ", 1)[0].strip() if " - " in raw else ""

    def _selected_subject_id(self):

        raw = self.grade_subject_cb.get()
        return raw.split(" - ", 1)[0].strip() if " - " in raw else ""

    def _find_existing_grade(self):
        """Finds the saved grade for the chosen student, subject, year, and term."""

        student_id = self._selected_student_id()
        subject_id = self._selected_subject_id()
        year = self.year_var.get().strip()
        term = self.term_cb.get().strip()

        for grade in self.grades_records:
            if (
                grade.get("student_id") == student_id
                and grade.get("subject_id") == subject_id
                and str(grade.get("academic_year")) == year
                and str(grade.get("academic_term")) == term
            ):
                return grade

        return None

    def _clear_score_inputs(self):

        for var in self.score_vars.values():
            var.set("")

    def _load_existing_scores(self):
        """Fills the score boxes if a grade is already saved for the current choices."""

        match = self._find_existing_grade()

        if match:
            for key in self.score_vars:
                self.score_vars[key].set(str(match.get(key, "")))
        else:
            self._clear_score_inputs()

    def _save_grades(self):
        """Adds a new grade or updates the saved one using GradeService."""

        student_id = self._selected_student_id()
        subject_id = self._selected_subject_id()
        year = self.year_var.get().strip()
        term = self.term_cb.get().strip()

        if not student_id or not subject_id:
            messagebox.showwarning(
                "Missing Selection",
                "Please choose a student and subject.",
            )
            return

        if not year or not term:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the academic year and term.",
            )
            return

        # read and check the four scores
        scores = {}

        labels = {
            "coursework": "Coursework",
            "project": "Project",
            "midterm": "Midterm",
            "final_exam": "Final Exam",
        }

        for key, label in labels.items():

            raw_value = self.score_vars[key].get().strip()

            try:
                number = float(raw_value)
            except ValueError:
                messagebox.showerror(
                    "Invalid Score",
                    f"{label} must be a number between 0 and 100.",
                )
                return

            if number < 0 or number > 100:
                messagebox.showerror(
                    "Out of Range",
                    f"{label} must be between 0 and 100.",
                )
                return

            scores[key] = round(number, 1) if number % 1 else int(number)

        existing = self._find_existing_grade()

        if existing:
            result = self.grade_service.update_grade(
                existing.get("grade_id"),
                scores,
            )
            success_message = "Grade updated successfully."

        else:
            result = self.grade_service.add_grade(
                student_id,
                subject_id,
                year,
                term,
                scores["coursework"],
                scores["project"],
                scores["midterm"],
                scores["final_exam"],
            )
            success_message = "Grade added successfully."

        if result != success_message:
            messagebox.showerror("Unable to Save", result)
            return

        # reload the saved records so the table shows what is really stored
        self._refresh_dashboard_data()
        self._refresh_grades_table()

        messagebox.showinfo(
            "Grades Saved",
            f"Saved {self._subject_name(subject_id)} grades for "
            f"{self._student_name(student_id)}.",
        )

    def _refresh_grades_table(self):
        """Fills the grades table from the saved grade records."""

        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        for grade in self.grades_records:

            final_value = self._final_grade(grade)

            self.grades_tree.insert(
                "",
                "end",
                iid=grade.get("grade_id"),
                values=(
                    f"{grade.get('student_id')} - {self._student_name(grade.get('student_id'))}",
                    self._subject_name(grade.get("subject_id")),
                    grade.get("academic_year", ""),
                    grade.get("academic_term", ""),
                    grade.get("coursework", ""),
                    grade.get("project", ""),
                    grade.get("midterm", ""),
                    grade.get("final_exam", ""),
                    f"{final_value:.1f}%" if final_value is not None else "N/A",
                    self._letter_grade(final_value),
                ),
            )

    def _on_grade_row_selected(self, _event):
        """Loads a clicked table row back into the form so it can be edited."""

        selected = self.grades_tree.selection()

        if not selected:
            return

        grade = self.grade_lookup.get(selected[0])

        if not grade:
            return

        student_id = grade.get("student_id")
        subject_id = grade.get("subject_id")

        self.grade_student_cb.set(
            f"{student_id} - {self._student_name(student_id)}"
        )

        self.grade_subject_cb.set(
            f"{subject_id} - {self._subject_name(subject_id)}"
        )

        self.year_var.set(str(grade.get("academic_year", "")))
        self.term_cb.set(str(grade.get("academic_term", "")))

        for key in self.score_vars:
            self.score_vars[key].set(str(grade.get(key, "")))


