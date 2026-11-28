"""
Admin Dashboard for the Monster High Academy Report Card System.

Works like the Teacher Dashboard: every section (students, teachers, subjects,
grades, reports) is drawn inside the same window. There are no separate screen
files and no popup windows. Add, edit and view forms open right inside the
dashboard with a Back button.
"""
# Standard library imports for math calculations, Tkinter GUI widgets, and dates
import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

# Pillow library for loading and resizing the Monster High school logo image
from PIL import Image, ImageTk

# Application theme colors, logo path, administrator model, backend services, and PDF export utility
from config.settings import THEME, LOGO_FILE
from models.administrator import Administrator
from services.admin_service import AdminService
from services.student_service import StudentService
from services.teacher_service import TeacherService
from services.subject_service import SubjectService
from services.grade_service import GradeService
from services.report_service import ReportService
from utils.pdf_generator import PDFGenerator


"""
Monster High color palette used across the dashboard UI.
Pulls core shades from config.settings.THEME where available and falls back
to hardcoded dark-purple and hot-pink hex values so the screen still renders
properly even if a setting key is missing.
"""

MH_THEME = {
    "bg_black": THEME.get("bg_root", "#0D0B12"),
    "bg_sidebar": "#14101D",
    "bg_card": THEME.get("bg_surface", "#1B1528"),
    "bg_input": "#241C35",
    "accent_pink": THEME.get("accent_pink", "#FF2A85"),
    "accent_pink_hover": "#FF569E",
    "accent_purple": THEME.get("text_purple", "#A855F7"),
    "border_purple": "#4C2A75",
    "text_white": THEME.get("text_main", "#FFFFFF"),
    "text_muted": "#D4C7E8",
}


