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

# Import the school theme and logo so the dashboard matches the rest of the app
# Try to grab the shared school theme + logo path from config.
# If the config module doesn't exist yet (like during early testing), we
# just fall back to empty/None and use the hardcoded defaults below.
try:
    from config.settings import THEME as _CONFIG_THEME, LOGO_FILE
except ImportError:
    _CONFIG_THEME = {}
    LOGO_FILE = None

# Central place for all the colors used across the dashboard.
# Anything that already exists in the shared config takes priority;
# the hex codes after the .get() are fallbacks so this file still works
# even without config.settings.
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
    """
    Tkinter does not give us rounded corners on regular frames out of the box,
    so I built this custom Canvas widget that draws a smooth rounded rectangle
    and places a normal Frame (self.inner) inside it for all the widgets.
    """

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
        # Match the canvas outer background to whatever container holds it so corners look transparent
        # We pop "bg" out of kwargs so it isn't passed to super().__init__ twice.
        parent_bg = kwargs.pop("bg", parent.cget("bg"))

        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )

        # Store the card's visual settings for redraws
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.border_width = border_width
        self.padding = padding

        # Every label, button, and table inside the card gets packed into self.inner
        self.inner = tk.Frame(self, bg=self.bg_color)

        # Place the inner frame as a canvas window so it moves/reshapes with the canvas
        self._window_id = self.create_window(
            self.padding,
            self.padding,
            window=self.inner,
            anchor="nw",
        )

        # Redraw the rounded shape whenever the card resizes so it never looks stretched
        self.bind("<Configure>", self._on_resize)

    def _round_rect_points(self, x1, y1, x2, y2, r):
        """
        Calculates the corner coordinates needed for create_polygon(..., smooth=True)
        to curve each corner smoothly without overlapping when the card is small.
        """
        # Clamp the radius so corners never overlap on tiny cards
        r = max(2, min(r, (x2 - x1) // 2, (y2 - y1) // 2))

        # Return the 12 anchor points that trace a rounded rectangle
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
        """
        Clears the old card background, redraws the rounded border at the new size,
        sends it behind the widgets, and resizes self.inner to fit inside the padding.
        """
        # Guard against zero/negative sizes during initial layout
        width = max(event.width, 40)
        height = max(event.height, 40)

        # Remove the previous card shape before drawing a new one
        self.delete("card_shape")

        # Pull the outline in by half the border width so the border doesn't get clipped
        inset = self.border_width / 2

        points = self._round_rect_points(
            inset,
            inset,
            width - inset,
            height - inset,
            self.radius,
        )

        # Draw the smooth rounded rectangle as the card background + border
        self.create_polygon(
            points,
            smooth=True,
            fill=self.bg_color,
            outline=self.border_color,
            width=self.border_width,
            tags="card_shape",
        )

        # Keep the drawn card shape underneath the embedded inner frame
        self.tag_lower("card_shape")

        # Resize the embedded frame to sit within the card's padding
        inner_width = max(width - (self.padding * 2), 20)
        inner_height = max(height - (self.padding * 2), 20)

        self.itemconfigure(
            self._window_id,
            width=inner_width,
            height=inner_height,
        )


def draw_corner_web(canvas, x0, y0, size=64, flip_x=False):
    """
    Draws a small Monster High spiderweb in the bottom corners of the sidebar
    using radial lines and curved cross-strands.
    """

    # sx flips the web horizontally when drawing the right-hand corner version
    sx = -1 if flip_x else 1
    cx = x0 + (size if flip_x else 0)  # X origin of the web
    cy = y0                            # Y origin of the web
    color = "#3B2459"

    # Three concentric "rings" and five radial spokes make the web pattern
    radii = [size * 0.35, size * 0.65, size * 0.95]
    angles = [0, 22, 45, 67, 90]

    # Draw each spoke as a straight line from the origin outward
    for degree in angles:
        rad = degree * math.pi / 180

        end_x = cx + sx * size * 0.95 * math.cos(rad)
        end_y = cy + size * 0.95 * math.sin(rad)

        canvas.create_line(
            cx, cy, end_x, end_y,
            fill=color,
            width=1,
        )

    # Draw the connecting strands as one polyline per ring
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

        # Save service references so we can query students/subjects/grades later
        self.parent = parent
        self.student_service = student_service
        self.subject_service = subject_service
        self.grade_service = grade_service
        self.auth_service = auth_service

        # Session/user info for display and filtering
        self.teacher_name = teacher_name
        self.teacher_id = teacher_id
        self.on_logout = on_logout
        self.on_open_grades = on_open_grades

        # Lists and lookup dictionaries populated from the backend services
        self.students = []
        self.subjects = []
        self.grades_records = []
        self.student_lookup = {}
        self.subject_lookup = {}
        self.grade_lookup = {}

        # Sidebar tab references + which tab is currently active
        self.nav_buttons = {}
        self.active_tab = "dashboard"

        # Load data first, apply ttk styling, then build the actual UI
        self._load_dashboard_data()
        self._configure_styles()
        self._build_layout()

        # Show the dashboard home tab by default
        self.show_section("dashboard")

    # ---------------------------------------------------------
    # LOAD DATA FROM SERVICES
    # ---------------------------------------------------------

    def _load_dashboard_data(self):
        """
        Pulls all students, subjects, and grades from the services and filters
        subjects and grades down to just what the logged-in teacher actually teaches.
        """

        try:
            students = self.student_service.get_all_students() or []
            subjects = self.subject_service.get_all_subjects() or []
            grades = self.grade_service.get_all_grades() or []

            """
            If a specific teacher logged in, filter out other teachers' subjects
            and only keep grade records that belong to this teacher's subjects.
            """
            if self.teacher_id:
                subjects = [
                    s for s in subjects
                    if s.get("teacher_id") == self.teacher_id
                ]

                # Collect the IDs of subjects this teacher teaches
                allowed_ids = {s.get("subject_id") for s in subjects}

                # Keep only grades whose subject belongs to this teacher
                grades = [
                    g for g in grades
                    if g.get("subject_id") in allowed_ids
                ]

            self.students = students
            self.subjects = subjects
            self.grades_records = grades

        except Exception as err:
            # Show a friendly error and reset to empty lists so UI doesn't crash
            messagebox.showerror(
                "Loading Error",
                f"Unable to load dashboard information.\n\n{err}",
            )

            self.students = []
            self.subjects = []
            self.grades_records = []

        """
        Build dictionary lookups keyed by ID so when we loop through grades later
        we can grab a student's name or subject title immediately without re-querying.
        """
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
        # Reload the latest data from disk/services before rendering a section
        self._load_dashboard_data()

    # ---------------------------------------------------------
    # SMALL HELPERS
    # ---------------------------------------------------------

    def _student_name(self, student_id):
        # Convert a student ID into their full name, or fall back to the ID itself
        student = self.student_lookup.get(student_id)

        if not student:
            return student_id or ""

        return (
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}"
        ).strip()

    def _subject_name(self, subject_id):
        # Convert a subject ID into its subject name, or fall back to the ID itself
        subject = self.subject_lookup.get(subject_id)

        if not subject:
            return subject_id or ""

        return subject.get("subject_name", subject_id)

    def _final_grade(self, grade):
        # Ask GradeService to compute the weighted final percentage for one grade record
        try:
            return self.grade_service.calculate_final_grade(grade)
        except Exception:
            return None

    def _letter_grade(self, final_grade):
        # Ask GradeService to map a numeric final score to a letter grade (A-F)
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
        """
        Loops through all visible grades for a student, calculates each subject's
        weighted final grade, and returns the overall average (or None if ungraded).
        """

        finals = []

        # Collect every numeric final grade for this student
        for grade in self.grades_records:
            if grade.get("student_id") == student_id:
                value = self._final_grade(grade)

                if value is not None:
                    finals.append(value)

        # No grades means no average
        if not finals:
            return None

        return round(sum(finals) / len(finals), 2)

    def _default_year_and_term(self):
        """
        Picks a starting academic year and term for the grade form by reusing
        the last saved grade's period, or falling back to the current school year.
        """

        # Reuse the last saved record's year/term as the default
        if self.grades_records:
            last = self.grades_records[-1]
            year = last.get("academic_year")
            term = last.get("academic_term")

            if year and term:
                return str(year), str(term)

        today = datetime.now()

        # School years start in August, so Aug-Dec belongs to the new year
        if today.month >= 8:
            year = f"{today.year}-{today.year + 1}"
        else:
            year = f"{today.year - 1}-{today.year}"

        return year, "Term 1"

    # ---------------------------------------------------------
    # STYLING
    # ---------------------------------------------------------

    def _configure_styles(self):
        # Apply custom dark Monster High colors to ttk Treeview tables and Comboboxes
        style = ttk.Style()

        # "clam" theme lets us override colors reliably on all platforms
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Base style for all Treeview tables on this dashboard
        style.configure(
            "MH.Treeview",
            background=MH_THEME["bg_card"],
            foreground=MH_THEME["text_white"],
            fieldbackground=MH_THEME["bg_card"],
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0,
        )

        # Header row styling for Treeview tables
        style.configure(
            "MH.Treeview.Heading",
            background="#261A3B",
            foreground=MH_THEME["text_white"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )

        # Highlight the selected row in pink
        style.map(
            "MH.Treeview",
            background=[("selected", MH_THEME["accent_pink"])],
            foreground=[("selected", MH_THEME["text_white"])],
        )

        # Comboboxes share the same dark input look as regular Entry widgets
        style.configure(
            "MH.TCombobox",
            fieldbackground=MH_THEME["bg_input"],
            background=MH_THEME["bg_input"],
            foreground=MH_THEME["text_white"],
            arrowcolor=MH_THEME["accent_pink"],
        )

    # ---------------------------------------------------------
    # MAIN LAYOUT
    # ---------------------------------------------------------

    def _build_layout(self):
        """
        Splits the window into a fixed-width sidebar on the left and a main
        content area on the right where each section swaps in and out.
        """

        # Outer container for the whole dashboard
        self.root_frame = tk.Frame(
            self.parent,
            bg=MH_THEME["bg_black"],
        )

        self.root_frame.pack(fill="both", expand=True)

        # Fixed-width left sidebar
        self.sidebar = tk.Frame(
            self.root_frame,
            bg=MH_THEME["bg_sidebar"],
            width=240,
            highlightbackground=MH_THEME["border_purple"],
            highlightthickness=1,
        )

        self.sidebar.pack(side="left", fill="y")
        # Prevent the sidebar from shrinking to fit its children
        self.sidebar.pack_propagate(False)

        # Right-hand main content area
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

        # content_host is where each section's widgets get built/destroyed
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
        # Builds the left navigation bar with the school logo, tabs, and logout button

        # Brand area at the top of the sidebar
        brand_box = tk.Frame(
            self.sidebar,
            bg=MH_THEME["bg_sidebar"],
            padx=18,
            pady=22,
        )

        brand_box.pack(fill="x")

        # Load the school logo image if it exists; otherwise fall back to text
        logo_loaded = False

        try:
            if LOGO_FILE:
                logo_image = Image.open(LOGO_FILE)
                logo_image.thumbnail((160, 90))

                # Keep a reference on self so the PhotoImage isn't garbage collected
                self.logo_photo = ImageTk.PhotoImage(logo_image)

                tk.Label(
                    brand_box,
                    image=self.logo_photo,
                    bg=MH_THEME["bg_sidebar"],
                ).pack(anchor="w")

                logo_loaded = True

        except Exception as err:
            # If the logo can't be loaded, print a warning and use the text fallback
            print("Could not load school logo:", err)

        # Text fallback when the logo image isn't available
        if not logo_loaded:
            tk.Label(
                brand_box,
                text="☠ MONSTER HIGH",
                bg=MH_THEME["bg_sidebar"],
                fg=MH_THEME["accent_pink"],
                font=("Trebuchet MS", 15, "bold"),
                anchor="w",
            ).pack(fill="x")

        # Subtitle under the brand
        tk.Label(
            brand_box,
            text="ACADEMY • TEACHER PORTAL",
            bg=MH_THEME["bg_sidebar"],
            fg=MH_THEME["accent_purple"],
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(3, 0))

        # Thin divider line under the brand area
        tk.Frame(
            self.sidebar,
            bg=MH_THEME["border_purple"],
            height=1,
        ).pack(fill="x", padx=16, pady=(0, 14))

        # Navigation items: internal key + display label
        nav_items = [
            ("dashboard", "❖  Dashboard"),
            ("students", "🎓  Student Records"),
            ("grades", "📋  Grade Management"),
        ]

        # Create one clickable button per nav item
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
            # Store each button so _highlight_nav can style them later
            self.nav_buttons[key] = btn

        # Decorative spiderwebs anchored to the bottom of the sidebar
        web_canvas = tk.Canvas(
            self.sidebar,
            bg=MH_THEME["bg_sidebar"],
            height=70,
            highlightthickness=0,
            bd=0,
        )

        web_canvas.pack(side="bottom", fill="x")

        # Draw one web in each bottom corner (the right one is flipped)
        draw_corner_web(web_canvas, 0, 0, size=62)
        draw_corner_web(web_canvas, 178, 0, size=62, flip_x=True)

        # Logout button pinned to the bottom of the sidebar
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
        # Highlights the active sidebar tab in pink and resets the other tabs

        self.active_tab = active_key

        for key, btn in self.nav_buttons.items():

            if key == active_key:
                # Active tab: pink text on darker background
                btn.configure(
                    bg=MH_THEME["bg_input"],
                    fg=MH_THEME["accent_pink"],
                )

            else:
                # Inactive tab: normal sidebar color
                btn.configure(
                    bg=MH_THEME["bg_sidebar"],
                    fg=MH_THEME["text_white"],
                )

    def _clear_content(self):
        # Destroy all widgets inside content_host before drawing the next view
        for widget in self.content_host.winfo_children():
            widget.destroy()

    def _handle_logout(self):
        """
        Confirms logout with the teacher, then either triggers the parent callback
        or closes this window and reopens the LoginScreen directly.
        """
        # Ask for confirmation before logging out
        if not messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            return

        # If the parent passed a logout callback, use it
        if callable(self.on_logout):
            self.root_frame.destroy()
            self.on_logout()
        else:
            # Otherwise, destroy the current window and rebuild the login screen
            from screens.monster_login import LoginScreen
            auth = self.auth_service
            if auth is None:
                from services.auth_service import AuthService
                auth = AuthService()
            self.parent.destroy()
            app = LoginScreen(auth)
            app.mainloop()

    def show_section(self, section_key):
        """
        Switches between Dashboard, Student Records, and Grade Management,
        reloading the latest data from the services each time so changes show right away.
        """

        self._refresh_dashboard_data()

        # Allow an external grade screen callback to take over if one was passed in
        if section_key == "grades" and callable(self.on_open_grades):
            self.on_open_grades()
            return

        self._highlight_nav(section_key)
        self._clear_content()

        # Render the requested section
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
        # Draws the home overview with summary stat cards and quick-navigation cards

        self._build_header(
            title="Welcome Back, Teacher!",
            subtitle="View student information and manage academic records.",
        )

        # Horizontal row that holds the three summary stat cards
        stats_row = tk.Frame(
            self.content_host,
            bg=MH_THEME["bg_black"],
        )

        stats_row.pack(fill="x", pady=(0, 22))

        # Three equal-width columns for the stat cards
        stats_row.columnconfigure(
            (0, 1, 2),
            weight=1,
            uniform="stats",
        )

        # (label, value, accent color) for each stat card
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

        # Build one RoundedCard per stat
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

            # Top line of the stat card: label on the left, skull icon on the right
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

            # Big numeric value in the card
            tk.Label(
                card.inner,
                text=value,
                bg=MH_THEME["bg_card"],
                fg=accent,
                font=("Trebuchet MS", 28, "bold"),
                anchor="w",
            ).pack(fill="x", pady=(4, 0))

        # Navigation cards that jump directly to Student Records or Grade Management
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

        # Card that opens the Student Records screen
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

        # Card that opens the Grade Management screen
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
        # Draws the top banner card showing the page title, teacher name, and today's date

        header_card = RoundedCard(
            self.content_host,
            bg_color=MH_THEME["bg_card"],
            border_color=MH_THEME["border_purple"],
            radius=18,
            padding=18,
            height=104,
        )

        header_card.pack(fill="x", pady=(0, 20))

        # Left side: page title + subtitle
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

        # Right side: teacher name (if provided) + today's date
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
        # Generic clickable "section" card used on the dashboard home screen

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

        # Large icon at the top of the card
        tk.Label(
            card.inner,
            text=icon,
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Segoe UI", 30),
            anchor="w",
        ).pack(anchor="w")

        # Card title
        tk.Label(
            card.inner,
            text=title,
            bg=MH_THEME["bg_card"],
            fg=MH_THEME["text_white"],
            font=("Trebuchet MS", 17, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(10, 6))

        # Card description (wrapped so it stays inside the card width)
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

        # Call-to-action button that jumps to the section
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
        """
        Builds the Student Records screen with live search filtering and a
        read-only table of students (double-clicking opens the student's profile).
        """

        self._build_header(
            title="Student Records",
            subtitle="Search and view student profiles (read-only access).",
        )

        # Card holding the search box + action buttons
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

        # StringVar that tracks the current search text
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

        # Re-filter the student table on every keystroke
        search_entry.bind(
            "<KeyRelease>",
            lambda _event: self._populate_student_table(),
        )

        # Clear button resets the search box
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

        # View Selected Student opens the profile view for the highlighted row
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
        ).pack