class RoundedCard(tk.Canvas):
    """Rounded card with a frame (self.inner) to put widgets in."""

    def __init__(self, parent, bg_color=MH_THEME["bg_card"],
                 border_color=MH_THEME["border_purple"], radius=18,
                 border_width=2, padding=18, **kwargs):
        """
        Sets up a custom Canvas-based rounded card with an inner Frame so regular
        Tkinter widgets can sit inside a rounded border without getting clipped.
        """
        # Remember whether a fixed height was passed; if not, the card auto-grows to fit its content
        self._fixed_height = "height" in kwargs
        # Match the canvas background to the parent container so the outer corners look transparent
        parent_bg = kwargs.pop("bg", parent.cget("bg"))
        parent_bg = kwargs.pop("bg", parent.cget("bg"))
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0, **kwargs)
        

        # Store the card's look settings so the drawing methods can use them later
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.border_width = border_width
        self.padding = padding

        # inner is the normal Frame that other widgets get packed into
        self.inner = tk.Frame(self, bg=self.bg_color)
        # Place the inner frame on the canvas, offset by the padding
        self._window_id = self.create_window(
            self.padding, self.padding, window=self.inner, anchor="nw"
        )
        # Redraw the card whenever the outer canvas or inner content changes size
        self.bind("<Configure>", self._on_resize)
        self.inner.bind("<Configure>", self._on_inner_resize)

    def _on_inner_resize(self, event):
        """
        When no fixed height was given, automatically grow or shrink the card
        to wrap whatever widgets are packed inside self.inner plus top/bottom padding.
        """
        if not self._fixed_height:
            needed_h = event.height + self.padding * 2
            if self.winfo_reqheight() != needed_h:
                self.configure(height=needed_h)

    def _round_rect_points(self, x1, y1, x2, y2, r):
        """
        Calculates the corner points needed to draw a rounded rectangle.
        Clamps the radius so the corners don't overlap if the card gets small.
        """
        r = max(2, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
        # Points go around the rectangle; smooth=True later turns the corners into curves
        return [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]



    def _on_resize(self, event):
        """
        Redraws the rounded card background whenever the widget changes size,
        and resizes the inner frame so the widgets inside fit neatly within the padding.
        """
        
        # Keep a minimum size so the rounded corners don't collapse when the window is tiny
        w = max(event.width, 40)
        h = max(event.height, 40)
        
        # Remove the old card shape before drawing the updated one
        self.delete("card_shape")
        # Pull the border in by half its width so the edges don't get cut off
        inset = self.border_width / 2
        points = self._round_rect_points(inset, inset, w - inset, h - inset, self.radius)

        # Draw the filled, outlined rounded shape
        self.create_polygon(
            points, smooth=True, fill=self.bg_color,
            outline=self.border_color, width=self.border_width, tags="card_shape",
        )
        # Send the background shape behind self.inner so it never covers the widgets
        self.tag_lower("card_shape")
        # Stretch the inner frame to match the card's new width minus left/right padding
        self.itemconfigure(
            self._window_id,
            width=max(w - self.padding * 2, 20),
        )
        # Only lock the inner height if the card was given a fixed height; otherwise let it auto-fit
        if self._fixed_height:
            self.itemconfigure(
                self._window_id,
                height=max(h - self.padding * 2, 20),
            )


def draw_corner_web(canvas, x0, y0, size=62, flip_x=False):
    """Draws a small spiderweb decoration."""
    # sx flips the drawing direction horizontally for the right-hand web
    sx = -1 if flip_x else 1
    cx = x0 + (size if flip_x else 0)
    cy = y0
    color = "#3B2459"
    # Three rings of the web and the angles of the straight "spokes"
    radii = [size * 0.35, size * 0.65, size * 0.95]
    angles = [0, 22, 45, 67, 90]

    # Draw the straight lines going out from the corner
    for deg in angles:
        rad = deg * math.pi / 180
        canvas.create_line(
            cx, cy,
            cx + sx * size * 0.95 * math.cos(rad),
            cy + size * 0.95 * math.sin(rad),
            fill=color, width=1,
        )

    # Draw each ring by connecting the points where it crosses the spokes
    for r in radii:
        points = []
        for deg in angles:
            rad = deg * math.pi / 180
            points.extend([cx + sx * r * math.cos(rad), cy + r * math.sin(rad)])
        canvas.create_line(points, fill=color, width=1)


class AdminDashboard:
    """
    Main Administrator Dashboard for Monster High Academy.
    Gives admins full control over students, teachers, subjects, grades,
    and PDF report card generation from one central window.
    """
    # Caps how wide the main content area stretches on large monitors so cards don't look overly wide
    MAX_CONTENT_WIDTH = 1000

    def __init__(self, root, administrator=None, auth_service=None, on_logout=None):
        """
        Initializes the dashboard window, wires up all backend services,
        loads the initial records, and opens on the home dashboard screen.
        """
        self.root = root
        self.auth_service = auth_service
        self.on_logout = on_logout

        # default admin so this file can be run on its own for testing
        if administrator is None:
            administrator = Administrator(
                "ADM001", "Admin", "User", "admin@monsterhigh.edu",
                access_level="full",
            )
        self.administrator = administrator

        """
        Initialize all backend services and pass their required dependencies
        (for example, SubjectService needs TeacherService, and GradeService needs both).
        """
        self.student_service = StudentService()
        self.teacher_service = TeacherService()
        self.subject_service = SubjectService(self.teacher_service)
        self.grade_service = GradeService(self.student_service, self.subject_service)
        self.report_service = ReportService(
            self.student_service, self.subject_service, self.grade_service
        )
        self.pdf_generator = PDFGenerator()
        self.admin_service = AdminService(
            administrator, self.student_service, self.subject_service,
            self.grade_service, self.report_service,
        )

        # Lists and ID-keyed lookup dictionaries populated when _load_data() runs
        self.students = []
        self.teachers = []
        self.subjects = []
        self.grades_records = []
        self.student_lookup = {}
        self.teacher_lookup = {}
        self.subject_lookup = {}
        self.grade_lookup = {}
        # Track how many PDFs are exported in this session and store sidebar button references
        self.reports_generated = 0   # counted for this session only
        self.nav_buttons = {}
        self._logging_out = False
        self.active_tab = "dashboard"
        # Configure the main Tkinter window title, default size, minimum bounds, and dark background
        self.root.title("Monster High Academy | Administrator Dashboard")
        self.root.geometry("1180x740")
        self.root.minsize(980, 640)
        self.root.resizable(True, True)
        self.root.configure(bg=MH_THEME["bg_black"])
        # Pull initial records from disk, apply dark Monster High styles, build the UI, and show home
        self._load_data()
        self._configure_styles()
        self._build_layout()
        self.show_section("dashboard")

    # ------------------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------------------

    def _load_data(self):
        """
        Pulls all students, teachers, subjects, and grades from the services
        and builds ID lookup dictionaries so we can turn IDs into names fast.
        """
        try:
            # Grab the latest records from each service (defaulting to an empty list if None comes back)
            self.students = self.student_service.get_all_students() or []
            self.teachers = self.teacher_service.get_all_teachers() or []
            self.subjects = self.subject_service.get_all_subjects() or []
            self.grades_records = self.grade_service.get_all_grades() or []
        except Exception as err:
            # Show a popup error and reset everything to empty lists so the UI doesn't crash
            messagebox.showerror(
                "Loading Error",
                f"Unable to load dashboard information.\n\n{err}",
            )
            self.students, self.teachers = [], []
            self.subjects, self.grades_records = [], []
        """
        Map each record by its unique ID so tables and dropdowns can look up
        names and details right away instead of searching the lists every time.
        """
        self.student_lookup = {s.get("person_id"): s for s in self.students}
        self.teacher_lookup = {self._teacher_id(t): t for t in self.teachers}
        self.subject_lookup = {s.get("subject_id"): s for s in self.subjects}
        self.grade_lookup = {g.get("grade_id"): g for g in self.grades_records}

    # ------------------------------------------------------------------
    # SMALL HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _person_name(record):
        # Join first and last name from a student or teacher dictionary cleanly
        return f"{record.get('first_name', '')} {record.get('last_name', '')}".strip()

    @staticmethod
    def _teacher_id(teacher):
        # Teacher records might store their ID under person_id or teacher_id depending on how they were saved
        return teacher.get("person_id") or teacher.get("teacher_id")

    def _student_name(self, student_id):
        # Turn a student ID into their full name, or fall back to showing the ID itself
        student = self.student_lookup.get(student_id)
        return self._person_name(student) if student else (student_id or "")

    def _teacher_name(self, teacher_id):
        # Handle subjects with no teacher assigned yet vs. an ID that no longer exists
        if not teacher_id:
            return "Unassigned"
        teacher = self.teacher_lookup.get(teacher_id)
        return self._person_name(teacher) if teacher else "Teacher not found"

    def _subject_name(self, subject_id):
        # Turn a subject ID into its subject name, or fall back to the ID if missing
        subject = self.subject_lookup.get(subject_id)
        return subject.get("subject_name", subject_id) if subject else (subject_id or "")

    def _final_grade(self, grade):
        # Ask GradeService to compute the weighted final percentage for one grade record
        try:
            return self.grade_service.calculate_final_grade(grade)
        except Exception:
            return None

    def _letter_grade(self, final_grade):
        # Convert a numeric final score into a letter grade (A-F) using GradeService
        if final_grade is None:
            return ""
        try:
            letter, _level = self.grade_service.get_grade_classification(final_grade)
            return letter
        except Exception:
            return ""

    def _student_average(self, student_id):
        """
        Collects all valid weighted final grades for one student across their
        subjects and returns the overall average rounded to 2 decimal places (or None).
        """
        finals = [
            self._final_grade(g) for g in self.grades_records
            if g.get("student_id") == student_id
        ]
        # Drop any grades that could not be calculated
        finals = [f for f in finals if f is not None]
        return round(sum(finals) / len(finals), 2) if finals else None

    def _default_year_and_term(self):
        """
        Pre-fills the grade and report forms with the academic year and term from
        the most recently saved grade, or calculates the current school year if none exist.
        """
        if self.grades_records:
            last = self.grades_records[-1]
            year, term = last.get("academic_year"), last.get("academic_term")
            if year and term:
                return str(year), str(term)
        # School years start in August, so Aug-Dec counts toward the upcoming school year
        today = datetime.now()
        today = datetime.now()
        if today.month >= 8:
            year = f"{today.year}-{today.year + 1}"
        else:
            year = f"{today.year - 1}-{today.year}"
        return year, "Term 1"

    @staticmethod
    def _choice_id(text):
        # Pull just the ID prefix from the left side of a dropdown choice string
        return text.split(" - ", 1)[0].strip() if " - " in text else ""

    def _teacher_choices(self):
        # Build a list of formatted "ID - Full Name" options for teacher assignment dropdowns
        return [
            f"{self._teacher_id(t)} - {self._person_name(t)}"
            for t in self.teachers if self._teacher_id(t)
        ]

    # ------------------------------------------------------------------
    # WIDGET HELPERS (keep the look the same everywhere)
    # ------------------------------------------------------------------

    def _btn(self, parent, text, command, kind="pink"):
        # Creates a flat button: "pink" is the main action style, anything else is the dark secondary style
        if kind == "pink":
            bg, hover = MH_THEME["accent_pink"], MH_THEME["accent_pink_hover"]
        else:
            bg, hover = MH_THEME["bg_input"], "#34284A"
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg=MH_THEME["text_white"],
            activebackground=hover, activeforeground=MH_THEME["text_white"],
            font=("Segoe UI", 9, "bold"), relief="flat", padx=16, pady=7,
            cursor="hand2",
        )

    def _label(self, parent, text):
        # Creates a consistent muted-lavender form field label on top of card backgrounds
        return tk.Label(
            parent, text=text, bg=MH_THEME["bg_card"], fg=MH_THEME["text_muted"],
            font=("Segoe UI", 9, "bold"), anchor="w",
        )

    def _entry(self, parent, var):
        # Creates a flat dark-purple text input box bound to a Tkinter StringVar
        return tk.Entry(
            parent, textvariable=var, bg=MH_THEME["bg_input"],
            fg=MH_THEME["text_white"], insertbackground=MH_THEME["accent_pink"],
            font=("Segoe UI", 10), relief="flat",
        )

    def _combo(self, parent, values, var, state="readonly"):
        # Creates a Monster High themed dropdown box (readonly by default so users pick valid options)
        return ttk.Combobox(
            parent, values=values, textvariable=var, state=state,
            style="MH.TCombobox",
        )

    def _field(self, parent, label, make, row, col, span=1):
        # Wraps a label and an input widget (created via the `make` factory function) inside one grid cell
        box = tk.Frame(parent, bg=MH_THEME["bg_card"])
        box.grid(row=row, column=col, columnspan=span, padx=6, pady=6, sticky="ew")
        self._label(box, label).pack(fill="x")
        widget = make(box)
        widget.pack(fill="x", ipady=4, pady=(4, 0))
        return widget

    def _table(self, parent, columns, selectmode="browse"):
        """columns = [(key, heading, width, anchor), ...]. Returns the Treeview."""
        # Builds a styled Treeview table paired with a vertical scrollbar inside the given container
        tree = ttk.Treeview(
            parent, columns=[c[0] for c in columns], show="headings",
            style="MH.Treeview", selectmode=selectmode,
        )
        # Set the heading text, width and alignment for every column
        for key, heading, width, anchor in columns:
            tree.heading(key, text=heading)
            tree.column(key, width=width, anchor=anchor)

        # Connect the scrollbar to the table so scrolling works both ways
        scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def _back_row(self, text, command):
        # Renders a top-left back button bar for sub-screens (like student detail or add/edit forms)
        row = tk.Frame(self.content_host, bg=MH_THEME["bg_black"])
        row.pack(fill="x", pady=(0, 12))
        self._btn(row, text, command, kind="dark").pack(side="left")

    def _toolbar(self, search_label, search_var, on_change, on_clear, actions):
        """
        Search bar card used by the Teachers and Subjects sections.
        actions = [(text, command, kind), ...] shown on the right, left to right.
        """
        card = RoundedCard(self.content_host, radius=16, padding=14, height=74)
        card.pack(fill="x", pady=(0, 14))

        tk.Label(card.inner, text=search_label, bg=MH_THEME["bg_card"],
                 fg=MH_THEME["text_white"],
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        # Filter the table live as the user types in the search box
        entry = self._entry(card.inner, search_var)
        entry.configure(width=28)
        entry.pack(side="left", ipady=5, padx=(0, 10))
        entry.bind("<KeyRelease>", lambda _e: on_change())

        self._btn(card.inner, "Clear", on_clear, "dark").pack(side="left")
        # Filter the table live as the user types in the search box
        # Packed in reverse because side="right" stacks from the right edge inward
        for text, command, kind in reversed(actions):
            self._btn(card.inner, text, command, kind).pack(side="right", padx=(8, 0))

    @staticmethod
    def _selected_id(tree, noun):
        # Check whether a table row is highlighted before running Edit, View, or Delete actions
        selected = tree.selection()
        if not selected:
            messagebox.showinfo(f"Select a {noun}", f"Please select a {noun.lower()} row first.")
            return None
        # Row IDs (iid) were set to the record IDs, so the selection is the ID itself
        return selected[0]

    # ------------------------------------------------------------------
    # STYLES AND LAYOUT
    # ------------------------------------------------------------------

    def _configure_styles(self):
        """
        Sets up custom ttk styles for Treeview tables and Combobox dropdowns
        so they match the dark Monster High purple-and-pink theme instead of
        default OS gray widgets.
        """
        style = ttk.Style()
        try:
            # Switch to 'clam' so background and heading colors can be customized cleanly
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Table body style (colors, row height, font)
        style.configure(
            "MH.Treeview", background=MH_THEME["bg_card"],
            foreground=MH_THEME["text_white"], fieldbackground=MH_THEME["bg_card"],
            rowheight=34, font=("Segoe UI", 10), borderwidth=0,
        )
        # Table header row style
        style.configure(
            "MH.Treeview.Heading", background="#261A3B",
            foreground=MH_THEME["text_white"], font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        # Selected rows turn hot pink
        style.map(
            "MH.Treeview",
            background=[("selected", MH_THEME["accent_pink"])],
            foreground=[("selected", MH_THEME["text_white"])],
        )
        # Dropdown box style
        style.configure(
            "MH.TCombobox", fieldbackground=MH_THEME["bg_input"],
            background=MH_THEME["bg_input"], foreground=MH_THEME["text_white"],
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
        self.root.option_add("*TCombobox*Listbox.background", "#F3E8FF")
        self.root.option_add("*TCombobox*Listbox.foreground", "#000000")
        self.root.option_add("*TCombobox*Listbox.selectBackground", MH_THEME["accent_pink"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

    def _build_layout(self):
        """
        Splits the main window into a fixed-width sidebar on the left and a
        flexible content container on the right where each section is drawn.
        """
        self.root_frame = tk.Frame(self.root, bg=MH_THEME["bg_black"])
        self.root_frame.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(
            self.root_frame, bg=MH_THEME["bg_sidebar"], width=240,
            highlightbackground=MH_THEME["border_purple"], highlightthickness=1,
        )
        self.sidebar.pack(side="left", fill="y")
        # Keep the sidebar locked at 240px wide instead of shrinking to its buttons
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(self.root_frame, bg=MH_THEME["bg_black"])
        self.main_area.pack(side="right", fill="both", expand=True)

        self._build_sidebar()

        # content_host is where every section gets drawn and cleared
        self.content_host = tk.Frame(self.main_area, bg=MH_THEME["bg_black"])
        self.content_host.pack(fill="both", expand=True, padx=28, pady=22)

        # re-center the home page when the window changes size
        self.main_area.bind("<Configure>", self._update_content_padding)

    def _build_sidebar(self):
        """
        Builds the left navigation sidebar with the school logo, section buttons,
        corner spiderweb decorations, and the logout button at the bottom.
        """
        brand_box = tk.Frame(self.sidebar, bg=MH_THEME["bg_sidebar"], padx=18, pady=22)
        brand_box.pack(fill="x")
        # Try loading the school logo image; fall back to text if the file is missing
        logo_loaded = False
        try:
            logo_image = Image.open(LOGO_FILE)
            logo_image.thumbnail((160, 90))
            # Keep a reference on self so Python doesn't garbage-collect the image
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            tk.Label(brand_box, image=self.logo_photo, bg=MH_THEME["bg_sidebar"]).pack(anchor="w")
            logo_loaded = True
        except Exception as err:
            print("Could not load school logo:", err)

        if not logo_loaded:
            tk.Label(
                brand_box, text="☠ MONSTER HIGH", bg=MH_THEME["bg_sidebar"],
                fg=MH_THEME["accent_pink"], font=("Trebuchet MS", 15, "bold"),
                anchor="w",
            ).pack(fill="x")

        tk.Label(
            brand_box, text="ACADEMY • ADMIN PORTAL", bg=MH_THEME["bg_sidebar"],
            fg=MH_THEME["accent_purple"], font=("Segoe UI", 8, "bold"), anchor="w",
        ).pack(fill="x", pady=(3, 0))

        # Thin divider line under the branding
        tk.Frame(self.sidebar, bg=MH_THEME["border_purple"], height=1).pack(
            fill="x", padx=16, pady=(0, 14)
        )

        # (section key, button text) for each sidebar tab
        nav_items = [
            ("dashboard", "❖  Dashboard"),
            ("students", "🎓  Manage Students"),
            ("teachers", "👩‍🏫  Manage Teachers"),
            ("subjects", "📚  Manage Subjects"),
            ("grades", "📋  Manage Grades"),
            ("reports", "📄  Generate Reports"),
        ]
        # Create a button for each portal section and store it in self.nav_buttons for highlighting
        for key, label in nav_items:
            btn = tk.Button(
                self.sidebar, text=label,
                # k=key locks in this loop's key so every button opens its own section
                command=lambda k=key: self.show_section(k),
                bg=MH_THEME["bg_sidebar"], fg=MH_THEME["text_white"],
                activebackground=MH_THEME["bg_input"],
                activeforeground=MH_THEME["accent_pink"],
                font=("Segoe UI", 10, "bold"), relief="flat", anchor="w",
                padx=12, pady=10, cursor="hand2",
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.nav_buttons[key] = btn
        # Decorative spiderwebs anchored to the bottom corners of the sidebar
        web_canvas = tk.Canvas(
            self.sidebar, bg=MH_THEME["bg_sidebar"], height=70,
            highlightthickness=0, bd=0,
        )
        web_canvas.pack(side="bottom", fill="x")
        draw_corner_web(web_canvas, 0, 0, size=62)
        draw_corner_web(web_canvas, 178, 0, size=62, flip_x=True)

        # Logout button sits at the very bottom of the sidebar
        tk.Button(
            self.sidebar, text="⎋  Logout", command=self._logout,
            bg="#261426", fg=MH_THEME["text_white"],
            activebackground=MH_THEME["accent_pink"],
            activeforeground=MH_THEME["text_white"],
            font=("Segoe UI", 10, "bold"), relief="flat", anchor="w",
            padx=18, pady=10, cursor="hand2",
        ).pack(side="bottom", fill="x", padx=14, pady=12)

    def _logout(self):
        """
        Asks the user to confirm logout, prevents double-clicks from running it twice,
        and either calls on_logout or closes this window so the login screen returns.
        """
        if self._logging_out:
            return

        if not messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            return

        self._logging_out = True

        # If a custom callback was passed in, tear down this frame and hand control back
        if self.on_logout:
            self.root_frame.destroy()
            self.on_logout()
            return

        """
        Close this dashboard window so the waiting login screen detects the window
        closing and shows itself again without spawning a duplicate login window.
        """
        self.root.destroy()

    def _highlight_nav(self, active_key):
        # Highlights the selected sidebar tab in pink and resets all other tabs to default
        self.active_tab = active_key
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(bg=MH_THEME["bg_input"], fg=MH_THEME["accent_pink"])
            else:
                btn.configure(bg=MH_THEME["bg_sidebar"], fg=MH_THEME["text_white"])

    def _update_content_padding(self, event=None):
        """Centers the home page with a max width; other sections use normal padding."""
        try:
            width = self.main_area.winfo_width()
            # Skip if the window hasn't finished measuring its width yet
            if width <= 1:
                return
            if self.active_tab == "dashboard":
                side_pad = max(28, (width - self.MAX_CONTENT_WIDTH) // 2)
            else:
                side_pad = 28
            self.content_host.pack_configure(padx=side_pad)
        except tk.TclError:
            # The widget may already be destroyed (for example during logout), so ignore the error
            pass

    def _clear_content(self):
        # Removes all widgets currently inside content_host before rendering a new screen
        for widget in self.content_host.winfo_children():
            widget.destroy()

    def show_section(self, section_key):
        """
        Switches between dashboard sections, reloading fresh data from the services
        every time so any edits made in one section appear immediately in others.
        """
        self._load_data()
        self._highlight_nav(section_key)
        self._clear_content()

        # Map each section key to the method that draws it
        renderers = {
            "dashboard": self._render_home,
            "students": self._render_students,
            "teachers": self._render_teachers,
            "subjects": self._render_subjects,
            "grades": self._render_grades,
            "reports": self._render_reports,
        }
        renderers[section_key]()
         # Re-apply padding once Tkinter finishes laying out the new section's widgets
        self.root.after_idle(self._update_content_padding)

    def _header(self, title, subtitle, action=None):
        """Top card on every section. action = (button text, command) or None."""
        # Taller card when there is an action button so everything fits
        card = RoundedCard(
            self.content_host, radius=18, padding=18,
            height=144 if action else 104,
        )
        card.pack(fill="x", pady=(0, 20))

        # Left side: title and subtitle
        left = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        left.pack(side="left", fill="both", expand=True)

        tk.Label(
            left, text=title, bg=MH_THEME["bg_card"], fg=MH_THEME["text_white"],
            font=("Trebuchet MS", 20, "bold"), anchor="w",
        ).pack(fill="x")
        tk.Label(
            left, text=subtitle, bg=MH_THEME["bg_card"], fg=MH_THEME["text_muted"],
            font=("Segoe UI", 10), anchor="w",
        ).pack(fill="x", pady=(4, 0))

        # Right side: admin name, today's date and the optional action button
        right = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        right.pack(side="right", anchor="ne")

        admin_name = self._person_name(
            {"first_name": self.administrator.get_first_name(),
             "last_name": self.administrator.get_last_name()}
        )
        tk.Label(
            right, text=f"Admin: {admin_name}", bg=MH_THEME["bg_card"],
            fg=MH_THEME["accent_pink"], font=("Segoe UI", 10, "bold"), anchor="e",
        ).pack(anchor="e")
        tk.Label(
            right, text=f"Date: {datetime.now().strftime('%B %d, %Y')}",
            bg=MH_THEME["bg_card"], fg=MH_THEME["text_muted"],
            font=("Segoe UI", 10), anchor="e",
        ).pack(anchor="e", pady=(3, 8))

        if action:
            self._btn(right, action[0], action[1]).pack(anchor="e")

    # ------------------------------------------------------------------
    # DASHBOARD HOME
    # ------------------------------------------------------------------

    def _render_home(self):
        """
        Draws the main Admin home overview with a welcome banner, four summary
        stat cards across the top, and three quick-access navigation cards below.
        """
        # Top header banner with a shortcut button to open the Add Student form right away
        self._header(
            "Welcome Back, Admin!",
            "Monster High Academy overview and quick controls.",
            action=("+ Quick Add Student", self._render_student_form),
        )
        # Row of 4 equal-width stat cards showing live counts from the loaded data
        stats_row = tk.Frame(self.content_host, bg=MH_THEME["bg_black"])
        stats_row.pack(fill="x", pady=(0, 22))
        stats_row.columnconfigure((0, 1, 2, 3), weight=1, uniform="stats")

        # (label, number to show, accent color) for each stat card
        stats = [
            ("TOTAL STUDENTS", len(self.students), MH_THEME["accent_pink"]),
            ("TOTAL TEACHERS", len(self.teachers), MH_THEME["accent_purple"]),
            ("TOTAL SUBJECTS", len(self.subjects), MH_THEME["accent_pink"]),
            ("REPORTS GENERATED", self.reports_generated, MH_THEME["accent_purple"]),
        ]
        for idx, (label, value, accent) in enumerate(stats):
            self._stat_card(stats_row, idx, label, value, accent)
        # Bottom row of 3 equal-width shortcut cards that jump to the main management tabs
        row = tk.Frame(self.content_host, bg=MH_THEME["bg_black"])
        row.pack(fill="both", expand=True)
        row.columnconfigure((0, 1, 2), weight=1, uniform="main_cards")
        row.rowconfigure(0, weight=1)

        # (icon, title, description, button text, section to open, accent color)
        shortcuts = [
            ("🎓", "Manage Students", "Add, view, edit and delete students, and generate their reports.",
             "View Students", "students", MH_THEME["accent_purple"]),
            ("👩‍🏫", "Manage Teachers", "Add, edit and delete faculty, and see the subjects they teach.",
             "View Teachers", "teachers", MH_THEME["accent_pink"]),
            ("📚", "Manage Subjects", "Add, edit and delete academy subjects and assign their teachers.",
             "View Subjects", "subjects", MH_THEME["accent_purple"]),
        ]
        for col, (icon, title, desc, btn_text, section, accent) in enumerate(shortcuts):
            self._shortcut_card(row, col, icon, title, desc, btn_text, section, accent)

    def _stat_card(self, parent, col, label, value, accent):
        """
        Creates one of the top summary stat cards (like Total Students or Total Teachers)
        with a title, a skull icon in the corner, and the big number underneath.
        """
        card = RoundedCard(parent, radius=18, padding=18, height=122)
        
        # Skip outer left padding on the first card and outer right padding on the last so the row lines up flush
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0 if col == 3 else 8), sticky="ew")
        
        # Top row inside the card holding the uppercase label on the left and the skull icon on the right
        top = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        top = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        top.pack(fill="x")
        tk.Label(top, text=label, bg=MH_THEME["bg_card"], fg=MH_THEME["text_muted"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(top, text="☠", bg=MH_THEME["bg_card"], fg=accent,
                 font=("Segoe UI", 11)).pack(side="right")
        # Large bold counter number below the header row
        tk.Label(card.inner, text=str(value), bg=MH_THEME["bg_card"], fg=accent,
                 font=("Trebuchet MS", 28, "bold"), anchor="w").pack(fill="x", pady=(4, 0))

    def _shortcut_card(self, parent, col, icon, title, desc, btn_text, section, accent):
        # One of the three big home cards: icon, title, description and a button that opens a section
        card = RoundedCard(parent, border_color=accent, radius=20, padding=24)
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0 if col == 2 else 8), sticky="nsew")

        tk.Label(card.inner, text=icon, bg=MH_THEME["bg_card"], fg=MH_THEME["text_white"],
                 font=("Segoe UI", 30), anchor="w").pack(anchor="w")
        tk.Label(card.inner, text=title, bg=MH_THEME["bg_card"], fg=MH_THEME["text_white"],
                 font=("Trebuchet MS", 17, "bold"), anchor="w").pack(fill="x", pady=(10, 6))
        tk.Label(card.inner, text=desc, bg=MH_THEME["bg_card"], fg=MH_THEME["text_muted"],
                 font=("Segoe UI", 10), wraplength=240, justify="left",
                 anchor="w").pack(fill="x", pady=(0, 18))
        self._btn(card.inner, btn_text, lambda: self.show_section(section)).pack(anchor="w")

    # ------------------------------------------------------------------
    # STUDENTS: list, search, view, add, edit, delete
    # ------------------------------------------------------------------

    def _render_students(self):
        # Draws the Manage Students screen: header, search bar with buttons, and the students table
        self._header(
            "Manage Students", "Search, add, view, edit and delete student records.",
            action=("+ Add Student", self._render_student_form),
        )

        # Search card holding the search box on the left and View/Edit/Delete on the right
        search_card = RoundedCard(self.content_host, radius=16, padding=14, height=74)
        search_card.pack(fill="x", pady=(0, 14))

        tk.Label(search_card.inner, text="Search (ID, Name, or Grade):",
                 bg=MH_THEME["bg_card"], fg=MH_THEME["text_white"],
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))

        self.student_search_var = tk.StringVar()
        entry = self._entry(search_card.inner, self.student_search_var)
        entry.configure(width=28)
        entry.pack(side="left", ipady=5, padx=(0, 10))
        # Re-filter the table every time a key is released
        entry.bind("<KeyRelease>", lambda _e: self._populate_student_table())

        self._btn(search_card.inner, "Clear", self._reset_student_search, "dark").pack(side="left")

        self._btn(search_card.inner, "Delete", self._delete_selected_student, "dark").pack(side="right")
        self._btn(search_card.inner, "Edit", self._edit_selected_student, "dark").pack(side="right", padx=8)
        self._btn(search_card.inner, "View", self._view_selected_student).pack(side="right")

        # Card that holds the students table
        table_card = RoundedCard(self.content_host, radius=18, padding=14)
        table_card.pack(fill="both", expand=True)

        self.student_tree = self._table(table_card.inner, [
            ("id", "Student ID", 90, "center"),
            ("name", "Student Name", 190, "w"),
            ("grade", "Grade Level", 90, "center"),
            ("gender", "Gender", 80, "center"),
            ("email", "Email", 210, "w"),
            ("average", "Average", 80, "center"),
        ])
        # Double-clicking a row opens that student's detail page
        self.student_tree.bind("<Double-1>", lambda _e: self._view_selected_student())

        self._populate_student_table()

    def _reset_student_search(self):
        # Clears the search box and shows all students again
        self.student_search_var.set("")
        self._populate_student_table()

    def _populate_student_table(self):
        # Empty the table first so rows don't get duplicated
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)

        query = self.student_search_var.get().strip().lower()

        for student in self.students:
            sid = student.get("person_id", "")
            name = self._person_name(student)
            grade = student.get("grade_level", "")
            gender = student.get("gender") or ""
            email = student.get("email") or ""

            # Skip students that don't match the search text
            if query and query not in f"{sid} {name} {grade} {gender} {email}".lower():
                continue

            avg = self._student_average(sid)
            # iid=sid lets us find the student ID again from the selected row
            self.student_tree.insert(
                "", "end", iid=sid,
                values=(sid, name, grade, gender, email,
                        f"{avg:.1f}%" if avg is not None else "No grades"),
            )

    def _selected_student_id(self):
        # Returns the selected student's ID, or warns the user if no row is selected
        selected = self.student_tree.selection()
        if not selected:
            messagebox.showinfo("Select a Student", "Please select a student row first.")
            return None
        return selected[0]

    def _view_selected_student(self):
        # Opens the detail page for the selected student
        sid = self._selected_student_id()
        if sid:
            self._render_student_detail(sid)

    def _edit_selected_student(self):
        # Opens the edit form filled in with the selected student's data
        sid = self._selected_student_id()
        if sid:
            self._render_student_form(self.student_lookup.get(sid))

    def _delete_selected_student(self):
        # Asks for confirmation, deletes the selected student, then refreshes the list
        sid = self._selected_student_id()
        if not sid:
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {self._student_name(sid)}?",
        ):
            return

        result = self.student_service.delete_student(sid)

        # The service returns a message string; "successfully" means it worked
        if isinstance(result, str) and "successfully" in result.lower():
            messagebox.showinfo("Success", result)
            self.show_section("students")
        else:
            messagebox.showerror("Error", str(result))

    def _render_student_detail(self, student_id):
        """One student's information, grades and report controls, inside the dashboard."""
        # Get the student record, or show an error and stop if it can't be found
        try:
            student = self.student_service.get_student_by_id(student_id)
        except Exception as err:
            messagebox.showerror("Student Not Found", f"Unable to retrieve student.\n\n{err}")
            return

        # Get this student's grades (empty list if something goes wrong)
        try:
            student_grades = self.grade_service.get_grades_by_student(student_id)
        except Exception:
            student_grades = []

        # Calculate the age from the date of birth
        try:
            age = self.student_service.calculate_student_age(student_id)
        except Exception:
            age = "Not available"

        self._highlight_nav("students")
        self._clear_content()

        self._header(
            self._person_name(student), "Student record.",
            action=("Edit Student", lambda: self._render_student_form(student)),
        )
        self._back_row("←  Back to Students", lambda: self.show_section("students"))

        body = tk.Frame(self.content_host, bg=MH_THEME["bg_black"])
        body.pack(fill="both", expand=True)

        # left: information card
        info = RoundedCard(body, border_color=MH_THEME["accent_pink"], padding=18, width=310)
        info.pack(side="left", fill="y", padx=(0, 14))

        tk.Label(info.inner, text="Student Information", bg=MH_THEME["bg_card"],
                 fg=MH_THEME["text_white"], font=("Trebuchet MS", 13, "bold"),
                 anchor="w").pack(fill="x", pady=(0, 8))

        # (label, value) pairs shown in the information card, with fallbacks for empty fields
        details = [
            ("Student ID", student.get("person_id", "")),
            ("Grade Level", student.get("grade_level", "")),
            ("Gender", student.get("gender") or "Not provided"),
            ("Email", student.get("email") or "Not provided"),
            ("Parent Contact", student.get("parent_contact") or "Not provided"),
            ("Date of Birth", student.get("date_of_birth") or "Not provided"),
            ("Age", age),
        ]
        # Show each detail as a small purple label with its value underneath
        for label, value in details:
            tk.Label(info.inner, text=label.upper(), bg=MH_THEME["bg_card"],
                     fg=MH_THEME["accent_purple"], font=("Segoe UI", 8, "bold"),
                     anchor="w").pack(fill="x", pady=(6, 0))
            tk.Label(info.inner, text=str(value), bg=MH_THEME["bg_card"],
                     fg=MH_THEME["text_white"], font=("Segoe UI", 10), anchor="w",
                     justify="left", wraplength=250).pack(fill="x")

        # right: grades + report controls
        right = tk.Frame(body, bg=MH_THEME["bg_black"])
        right.pack(side="left", fill="both", expand=True)

        # Report controls card is packed to the bottom first so it always stays visible
        report_card = RoundedCard(right, border_color=MH_THEME["accent_pink"],
                                  radius=16, padding=14, height=78)
        report_card.pack(side="bottom", fill="x", pady=(12, 0))

        grades_card = RoundedCard(right, padding=18)
        grades_card.pack(side="top", fill="both", expand=True)

        tk.Label(grades_card.inner, text="Grades by Subject", bg=MH_THEME["bg_card"],
                 fg=MH_THEME["text_white"], font=("Trebuchet MS", 13, "bold"),
                 anchor="w").pack(fill="x", pady=(0, 8))

        # Overall average text shown under the table (filled in below)
        overall_label = tk.Label(grades_card.inner, text="", bg=MH_THEME["bg_card"],
                                 fg=MH_THEME["accent_pink"], font=("Segoe UI", 10, "bold"),
                                 anchor="w")
        overall_label.pack(side="bottom", fill="x", pady=(10, 0))

        table_frame = tk.Frame(grades_card.inner, bg=MH_THEME["bg_card"])
        table_frame.pack(fill="both", expand=True)

        # selectmode="none" makes this table view-only
        tree = self._table(table_frame, [
            ("subject", "Subject", 170, "w"),
            ("period", "Year / Term", 140, "w"),
            ("final", "Final Grade", 90, "center"),
            ("letter", "Grade", 60, "center"),
        ], selectmode="none")

        # Add one row per grade and collect the final scores for the overall average
        finals = []
        for grade in student_grades:
            final_value = self._final_grade(grade)
            if final_value is not None:
                finals.append(final_value)
            tree.insert("", "end", values=(
                self._subject_name(grade.get("subject_id")),
                f"{grade.get('academic_year', '')} | {grade.get('academic_term', '')}",
                f"{final_value:.1f}%" if final_value is not None else "N/A",
                self._letter_grade(final_value),
            ))

        # Show the overall average with its letter grade, or a message if there are no grades
        if finals:
            overall = round(sum(finals) / len(finals), 2)
            overall_label.config(text=f"Overall Average: {overall:.1f}%  ({self._letter_grade(overall)})")
        else:
            overall_label.config(text="No grades have been recorded for this student yet.")

        # report controls
        default_year, default_term = self._default_year_and_term()
        year_var = tk.StringVar(value=default_year)
        term_var = tk.StringVar(value=default_term)

        tk.Label(report_card.inner, text="Report:", bg=MH_THEME["bg_card"],
                 fg=MH_THEME["text_white"], font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
        year_entry = self._entry(report_card.inner, year_var)
        year_entry.configure(width=12)
        year_entry.pack(side="left", ipady=4, padx=(0, 8))
        term_box = self._combo(report_card.inner, ["Term 1", "Term 2", "Term 3"], term_var, "normal")
        term_box.configure(width=10)
        term_box.pack(side="left", ipady=3, padx=(0, 10))
        # Button that builds the PDF for this student using the year and term typed above
        self._btn(
            report_card.inner, "Generate PDF Report",
            lambda: self._generate_report(student_id, year_var.get().strip(), term_var.get().strip()),
        ).pack(side="left")

    def _render_student_form(self, student=None):
        """Add form (student=None) or edit form, shown inside the dashboard."""
        # editing is True when an existing student was passed in
        editing = student is not None
        s = student or {}

        self._highlight_nav("students")
        self._clear_content()

        self._header(
            "Edit Student" if editing else "Register New Student",
            f"Student ID: {s.get('person_id', '')}" if editing
            else "Enter the student's information below.",
        )
        self._back_row("←  Back to Students", lambda: self.show_section("students"))

        card = RoundedCard(self.content_host, border_color=MH_THEME["accent_pink"], padding=22)
        card.pack(fill="x")

        # Two-column grid that holds all the form fields
        form = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1, uniform="f")

        # One StringVar per field, pre-filled with the student's data when editing
        v = {
            "first": tk.StringVar(value=s.get("first_name", "")),
            "last": tk.StringVar(value=s.get("last_name", "")),
            "email": tk.StringVar(value=s.get("email") or ""),
            "grade": tk.StringVar(value=str(s.get("grade_level", "7"))),
            "gender": tk.StringVar(value=s.get("gender") or ""),
            "parent": tk.StringVar(value=s.get("parent_contact") or ""),
            "dob": tk.StringVar(value=str(s.get("date_of_birth") or "")[:10]),
        }

        self._field(form, "First Name *", lambda b: self._entry(b, v["first"]), 0, 0)
        self._field(form, "Last Name *", lambda b: self._entry(b, v["last"]), 0, 1)
        self._field(form, "Email", lambda b: self._entry(b, v["email"]), 1, 0)
        self._field(form, "Grade Level *",
                    lambda b: self._combo(b, ["7", "8", "9", "10", "11"], v["grade"]), 1, 1)
        self._field(form, "Gender",
                    lambda b: self._combo(b, ["Female", "Male", "Other"], v["gender"]), 2, 0)
        self._field(form, "Parent Contact", lambda b: self._entry(b, v["parent"]), 2, 1)
        self._field(form, "Date of Birth (YYYY-MM-DD)", lambda b: self._entry(b, v["dob"]), 3, 0)

        def save():
            # Read the form values and trim extra spaces
            first = v["first"].get().strip()
            last = v["last"].get().strip()
            grade_text = v["grade"].get().strip()

            # Required fields must be filled in
            if not first or not last or not grade_text:
                messagebox.showwarning(
                    "Missing Information",
                    "Please complete the first name, last name and grade level.",
                )
                return

            # Grade level must be a whole number
            try:
                grade_level = int(grade_text)
            except ValueError:
                messagebox.showerror("Invalid Grade", "Please select a valid grade level.")
                return

            # Date of birth is optional, but if given it must be a valid YYYY-MM-DD date
            dob = None
            dob_text = v["dob"].get().strip()
            if dob_text:
                try:
                    dob = date.fromisoformat(dob_text)
                except ValueError:
                    messagebox.showerror(
                        "Invalid Date",
                        "Please enter the date as YYYY-MM-DD.\nExample: 2012-05-18",
                    )
                    return

            # Optional fields become None when left empty
            email = v["email"].get().strip() or None
            gender = v["gender"].get().strip() or None
            parent = v["parent"].get().strip() or None

            # Update the existing student, or add a new one; success is the message we expect back
            if editing:
                result = self.student_service.update_student(
                    s.get("person_id"),
                    {
                        "first_name": first, "last_name": last, "email": email,
                        "grade_level": grade_level, "gender": gender,
                        "parent_contact": parent, "date_of_birth": dob,
                    },
                )
                success = "Student updated successfully."
            else:
                result = self.student_service.add_student(
                    first, last, email, grade_level, gender, parent,
                    date_of_birth=dob,
                )
                success = "Student added successfully."

            # Any other message from the service is treated as an error
            if result != success:
                messagebox.showerror("Unable to Save", str(result))
                return

            messagebox.showinfo("Saved", result)
            self.show_section("students")

        buttons = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        buttons.pack(fill="x", pady=(14, 0))
        self._btn(buttons, "Save Changes" if editing else "Register Student", save).pack(side="left")
        self._btn(buttons, "Cancel", lambda: self.show_section("students"), "dark").pack(side="left", padx=(10, 0))

    # ------------------------------------------------------------------
    # TEACHERS: list, search, add, edit, delete
    # ------------------------------------------------------------------

    def _render_teachers(self):
        # Draws the Manage Teachers screen: header, search toolbar, and the teachers table
        self._header(
            "Manage Teachers", "Search, add, edit and delete teacher records.",
            action=("+ Add Teacher", self._render_teacher_form),
        )

        self.teacher_search_var = tk.StringVar()
        self._toolbar(
            "Search (ID, Name, Email, or Subject):",
            self.teacher_search_var,
            self._populate_teacher_table,
            self._reset_teacher_search,
            [("Edit", self._edit_selected_teacher, "pink"),
             ("Delete", self._delete_selected_teacher, "dark")],
        )

        table_card = RoundedCard(self.content_host, radius=18, padding=14)
        table_card.pack(fill="both", expand=True)

        self.teacher_tree = self._table(table_card.inner, [
            ("id", "Teacher ID", 90, "center"),
            ("name", "Teacher Name", 190, "w"),
            ("email", "Email", 220, "w"),
            ("assigned", "Assigned Subjects", 260, "w"),
        ])
        # Double-clicking a row opens the edit form
        self.teacher_tree.bind("<Double-1>", lambda _e: self._edit_selected_teacher())

        self._populate_teacher_table()

    def _reset_teacher_search(self):
        # Clears the search box and shows all teachers again
        self.teacher_search_var.set("")
        self._populate_teacher_table()

    def _populate_teacher_table(self):
        # Empty the table first so rows don't get duplicated
        for row in self.teacher_tree.get_children():
            self.teacher_tree.delete(row)

        query = self.teacher_search_var.get().strip().lower()

        for teacher in self.teachers:
            tid = self._teacher_id(teacher)
            name = self._person_name(teacher)
            email = teacher.get("email") or ""
            specialty = teacher.get("subject_taught") or ""
            # Find every subject that is assigned to this teacher
            taught = [
                s.get("subject_name", "") for s in self.subjects
                if s.get("teacher_id") == tid
            ]
            assigned = ", ".join(taught) if taught else "None assigned"

            # Skip teachers that don't match the search text
            if query and query not in f"{tid} {name} {email} {specialty} {assigned}".lower():
                continue

            self.teacher_tree.insert(
                "", "end", iid=tid,
                values=(tid, name, email, specialty, assigned),
            )

    def _edit_selected_teacher(self):
        # Opens the edit form for the selected teacher
        tid = self._selected_id(self.teacher_tree, "Teacher")
        if tid:
            self._render_teacher_form(self.teacher_lookup.get(tid))

    def _delete_selected_teacher(self):
        # Confirms and deletes the selected teacher, warning if they still have subjects assigned
        tid = self._selected_id(self.teacher_tree, "Teacher")
        if not tid:
            return

        assigned = sum(1 for s in self.subjects if s.get("teacher_id") == tid)
        message = f"Are you sure you want to delete {self._teacher_name(tid)}?"
        if assigned:
            message += f"\n\nThis teacher is assigned to {assigned} subject(s)."

        if not messagebox.askyesno("Confirm Delete", message):
            return

        result = self.teacher_service.delete_teacher(tid)

        if isinstance(result, str) and "successfully" in result.lower():
            messagebox.showinfo("Success", result)
            self.show_section("teachers")
        else:
            messagebox.showerror("Delete Error", str(result))

    def _render_teacher_form(self, teacher=None):
        """Add form (teacher=None) or edit form, shown inside the dashboard."""
        # editing is True when an existing teacher was passed in
        editing = teacher is not None
        t = teacher or {}

        self._highlight_nav("teachers")
        self._clear_content()

        self._header(
            "Edit Teacher" if editing else "Register New Teacher",
            f"Teacher ID: {self._teacher_id(t)}" if editing
            else "Enter the teacher's information below.",
        )
        self._back_row("←  Back to Teachers", lambda: self.show_section("teachers"))

        card = RoundedCard(self.content_host, border_color=MH_THEME["accent_pink"], padding=22)
        card.pack(fill="x")

        form = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1, uniform="f")

        # One StringVar per field, pre-filled with the teacher's data when editing
        v = {
            "first": tk.StringVar(value=t.get("first_name", "")),
            "last": tk.StringVar(value=t.get("last_name", "")),
            "email": tk.StringVar(value=t.get("email") or ""),
            "gender": tk.StringVar(value=t.get("gender") or ""),
            "dob": tk.StringVar(value=str(t.get("date_of_birth") or "")[:10]),
        }

        self._field(form, "First Name *", lambda b: self._entry(b, v["first"]), 0, 0)
        self._field(form, "Last Name *", lambda b: self._entry(b, v["last"]), 0, 1)
        self._field(form, "Email", lambda b: self._entry(b, v["email"]), 1, 0)
        self._field(form, "Gender",
                    lambda b: self._combo(b, ["Female", "Male", "Other"], v["gender"]), 1, 1)
        self._field(form, "Date of Birth (YYYY-MM-DD)", lambda b: self._entry(b, v["dob"]), 2, 0)

        def save():
            # Read the names and make sure both were filled in
            first = v["first"].get().strip()
            last = v["last"].get().strip()

            if not first or not last:
                messagebox.showwarning(
                    "Missing Information",
                    "Please complete the first name and last name.",
                )
                return

            # Date of birth is optional, but if given it must be a valid YYYY-MM-DD date
            dob = None
            dob_text = v["dob"].get().strip()
            if dob_text:
                try:
                    dob = date.fromisoformat(dob_text)
                except ValueError:
                    messagebox.showerror(
                        "Invalid Date",
                        "Please enter the date as YYYY-MM-DD.\nExample: 1985-05-18",
                    )
                    return

            # Optional fields become None when left empty
            email = v["email"].get().strip() or None
            gender = v["gender"].get().strip() or None

            # Update the existing teacher, or add a new one; success is the message we expect back
            if editing:
                result = self.teacher_service.update_teacher(
                    self._teacher_id(t),
                    {
                        "first_name": first, "last_name": last, "email": email,
                        "gender": gender, "date_of_birth": dob,
                    },
                )
                success = "Teacher updated successfully."
            else:
                result = self.teacher_service.add_teacher(
                    first, last, email, None, gender, date_of_birth=dob,
                )
                success = "Teacher added successfully."

            # Any other message from the service is treated as an error
            if result != success:
                messagebox.showerror("Unable to Save", str(result))
                return

            messagebox.showinfo("Saved", result)
            self.show_section("teachers")

        buttons = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        buttons.pack(fill="x", pady=(14, 0))
        self._btn(buttons, "Save Changes" if editing else "Register Teacher", save).pack(side="left")
        self._btn(buttons, "Cancel", lambda: self.show_section("teachers"), "dark").pack(side="left", padx=(10, 0)) 

    # ------------------------------------------------------------------
    # SUBJECTS: list, search, add, edit, delete
    # ------------------------------------------------------------------

    def _render_subjects(self):
        # Draws the Manage Subjects screen: header, search toolbar, and the subjects table
        self._header(
            "Manage Subjects", "Search, add, edit and delete academy subjects.",
            action=("+ Add Subject", self._render_subject_form),
        )

        self.subject_search_var = tk.StringVar()
        self._toolbar(
            "Search (ID, Subject, or Teacher):",
            self.subject_search_var,
            self._populate_subject_table,
            self._reset_subject_search,
            [("Edit", self._edit_selected_subject, "pink"),
             ("Delete", self._delete_selected_subject, "dark")],
        )

        table_card = RoundedCard(self.content_host, radius=18, padding=14)
        table_card.pack(fill="both", expand=True)

        self.subject_tree = self._table(table_card.inner, [
            ("id", "Subject ID", 100, "center"),
            ("name", "Subject Name", 240, "w"),
            ("teacher", "Assigned Teacher", 220, "w"),
            ("grades", "Grades Recorded", 130, "center"),
        ])
        # Double-clicking a row opens the edit form
        self.subject_tree.bind("<Double-1>", lambda _e: self._edit_selected_subject())

        self._populate_subject_table()

    def _reset_subject_search(self):
        # Clears the search box and shows all subjects again
        self.subject_search_var.set("")
        self._populate_subject_table()

    def _populate_subject_table(self):
        # Empty the table first so rows don't get duplicated
        for row in self.subject_tree.get_children():
            self.subject_tree.delete(row)

        query = self.subject_search_var.get().strip().lower()

        for subject in self.subjects:
            sid = subject.get("subject_id")
            name = subject.get("subject_name", "")
            teacher = self._teacher_name(subject.get("teacher_id"))

            # Skip subjects that don't match the search text
            if query and query not in f"{sid} {name} {teacher}".lower():
                continue

            # Count how many grade records belong to this subject
            count = sum(1 for g in self.grades_records if g.get("subject_id") == sid)
            self.subject_tree.insert(
                "", "end", iid=sid, values=(sid, name, teacher, count),
            )

    def _edit_selected_subject(self):
        # Opens the edit form for the selected subject
        sid = self._selected_id(self.subject_tree, "Subject")
        if sid:
            self._render_subject_form(self.subject_lookup.get(sid))

    def _delete_selected_subject(self):
        # Confirms and deletes the selected subject, warning if it already has grades recorded
        sid = self._selected_id(self.subject_tree, "Subject")
        if not sid:
            return

        count = sum(1 for g in self.grades_records if g.get("subject_id") == sid)
        message = f"Are you sure you want to delete {self._subject_name(sid)}?"
        if count:
            message += f"\n\nThis subject has {count} grade record(s) on file."

        if not messagebox.askyesno("Confirm Delete", message):
            return

        result = self.subject_service.delete_subject(sid)

        if result == "Subject deleted successfully.":
            messagebox.showinfo("Success", result)
            self.show_section("subjects")
        else:
            messagebox.showerror("Delete Error", str(result))

    def _render_subject_form(self, subject=None):
        """Add form (subject=None) or edit form, shown inside the dashboard."""
        # editing is True when an existing subject was passed in
        editing = subject is not None
        sub = subject or {}

        # every subject needs a teacher, so stop early if there are none
        teacher_choices = self._teacher_choices()
        if not teacher_choices:
            messagebox.showwarning(
                "No Teachers Available",
                "Please add a teacher before registering a subject.",
            )
            return

        self._highlight_nav("subjects")
        self._clear_content()

        self._header(
            "Edit Subject" if editing else "Register New Subject",
            f"Subject ID: {sub.get('subject_id', '')}" if editing
            else "Enter the subject's information below.",
        )
        self._back_row("←  Back to Subjects", lambda: self.show_section("subjects"))

        card = RoundedCard(self.content_host, border_color=MH_THEME["accent_pink"], padding=22)
        card.pack(fill="x")

        form = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1, uniform="f")

        # pre-select the teacher already assigned (edit) or the first one (add)
        current_teacher = sub.get("teacher_id")
        selected_choice = teacher_choices[0] if not editing else ""
        for choice in teacher_choices:
            if self._choice_id(choice) == current_teacher:
                selected_choice = choice
                break

        name_var = tk.StringVar(value=sub.get("subject_name", ""))
        teacher_var = tk.StringVar(value=selected_choice)

        self._field(form, "Subject Name *", lambda b: self._entry(b, name_var), 0, 0)
        self._field(form, "Assigned Teacher *",
                    lambda b: self._combo(b, teacher_choices, teacher_var), 0, 1)

        def save():
            subject_name = name_var.get().strip()
            teacher_id = self._choice_id(teacher_var.get())

            # The chosen teacher must be one of the real options in the dropdown
            valid_ids = {self._choice_id(c) for c in teacher_choices}
            if not subject_name or teacher_id not in valid_ids:
                messagebox.showwarning(
                    "Missing Information",
                    "Please enter a subject name and select a teacher.",
                )
                return

            # Update the existing subject, or add a new one; success is the message we expect back
            if editing:
                result = self.subject_service.update_subject(
                    sub.get("subject_id"),
                    {"subject_name": subject_name, "teacher_id": teacher_id},
                )
                success = "Subject updated successfully."
            else:
                result = self.subject_service.add_subject(subject_name, teacher_id)
                success = "Subject added successfully."

            # Any other message from the service is treated as an error
            if result != success:
                messagebox.showerror("Unable to Save", str(result))
                return

            messagebox.showinfo("Saved", result)
            self.show_section("subjects")

        buttons = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        buttons.pack(fill="x", pady=(14, 0))
        self._btn(buttons, "Save Changes" if editing else "Save Subject", save).pack(side="left")
        self._btn(buttons, "Cancel", lambda: self.show_section("subjects"), "dark").pack(side="left", padx=(10, 0))

    # ------------------------------------------------------------------
    # GRADES (enter / update for any student and subject)
    # ------------------------------------------------------------------

    def _render_grades(self):
        # Draws the Manage Grades screen: an entry form on top and a table of all grades below
        self._header(
            "Manage Grades",
            "Enter and update coursework, project, midterm, and final exam grades.",
        )

        form_card = RoundedCard(self.content_host, border_color=MH_THEME["accent_pink"],
                                radius=18, padding=18)
        form_card.pack(fill="x", pady=(0, 14))

        # Six-column grid so fields can be different widths using columnspan
        grid = tk.Frame(form_card.inner, bg=MH_THEME["bg_card"])
        grid.pack(fill="x", pady=(0, 8))
        grid.columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="g")

        # Dropdown options formatted as "ID - Name"
        student_choices = [
            f"{s.get('person_id')} - {self._student_name(s.get('person_id'))}"
            for s in self.students
        ]
        subject_choices = [
            f"{s.get('subject_id')} - {s.get('subject_name', '')}"
            for s in self.subjects
        ]
        default_year, default_term = self._default_year_and_term()

        # Form variables are stored on self because other methods read and update them
        self.g_student = tk.StringVar(value=student_choices[0] if student_choices else "")
        self.g_subject = tk.StringVar(value=subject_choices[0] if subject_choices else "")
        self.g_year = tk.StringVar(value=default_year)
        self.g_term = tk.StringVar(value=default_term)
        self.g_scores = {k: tk.StringVar() for k in ("coursework", "project", "midterm", "final_exam")}

        self._field(grid, "Select Student",
                    lambda b: self._combo(b, student_choices, self.g_student), 0, 0, 3)
        self._field(grid, "Select Subject",
                    lambda b: self._combo(b, subject_choices, self.g_subject), 0, 3, 3)
        self._field(grid, "Academic Year", lambda b: self._entry(b, self.g_year), 1, 0)
        self._field(grid, "Academic Term",
                    lambda b: self._combo(b, ["Term 1", "Term 2", "Term 3"], self.g_term, "normal"), 1, 1)

        # One input box for each of the four scores
        score_labels = [("coursework", "Coursework"), ("project", "Project"),
                        ("midterm", "Midterm"), ("final_exam", "Final Exam")]
        for i, (key, title) in enumerate(score_labels):
            # k=key locks in this loop's key for each entry box
            self._field(grid, f"{title} (0-100)",
                        lambda b, k=key: self._entry(b, self.g_scores[k]), 1, i + 2)

        # reload saved scores when the student, subject, year or term changes
        for var in (self.g_student, self.g_subject, self.g_year, self.g_term):
            var.trace_add("write", lambda *_: self._load_existing_scores())

        self._load_existing_scores()

        buttons = tk.Frame(form_card.inner, bg=MH_THEME["bg_card"])
        buttons.pack(fill="x")
        self._btn(buttons, "Save / Update Grades", self._save_grades).pack(side="left")
        self._btn(buttons, "Clear Scores", self._clear_score_inputs, "dark").pack(side="left", padx=(10, 0))
        self._btn(buttons, "Delete Selected Grade", self._delete_selected_grade, "dark").pack(side="right")

        # Table listing every saved grade record
        list_card = RoundedCard(self.content_host, radius=18, padding=14)
        list_card.pack(fill="both", expand=True)

        self.grades_tree = self._table(list_card.inner, [
            ("student", "Student", 150, "w"),
            ("subject", "Subject", 130, "w"),
            ("year", "Year", 80, "center"),
            ("term", "Term", 65, "center"),
            ("coursework", "Coursework", 85, "center"),
            ("project", "Project", 65, "center"),
            ("midterm", "Midterm", 65, "center"),
            ("final_exam", "Exam", 60, "center"),
            ("final", "Final", 70, "center"),
            ("letter", "Grade", 50, "center"),
        ])
        # Clicking a row copies that grade into the form above so it can be edited
        self.grades_tree.bind("<<TreeviewSelect>>", self._on_grade_row_selected)

        self._refresh_grades_table()

    def _find_existing_grade(self):
        # Looks for a saved grade matching the student, subject, year and term chosen in the form
        student_id = self._choice_id(self.g_student.get())
        subject_id = self._choice_id(self.g_subject.get())
        year = self.g_year.get().strip()
        term = self.g_term.get().strip()

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
        # Empties all four score boxes
        for var in self.g_scores.values():
            var.set("")

    def _load_existing_scores(self):
        # Fills the score boxes with saved scores if a matching grade exists, otherwise clears them
        match = self._find_existing_grade()
        if match:
            for key, var in self.g_scores.items():
                var.set(str(match.get(key, "")))
        else:
            self._clear_score_inputs()

    def _save_grades(self):
        # Validates the form, then adds a new grade or updates the existing one
        student_id = self._choice_id(self.g_student.get())
        subject_id = self._choice_id(self.g_subject.get())
        year = self.g_year.get().strip()
        term = self.g_term.get().strip()

        if not student_id or not subject_id:
            messagebox.showwarning("Missing Selection", "Please choose a student and subject.")
            return
        if not year or not term:
            messagebox.showwarning("Missing Information", "Please enter the academic year and term.")
            return

        labels = {"coursework": "Coursework", "project": "Project",
                  "midterm": "Midterm", "final_exam": "Final Exam"}
        scores = {}

        # Each score must be a number from 0 to 100
        for key, label in labels.items():
            try:
                number = float(self.g_scores[key].get().strip())
            except ValueError:
                messagebox.showerror("Invalid Score", f"{label} must be a number between 0 and 100.")
                return
            if number < 0 or number > 100:
                messagebox.showerror("Out of Range", f"{label} must be between 0 and 100.")
                return
            # Keep whole numbers as int and round decimals to one place
            scores[key] = round(number, 1) if number % 1 else int(number)

        existing = self._find_existing_grade()

        # Update if this grade already exists, otherwise add a new record
        if existing:
            result = self.grade_service.update_grade(existing.get("grade_id"), scores)
            success = "Grade updated successfully."
        else:
            result = self.grade_service.add_grade(
                student_id, subject_id, year, term,
                scores["coursework"], scores["project"],
                scores["midterm"], scores["final_exam"],
            )
            success = "Grade added successfully."

        if result != success:
            messagebox.showerror("Unable to Save", str(result))
            return

        # Reload the data so the table shows the new or updated grade
        self._load_data()
        self._refresh_grades_table()
        messagebox.showinfo(
            "Grades Saved",
            f"Saved {self._subject_name(subject_id)} grades for {self._student_name(student_id)}.",
        )

    def _refresh_grades_table(self):
        # Rebuilds the grades table from the latest records
        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        for grade in self.grades_records:
            final_value = self._final_grade(grade)
            sid = grade.get("student_id")
            self.grades_tree.insert(
                "", "end", iid=grade.get("grade_id"),
                values=(
                    f"{sid} - {self._student_name(sid)}",
                    self._subject_name(grade.get("subject_id")),
                    grade.get("academic_year", ""), grade.get("academic_term", ""),
                    grade.get("coursework", ""), grade.get("project", ""),
                    grade.get("midterm", ""), grade.get("final_exam", ""),
                    f"{final_value:.1f}%" if final_value is not None else "N/A",
                    self._letter_grade(final_value),
                ),
            )

    def _on_grade_row_selected(self, _event):
        # When a table row is clicked, copy its values into the form so the grade can be edited
        selected = self.grades_tree.selection()
        if not selected:
            return

        grade = self.grade_lookup.get(selected[0])
        if not grade:
            return

        sid, subj = grade.get("student_id"), grade.get("subject_id")
        self.g_student.set(f"{sid} - {self._student_name(sid)}")
        self.g_subject.set(f"{subj} - {self._subject_name(subj)}")
        self.g_year.set(str(grade.get("academic_year", "")))
        self.g_term.set(str(grade.get("academic_term", "")))

        for key, var in self.g_scores.items():
            var.set(str(grade.get(key, "")))

    def _delete_selected_grade(self):
        """Deletes the grade selected in the grades table."""
        grade_id = self._selected_id(self.grades_tree, "grade")
        if not grade_id:
            return

        grade = self.grade_lookup.get(grade_id)
        if not grade:
            messagebox.showerror("Grade Not Found", "The selected grade could not be found.")
            return

        student_name = self._student_name(grade.get("student_id"))
        subject_name = self._subject_name(grade.get("subject_id"))

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Delete the grade for {student_name} in {subject_name}?\n\nThis action cannot be undone.",
        )
        if not confirmed:
            return

        result = self.grade_service.delete_grade(grade_id)

        # On success, reload the data, refresh the table and clear the score boxes
        if isinstance(result, str) and "successfully" in result.lower():
            self._load_data()
            self._refresh_grades_table()
            self._clear_score_inputs()
            messagebox.showinfo("Grade Deleted", result)
        else:
            messagebox.showerror("Unable to Delete Grade", str(result))

    # ------------------------------------------------------------------
    # REPORTS
    # ------------------------------------------------------------------

    def _render_reports(self):
        """
        Draws the Generate Reports screen where an admin can choose a student,
        academic year, and term, then export their formatted PDF report card.
        """
        self._header("Generate Reports", "Create a PDF report card for any student.")

        card = RoundedCard(self.content_host, border_color=MH_THEME["accent_pink"],
                           radius=18, padding=22)
        card.pack(fill="x")

        # Three-column layout for Student, Academic Year, and Academic Term
        grid = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        grid.pack(fill="x")
        grid.columnconfigure((0, 1, 2), weight=1, uniform="r")

        # Format dropdown items as "ID - Full Name" so _choice_id() can extract the ID on submit
        student_choices = [
            f"{s.get('person_id')} - {self._student_name(s.get('person_id'))}"
            for s in self.students
        ]
        default_year, default_term = self._default_year_and_term()

        student_var = tk.StringVar(value=student_choices[0] if student_choices else "")
        year_var = tk.StringVar(value=default_year)
        term_var = tk.StringVar(value=default_term)

        self._field(grid, "Select Student",
                    lambda b: self._combo(b, student_choices, student_var), 0, 0)
        self._field(grid, "Academic Year", lambda b: self._entry(b, year_var), 0, 1)
        # Set state to "normal" so custom term labels can also be typed if needed
        self._field(grid, "Academic Term",
                    lambda b: self._combo(b, ["Term 1", "Term 2", "Term 3"], term_var, "normal"), 0, 2)

        buttons = tk.Frame(card.inner, bg=MH_THEME["bg_card"])
        buttons.pack(fill="x", pady=(14, 0))
        # Button sends the chosen student ID, year and term to _generate_report
        self._btn(
            buttons, "Generate PDF Report",
            lambda: self._generate_report(
                self._choice_id(student_var.get()),
                year_var.get().strip(), term_var.get().strip(),
            ),
        ).pack(side="left")

    def _generate_report(self, student_id, academic_year, academic_term):
        """Builds a PDF report card (used by the Reports section and the student view)."""
        # Stop early if any required selection or period field was left blank
        if not student_id or not academic_year or not academic_term:
            messagebox.showwarning(
                "Missing Information",
                "Please choose a student and enter the academic year and term.",
            )
            return

        try:
            # Gather the student's profile, subject scores, averages, and remarks for that term
            report_data = self.report_service.prepare_report(
                student_id, academic_year, academic_term
            )

            # ReportService returns an error message string if the student or grades aren't found
            if isinstance(report_data, str):
                messagebox.showerror("Report Error", report_data)
                return

            # Render the PDF file to disk and increment the session counter shown on the dashboard
            file_path = self.pdf_generator.generate_report(report_data)
            self.reports_generated += 1

            messagebox.showinfo(
                "Report Generated",
                f"Student report generated successfully!\n\nSaved to:\n{file_path}",
            )

        except Exception as err:
            # Catch unexpected file-write or PDF rendering failures and show the error to the user
            messagebox.showerror(
                "Report Generation Error",
                f"Unable to generate student report:\n{err}",
            )