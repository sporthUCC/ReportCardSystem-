import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services.student_service import StudentService
from services.teacher_service import TeacherService
from services.subject_service import SubjectService
from services.grade_service import GradeService
from services.report_service import ReportService
from utils.pdf_generator import PDFGenerator
from config.settings import THEME


PLACEHOLDER = "Search students..."

class StudentScreen:

    def __init__(
        self,
        parent,
        student_service,
        grade_service,
        subject_service,
        report_service,
        pdf_generator
    ):
        self.parent = parent
        self.student_service = student_service
        self.grade_service = grade_service
        self.subject_service = subject_service
        self.report_service = report_service
        self.pdf_generator = pdf_generator

        self.all_students = []

        self.apply_monster_high_theme()
        self.build_screen()
        self.load_students()

    # ------------------------------------------------------------------
    # Theme and decoration helpers
    # ------------------------------------------------------------------

    # Applies Monster High colors and fonts to ttk widgets without changing screen logic.
    def apply_monster_high_theme(self):
        style = ttk.Style(self.parent)
        style.theme_use("clam")

        # Dark dropdown lists for comboboxes
        self.parent.option_add("*TCombobox*Listbox.background", THEME["bg_root"])
        self.parent.option_add("*TCombobox*Listbox.foreground", THEME["text_main"])
        self.parent.option_add("*TCombobox*Listbox.selectBackground", THEME["accent_pink"])
        self.parent.option_add("*TCombobox*Listbox.selectForeground", THEME["text_main"])
        self.parent.option_add("*TCombobox*Listbox.font", ("Georgia", 10))

        style.configure(
            ".",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 10),
            bordercolor=THEME["text_purple"],
            focuscolor=THEME["accent_pink"],
        )

        style.configure("MH.TFrame", background=THEME["bg_root"])
        style.configure("MH.Card.TFrame", background=THEME["bg_surface"])

        style.configure(
            "MH.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 10),
        )
        style.configure(
            "MH.Heading.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 22, "bold"),
        )
        style.configure(
            "MH.Subheading.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_purple"],
            font=("Georgia", 14, "bold"),
        )
        style.configure(
            "MH.Card.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            font=("Georgia", 10),
        )
        style.configure(
            "MH.CardTitle.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            font=("Georgia", 18, "bold"),
        )
        style.configure(
            "MH.CardMuted.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["text_purple"],
            font=("Georgia", 9),
        )
        style.configure(
            "MH.CardBold.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["accent_pink"],
            font=("Georgia", 9, "bold"),
        )

        style.configure(
            "MH.TLabelframe",
            background=THEME["bg_surface"],
            bordercolor=THEME["accent_pink"],
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "MH.TLabelframe.Label",
            background=THEME["bg_surface"],
            foreground=THEME["text_purple"],
            font=("Georgia", 10, "bold"),
        )

        style.configure(
            "MH.TButton",
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            bordercolor=THEME["text_purple"],
            font=("Georgia", 10, "bold"),
            padding=(12, 6),
        )
        style.map(
            "MH.TButton",
            background=[("active", THEME["text_purple"])],
            foreground=[("active", THEME["bg_root"])],
        )

        style.configure(
            "MH.Pink.TButton",
            background=THEME["accent_pink"],
            foreground=THEME["text_main"],
            bordercolor=THEME["accent_pink"],
            font=("Georgia", 10, "bold"),
            padding=(14, 6),
        )
        style.map(
            "MH.Pink.TButton",
            background=[("active", THEME["text_purple"])],
            foreground=[("active", THEME["bg_root"])],
        )

        style.configure(
            "MH.Cyan.TButton",
            background=THEME["bg_surface"],
            foreground=THEME["text_purple"],
            bordercolor=THEME["text_purple"],
            font=("Georgia", 10, "bold"),
            padding=(12, 6),
        )
        style.map(
            "MH.Cyan.TButton",
            background=[("active", THEME["text_purple"])],
            foreground=[("active", THEME["bg_root"])],
        )

        style.configure(
            "MH.TEntry",
            fieldbackground=THEME["bg_root"],
            foreground=THEME["text_main"],
            insertcolor=THEME["text_main"],
            bordercolor=THEME["text_purple"],
            padding=5,
        )
        style.map(
            "MH.TEntry",
            fieldbackground=[("readonly", THEME["bg_surface"])],
            foreground=[("readonly", THEME["text_purple"])],
        )

        style.configure(
            "MH.TCombobox",
            fieldbackground=THEME["bg_root"],
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            arrowcolor=THEME["accent_pink"],
            bordercolor=THEME["text_purple"],
            padding=5,
        )
        style.map(
            "MH.TCombobox",
            fieldbackground=[("readonly", THEME["bg_root"])],
            foreground=[("readonly", THEME["text_main"])],
            selectbackground=[("readonly", THEME["bg_root"])],
            selectforeground=[("readonly", THEME["text_main"])],
        )

        style.configure(
            "MH.Treeview",
            background=THEME["bg_surface"],
            fieldbackground=THEME["bg_surface"],
            foreground=THEME["text_main"],
            bordercolor=THEME["text_purple"],
            rowheight=28,
            font=("Georgia", 10),
        )
        style.configure(
            "MH.Treeview.Heading",
            background=THEME["bg_root"],
            foreground=THEME["text_purple"],
            bordercolor=THEME["accent_pink"],
            font=("Georgia", 10, "bold"),
            padding=(8, 6),
        )
        style.map(
            "MH.Treeview",
            background=[("selected", THEME["accent_pink"])],
            foreground=[("selected", THEME["text_main"])],
        )
        style.map(
            "MH.Treeview.Heading",
            background=[("active", THEME["accent_pink"])],
            foreground=[("active", THEME["text_main"])],
        )

        # Keeps row stripe colors working on newer Tk versions
        def fixed_map(option):
            return [
                elm for elm in style.map("MH.Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")
            ]

        style.map(
            "MH.Treeview",
            foreground=fixed_map("foreground"),
            background=fixed_map("background")
        )

        style.configure(
            "MH.Vertical.TScrollbar",
            background=THEME["bg_surface"],
            troughcolor=THEME["bg_root"],
            bordercolor=THEME["text_purple"],
            arrowcolor=THEME["accent_pink"],
        )

    # Draws a banner with spiderwebs in both top corners and a plain
    # Georgia title.
    def create_banner(self, parent, title, subtitle="", height=90):

        canvas = tk.Canvas(
            parent,
            height=height,
            bg=THEME["bg_surface"],
            highlightthickness=0
        )

        scale = height / 90

        def draw(width):
            canvas.delete("all")

            # Background
            canvas.create_rectangle(
                0, 0, width, height,
                fill=THEME["bg_surface"],
                outline=""
            )

            # Spiderwebs in the top left and top right corners
            radius = int(70 * scale)

            def draw_web(corner_x, direction):
                for angle in (0, 22, 45, 68, 90):
                    canvas.create_line(
                        corner_x, 0,
                        corner_x + direction * radius * math.cos(math.radians(angle)),
                        radius * math.sin(math.radians(angle)),
                        fill=THEME["text_purple"]
                    )

                for ring in range(1, 5):
                    r = int(radius * ring / 4)

                    if direction == 1:
                        canvas.create_arc(
                            corner_x - r, -r, corner_x + r, r,
                            start=270,
                            extent=90,
                            style="arc",
                            outline=THEME["text_purple"]
                        )
                    else:
                        canvas.create_arc(
                            corner_x - r, -r, corner_x + r, r,
                            start=180,
                            extent=90,
                            style="arc",
                            outline=THEME["text_purple"]
                        )

            draw_web(0, 1)
            draw_web(width, -1)

            # Plain Georgia title
            text_x = int(radius * 0.6) + 24
            title_y = int(height * 0.42) if subtitle else int(height / 2)

            canvas.create_text(
                text_x, title_y,
                text=title,
                anchor="w",
                fill=THEME["text_main"],
                font=("Georgia", max(int(22 * scale), 14), "bold")
            )

            if subtitle:
                canvas.create_text(
                    text_x, int(height * 0.76),
                    text=subtitle,
                    anchor="w",
                    fill=THEME["text_purple"],
                    font=("Georgia", 10, "italic")
                )

            # Pink bottom edge
            canvas.create_rectangle(
                0, height - 3, width, height,
                fill=THEME["accent_pink"],
                outline=""
            )

        canvas.bind("<Configure>", lambda event: draw(event.width))

        return canvas

    # Thin solid pink divider line.
    def create_divider(self, parent):

        return tk.Frame(
            parent,
            height=2,
            bg=THEME["accent_pink"]
        )

    # Sizes a popup to fit the screen and centres it.
    def center_popup(self, popup, width, height):

        popup.update_idletasks()

        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        width = min(width, screen_width - 60)
        height = min(height, screen_height - 100)

        x = (screen_width - width) // 2
        y = max((screen_height - height) // 2 - 20, 10)

        popup.geometry(f"{width}x{height}+{x}+{y}")

    # Adds alternating row colors to a table.
    def configure_row_tags(self, table):

        table.tag_configure("even", background=THEME["bg_surface"])
        table.tag_configure("odd", background=THEME["bg_root"])
        table.tag_configure("grade_top", foreground=THEME["text_purple"])
        table.tag_configure("grade_low", foreground=THEME["accent_pink"])

    # ------------------------------------------------------------------
    # Main screen
    # ------------------------------------------------------------------

    # Builds the main student management screen.
    def build_screen(self):

        self.main_frame = ttk.Frame(self.parent, padding=20, style="MH.TFrame")
        self.main_frame.pack(fill="both", expand=True)

        self.create_banner(
            self.main_frame,
            "Student Management",
            "Monster High Academy student records",
            height=90
        ).pack(fill="x")

        self.create_divider(self.main_frame).pack(fill="x", pady=(0, 15))

        # Search section.
        search_frame = ttk.Frame(self.main_frame, style="MH.TFrame")
        search_frame.pack(fill="x", pady=(0, 15))

        self.search_entry = ttk.Entry(search_frame, width=35, style="MH.TEntry")
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.insert(0, PLACEHOLDER)

        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry.bind(
            "<Return>",
            lambda event: self.search_students()
        )

        ttk.Button(
            search_frame,
            text="Search",
            command=self.search_students,
            style="MH.Cyan.TButton"
        ).pack(side="left", padx=3)

        ttk.Button(
            search_frame,
            text="Clear",
            command=self.clear_search,
            style="MH.TButton"
        ).pack(side="left", padx=3)

        ttk.Button(
            search_frame,
            text="Refresh",
            command=self.load_students,
            style="MH.TButton"
        ).pack(side="left", padx=3)

        # Action buttons.
        button_frame = ttk.Frame(self.main_frame, style="MH.TFrame")
        button_frame.pack(side="bottom", fill="x", pady=15)

        ttk.Button(
            button_frame,
            text="Add Student",
            command=self.open_add_student,
            style="MH.Pink.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="View Student",
            command=self.view_student,
            style="MH.Cyan.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Edit Student",
            command=self.edit_student,
            style="MH.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Delete Student",
            command=self.delete_student,
            style="MH.TButton"
        ).pack(side="left", padx=5)

        # Student table.
        table_frame = ttk.Frame(self.main_frame, style="MH.TFrame")
        table_frame.pack(fill="both", expand=True)

        columns = (
            "student_id",
            "first_name",
            "last_name",
            "grade_level",
            "email"
        )

        self.student_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="MH.Treeview"
        )

        self.configure_row_tags(self.student_table)

        self.student_table.heading("student_id", text="Student ID")
        self.student_table.heading("first_name", text="First Name")
        self.student_table.heading("last_name", text="Last Name")
        self.student_table.heading("grade_level", text="Grade")
        self.student_table.heading("email", text="Email")

        self.student_table.column("student_id", width=110)
        self.student_table.column("first_name", width=150)
        self.student_table.column("last_name", width=150)
        self.student_table.column("grade_level", width=100)
        self.student_table.column("email", width=200)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.student_table.yview,
            style="MH.Vertical.TScrollbar"
        )

        self.student_table.configure(yscrollcommand=scrollbar.set)

        self.student_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # Removes the placeholder text when the search box is focused.
    def on_search_focus_in(self, event=None):

        if self.search_entry.get() == PLACEHOLDER:
            self.search_entry.delete(0, tk.END)

    # Restores the placeholder text if the search box is left empty.
    def on_search_focus_out(self, event=None):

        if not self.search_entry.get().strip():
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, PLACEHOLDER)

    # Retrieves all student records.
    def load_students(self):

        try:
            self.all_students = self.student_service.get_all_students()
            self.display_students(self.all_students)

        except Exception as err:
            messagebox.showerror(
                "Error",
                f"Unable to load students:\n{err}"
            )

    # Displays student records in the table.
    def display_students(self, students):

        for item in self.student_table.get_children():
            self.student_table.delete(item)

        for index, student in enumerate(students):

            self.student_table.insert(
                "",
                "end",
                values=(
                    student.get("person_id", ""),
                    student.get("first_name", ""),
                    student.get("last_name", ""),
                    student.get("grade_level", ""),
                    student.get("email") or ""
                ),
                tags=("even" if index % 2 == 0 else "odd",)
            )

    # Searches the loaded student records.
    def search_students(self):

        search_term = self.search_entry.get().strip().lower()

        if not search_term or search_term == PLACEHOLDER.lower():
            self.display_students(self.all_students)
            return

        filtered_students = []

        for student in self.all_students:

            searchable_text = " ".join([
                str(student.get("person_id") or ""),
                str(student.get("first_name") or ""),
                str(student.get("last_name") or ""),
                str(student.get("grade_level") or ""),
                str(student.get("email") or "")
            ]).lower()

            if search_term in searchable_text:
                filtered_students.append(student)

        self.display_students(filtered_students)

    # Clears the search field and shows all students.
    def clear_search(self):

        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, PLACEHOLDER)
        self.display_students(self.all_students)

    # ------------------------------------------------------------------
    # Add student
    # ------------------------------------------------------------------

    # Opens the student registration window.
    def open_add_student(self):

        popup = tk.Toplevel(self.parent)
        popup.title("Register New Student")
        popup.resizable(False, False)
        popup.configure(
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )
        popup.transient(self.parent.winfo_toplevel())
        self.center_popup(popup, 500, 610)
        popup.grab_set()

        main_frame = ttk.Frame(popup, padding=25, style="MH.Card.TFrame")
        main_frame.pack(fill="both", expand=True)

        self.create_banner(
            main_frame,
            "New Student",
            "Enter the student's information below",
            height=70
        ).pack(fill="x")

        self.create_divider(main_frame).pack(fill="x", pady=(0, 15))

        form_frame = ttk.Frame(main_frame, style="MH.Card.TFrame")
        form_frame.pack(fill="x")

        # First name.
        ttk.Label(
            form_frame,
            text="First Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=7)

        first_name_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        first_name_entry.grid(row=0, column=1, sticky="ew", pady=7)

        # Last name.
        ttk.Label(
            form_frame,
            text="Last Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=7)

        last_name_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        last_name_entry.grid(row=1, column=1, sticky="ew", pady=7)

        # Email.
        ttk.Label(
            form_frame,
            text="Email",
            style="MH.CardBold.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=7)

        email_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        email_entry.grid(row=2, column=1, sticky="ew", pady=7)

        # Grade level.
        ttk.Label(
            form_frame,
            text="Grade Level *",
            style="MH.CardBold.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=7)

        grade_combo = ttk.Combobox(
            form_frame,
            values=("7", "8", "9", "10", "11"),
            state="readonly",
            width=32,
            style="MH.TCombobox"
        )
        grade_combo.grid(row=3, column=1, sticky="ew", pady=7)

        # Gender.
        ttk.Label(
            form_frame,
            text="Gender",
            style="MH.CardBold.TLabel"
        ).grid(row=4, column=0, sticky="w", pady=7)

        gender_combo = ttk.Combobox(
            form_frame,
            values=("Female", "Male", "Other"),
            state="readonly",
            width=32,
            style="MH.TCombobox"
        )
        gender_combo.grid(row=4, column=1, sticky="ew", pady=7)

        # Parent contact.
        ttk.Label(
            form_frame,
            text="Parent Contact",
            style="MH.CardBold.TLabel"
        ).grid(row=5, column=0, sticky="w", pady=7)

        parent_contact_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        parent_contact_entry.grid(row=5, column=1, sticky="ew", pady=7)

        # Date of birth.
        ttk.Label(
            form_frame,
            text="Date of Birth",
            style="MH.CardBold.TLabel"
        ).grid(row=6, column=0, sticky="w", pady=7)

        dob_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        dob_entry.grid(row=6, column=1, sticky="ew", pady=7)
        dob_entry.insert(0, "YYYY-MM-DD")

        ttk.Label(
            main_frame,
            text="* Required fields. Date format: YYYY-MM-DD",
            style="MH.CardMuted.TLabel"
        ).pack(anchor="w", pady=(12, 15))

        # Registers the student using StudentService.
        def save_student():

            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            grade_level = grade_combo.get().strip()
            gender = gender_combo.get().strip()
            parent_contact = parent_contact_entry.get().strip()
            dob_text = dob_entry.get().strip()

            # Check required fields.
            if not first_name or not last_name or not grade_level:
                messagebox.showwarning(
                    "Missing Information",
                    "Please complete the first name, last name "
                    "and grade level.",
                    parent=popup
                )
                return

            # Convert grade level to an integer.
            try:
                grade_level = int(grade_level)

            except ValueError:
                messagebox.showerror(
                    "Invalid Grade",
                    "Please select a valid grade level.",
                    parent=popup
                )
                return

            # Convert date of birth into a date object.
            dob = None

            if dob_text and dob_text != "YYYY-MM-DD":

                try:
                    dob = date.fromisoformat(dob_text)

                except ValueError:
                    messagebox.showerror(
                        "Invalid Date",
                        "Please enter the date in YYYY-MM-DD format.\n"
                        "Example: 2012-05-18",
                        parent=popup
                    )
                    return

            # Send the information to StudentService.
            result = self.student_service.add_student(
                first_name,
                last_name,
                email or None,
                grade_level,
                gender or None,
                parent_contact or None,
                date_of_birth=dob
            )

            if result == "Student added successfully.":

                messagebox.showinfo(
                    "Registration Successful",
                    result,
                    parent=popup
                )

                # Refresh the student table.
                self.load_students()

                popup.destroy()

            else:
                messagebox.showerror(
                    "Registration Error",
                    result,
                    parent=popup
                )

        # Form buttons.
        button_frame = ttk.Frame(main_frame, style="MH.Card.TFrame")
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Register Student",
            command=save_student,
            style="MH.Pink.TButton"
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            style="MH.TButton"
        ).pack(side="left")

        first_name_entry.focus_set()

    # ------------------------------------------------------------------
    # Select, view and edit
    # ------------------------------------------------------------------

    # Retrieves the selected student.
    def get_selected_student(self):

        selected_item = self.student_table.selection()

        if not selected_item:
            messagebox.showwarning(
                "No Selection",
                "Please select a student first."
            )
            return None

        student_id = self.student_table.item(
            selected_item[0],
            "values"
        )[0]

        try:
            return self.student_service.get_student_by_id(student_id)

        except ValueError as err:
            messagebox.showerror("Error", str(err))
            return None

    # Opens the student details popup.
    def view_student(self):

        student = self.get_selected_student()

        if student is None:
            return

        self.open_student_details(student)

    # Opens a form to edit the selected student's information.
    def edit_student(self):

        student = self.get_selected_student()

        if student is None:
            return

        popup = tk.Toplevel(self.parent)
        popup.title("Edit Student")
        popup.resizable(False, False)
        popup.configure(
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )
        popup.transient(self.parent.winfo_toplevel())
        self.center_popup(popup, 500, 640)
        popup.grab_set()

        main_frame = ttk.Frame(popup, padding=25, style="MH.Card.TFrame")
        main_frame.pack(fill="both", expand=True)

        self.create_banner(
            main_frame,
            "Edit Monster",
            "Update the student's information below",
            height=70
        ).pack(fill="x")

        self.create_divider(main_frame).pack(fill="x", pady=(0, 12))

        form_frame = ttk.Frame(main_frame, style="MH.Card.TFrame")
        form_frame.pack(fill="x")

        # Student ID is displayed but cannot be changed.
        ttk.Label(
            form_frame,
            text="Student ID",
            style="MH.CardBold.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=7)

        student_id_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        student_id_entry.grid(row=0, column=1, sticky="ew", pady=7)
        student_id_entry.insert(0, student.get("person_id", ""))
        student_id_entry.configure(state="readonly")

        # First name.
        ttk.Label(
            form_frame,
            text="First Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=7)

        first_name_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        first_name_entry.grid(row=1, column=1, sticky="ew", pady=7)
        first_name_entry.insert(0, student.get("first_name", ""))

        # Last name.
        ttk.Label(
            form_frame,
            text="Last Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=7)

        last_name_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        last_name_entry.grid(row=2, column=1, sticky="ew", pady=7)
        last_name_entry.insert(0, student.get("last_name", ""))

        # Email.
        ttk.Label(
            form_frame,
            text="Email",
            style="MH.CardBold.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=7)

        email_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        email_entry.grid(row=3, column=1, sticky="ew", pady=7)
        email_entry.insert(0, student.get("email") or "")

        # Grade level.
        ttk.Label(
            form_frame,
            text="Grade Level *",
            style="MH.CardBold.TLabel"
        ).grid(row=4, column=0, sticky="w", pady=7)

        grade_combo = ttk.Combobox(
            form_frame,
            values=("7", "8", "9", "10", "11"),
            state="readonly",
            width=32,
            style="MH.TCombobox"
        )
        grade_combo.grid(row=4, column=1, sticky="ew", pady=7)
        grade_combo.set(str(student.get("grade_level", "")))

        # Gender.
        ttk.Label(
            form_frame,
            text="Gender",
            style="MH.CardBold.TLabel"
        ).grid(row=5, column=0, sticky="w", pady=7)

        gender_combo = ttk.Combobox(
            form_frame,
            values=("Female", "Male", "Other"),
            state="readonly",
            width=32,
            style="MH.TCombobox"
        )
        gender_combo.grid(row=5, column=1, sticky="ew", pady=7)
        gender_combo.set(student.get("gender") or "")

        # Parent contact.
        ttk.Label(
            form_frame,
            text="Parent Contact",
            style="MH.CardBold.TLabel"
        ).grid(row=6, column=0, sticky="w", pady=7)

        parent_contact_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        parent_contact_entry.grid(row=6, column=1, sticky="ew", pady=7)
        parent_contact_entry.insert(
            0,
            student.get("parent_contact") or ""
        )

        # Date of birth.
        ttk.Label(
            form_frame,
            text="Date of Birth",
            style="MH.CardBold.TLabel"
        ).grid(row=7, column=0, sticky="w", pady=7)

        dob_entry = ttk.Entry(form_frame, width=35, style="MH.TEntry")
        dob_entry.grid(row=7, column=1, sticky="ew", pady=7)

        existing_dob = student.get("date_of_birth")

        if existing_dob:
            dob_entry.insert(0, str(existing_dob)[:10])

        ttk.Label(
            main_frame,
            text="* Required fields. Date format: YYYY-MM-DD",
            style="MH.CardMuted.TLabel"
        ).pack(anchor="w", pady=(12, 15))

        # Saves the updated student information.
        def save_changes():

            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            grade_level = grade_combo.get().strip()
            gender = gender_combo.get().strip()
            parent_contact = parent_contact_entry.get().strip()
            dob_text = dob_entry.get().strip()

            # Check required fields.
            if not first_name or not last_name or not grade_level:
                messagebox.showwarning(
                    "Missing Information",
                    "Please complete the first name, last name "
                    "and grade level.",
                    parent=popup
                )
                return

            # Convert grade level into an integer.
            try:
                grade_level = int(grade_level)

            except ValueError:
                messagebox.showerror(
                    "Invalid Grade",
                    "Please select a valid grade level.",
                    parent=popup
                )
                return

            # Convert date of birth into a date object.
            dob = None

            if dob_text:

                try:
                    dob = date.fromisoformat(dob_text)

                except ValueError:
                    messagebox.showerror(
                        "Invalid Date",
                        "Please enter the date in YYYY-MM-DD format.\n"
                        "Example: 2012-05-18",
                        parent=popup
                    )
                    return

            # Prepare the information for StudentService.
            update_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email or None,
                "grade_level": grade_level,
                "gender": gender or None,
                "parent_contact": parent_contact or None,
                "date_of_birth": dob
            }

            # Update the student record.
            result = self.student_service.update_student(
                student.get("person_id"),
                update_data
            )

            if result == "Student updated successfully.":

                messagebox.showinfo(
                    "Update Successful",
                    result,
                    parent=popup
                )

                self.load_students()
                popup.destroy()

            else:
                messagebox.showerror(
                    "Update Error",
                    result,
                    parent=popup
                )

        # Form buttons.
        button_frame = ttk.Frame(main_frame, style="MH.Card.TFrame")
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes,
            style="MH.Pink.TButton"
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            style="MH.TButton"
        ).pack(side="left")

        first_name_entry.focus_set()

    # Displays personal and academic information.
    def open_student_details(self, student):

        popup = tk.Toplevel(self.parent)
        popup.title("Student Information")
        popup.minsize(850, 620)
        popup.configure(
            bg=THEME["bg_root"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )
        popup.transient(self.parent.winfo_toplevel())
        self.center_popup(popup, 1000, 760)
        popup.grab_set()

        student_id = student.get("person_id", "")

        main_frame = ttk.Frame(popup, padding=20, style="MH.TFrame")
        main_frame.pack(fill="both", expand=True)

        full_name = (
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}"
        ).strip()

        self.create_banner(
            main_frame,
            full_name,
            f"Student ID: {student_id}",
            height=80
        ).pack(fill="x")

        self.create_divider(main_frame).pack(fill="x", pady=(0, 12))

        # Personal information.
        personal_frame = ttk.LabelFrame(
            main_frame,
            text="Personal Information",
            padding=12,
            style="MH.TLabelframe"
        )
        personal_frame.pack(fill="x", pady=(0, 10))

        personal_details = [
            ("First Name", student.get("first_name", "N/A")),
            ("Last Name", student.get("last_name", "N/A")),
            ("Email", student.get("email") or "Not provided"),
            ("Gender", student.get("gender") or "Not provided"),
            ("Grade Level", student.get("grade_level", "N/A")),
            ("Parent Contact", student.get("parent_contact") or "Not provided"),
            ("Date of Birth", student.get("date_of_birth") or "Not provided")
        ]

        for index, (label, value) in enumerate(personal_details):

            row = index // 2
            column = (index % 2) * 2

            ttk.Label(
                personal_frame,
                text=f"{label}:",
                style="MH.CardBold.TLabel"
            ).grid(
                row=row,
                column=column,
                sticky="w",
                padx=10,
                pady=4
            )

            ttk.Label(
                personal_frame,
                text=str(value),
                style="MH.Card.TLabel"
            ).grid(
                row=row,
                column=column + 1,
                sticky="w",
                padx=10,
                pady=4
            )

        # The Close button and the report section are packed to the bottom
        # BEFORE the academic table, so they are always visible when the
        # popup opens. The academic table takes whatever space is left.
        ttk.Button(
            main_frame,
            text="Close",
            command=popup.destroy,
            style="MH.TButton"
        ).pack(side="bottom", anchor="e")

        report_frame = ttk.LabelFrame(
            main_frame,
            text="Generate Student Report",
            padding=12,
            style="MH.TLabelframe"
        )
        report_frame.pack(side="bottom", fill="x", pady=(10, 10))

        ttk.Label(
            report_frame,
            text="Academic Year:",
            style="MH.CardBold.TLabel"
        ).grid(row=0, column=0, padx=5, pady=5)

        year_entry = ttk.Entry(report_frame, width=15, style="MH.TEntry")
        year_entry.grid(row=0, column=1, padx=5, pady=5)
        year_entry.insert(0, "2026")

        ttk.Label(
            report_frame,
            text="Academic Term:",
            style="MH.CardBold.TLabel"
        ).grid(row=0, column=2, padx=5, pady=5)

        term_combo = ttk.Combobox(
            report_frame,
            values=("Term 1", "Term 2", "Term 3"),
            state="readonly",
            width=15,
            style="MH.TCombobox"
        )
        term_combo.grid(row=0, column=3, padx=5, pady=5)
        term_combo.set("Term 1")

        ttk.Button(
            report_frame,
            text="Generate Report",
            style="MH.Pink.TButton",
            command=lambda: self.generate_student_report(
                popup,
                student_id,
                year_entry.get().strip(),
                term_combo.get().strip()
            )
        ).grid(row=0, column=4, padx=10, pady=5)

        # Academic records heading.
        ttk.Label(
            main_frame,
            text="Academic Records",
            style="MH.Subheading.TLabel"
        ).pack(anchor="w", pady=(2, 8))

        # Academic records table.
        academic_frame = ttk.Frame(main_frame, style="MH.TFrame")
        academic_frame.pack(fill="both", expand=True)

        columns = (
            "subject",
            "academic_year",
            "academic_term",
            "coursework",
            "project",
            "midterm",
            "final_exam",
            "average",
            "letter"
        )

        academic_table = ttk.Treeview(
            academic_frame,
            columns=columns,
            show="headings",
            height=5,
            style="MH.Treeview"
        )

        self.configure_row_tags(academic_table)

        headings = {
            "subject": "Subject",
            "academic_year": "Academic Year",
            "academic_term": "Term",
            "coursework": "Coursework",
            "project": "Project",
            "midterm": "Midterm",
            "final_exam": "Final Exam",
            "average": "Average",
            "letter": "Grade"
        }

        widths = {
            "subject": 140,
            "academic_year": 100,
            "academic_term": 90,
            "coursework": 85,
            "project": 75,
            "midterm": 75,
            "final_exam": 85,
            "average": 80,
            "letter": 60
        }

        for column in columns:
            academic_table.heading(column, text=headings[column])
            academic_table.column(
                column,
                width=widths[column],
                anchor="center"
            )

        academic_scrollbar = ttk.Scrollbar(
            academic_frame,
            orient="vertical",
            command=academic_table.yview,
            style="MH.Vertical.TScrollbar"
        )

        academic_table.configure(
            yscrollcommand=academic_scrollbar.set
        )

        academic_table.pack(side="left", fill="both", expand=True)
        academic_scrollbar.pack(side="right", fill="y")

        self.load_student_grades(academic_table, student_id)

    # Retrieves and displays the student's academic records.
    def load_student_grades(self, academic_table, student_id):

        try:
            grades = self.grade_service.get_grades_by_student(student_id)

            for index, grade in enumerate(grades):

                subject = self.subject_service.get_subject_by_id(
                    grade["subject_id"]
                )

                subject_name = (
                    subject.get("subject_name", "Unknown Subject")
                    if subject else "Unknown Subject"
                )

                average = self.grade_service.calculate_final_grade(grade)

                letter_grade, _performance = (
                    self.grade_service.get_grade_classification(average)
                )

                # Row stripe plus a colour for top and failing grades.
                tags = ["even" if index % 2 == 0 else "odd"]

                first_letter = str(letter_grade).strip()[:1].upper()

                if first_letter == "A":
                    tags.append("grade_top")
                elif first_letter == "F":
                    tags.append("grade_low")

                academic_table.insert(
                    "",
                    "end",
                    values=(
                        subject_name,
                        grade.get("academic_year", ""),
                        grade.get("academic_term", ""),
                        grade.get("coursework", ""),
                        grade.get("project", ""),
                        grade.get("midterm", ""),
                        grade.get("final_exam", ""),
                        average,
                        letter_grade
                    ),
                    tags=tuple(tags)
                )

            if not grades:
                academic_table.insert(
                    "",
                    "end",
                    values=(
                        "No academic records found.",
                        "", "", "", "", "", "", "", ""
                    )
                )

        except (ValueError, KeyError) as err:
            messagebox.showerror(
                "Academic Records",
                f"Unable to retrieve academic records:\n{err}"
            )

    # Generates a PDF report for the student.
    def generate_student_report(
        self,
        popup,
        student_id,
        academic_year,
        academic_term
    ):

        if not academic_year or not academic_term:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the academic year and select a term.",
                parent=popup
            )
            return

        try:
            report_data = self.report_service.prepare_report(
                student_id,
                academic_year,
                academic_term
            )

            if isinstance(report_data, str):
                messagebox.showerror(
                    "Report Error",
                    report_data,
                    parent=popup
                )
                return

            file_path = self.pdf_generator.generate_report(report_data)

            messagebox.showinfo(
                "Report Generated",
                f"Student report generated successfully!\n\n"
                f"Saved to:\n{file_path}",
                parent=popup
            )

        except Exception as err:
            messagebox.showerror(
                "Report Generation Error",
                f"Unable to generate student report:\n{err}",
                parent=popup
            )

    # Deletes a selected student.
    def delete_student(self):

        student = self.get_selected_student()

        if student is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete "
            f"{student.get('first_name', '')} "
            f"{student.get('last_name', '')}?"
        )

        if not confirm:
            return

        result = self.student_service.delete_student(
            student["person_id"]
        )

        if isinstance(result, str) and "successfully" in result.lower():
            messagebox.showinfo("Success", result)
            self.load_students()
        else:
            messagebox.showerror("Error", str(result))
"""
if __name__ == "__main__":

    root = tk.Tk()
    root.title("Monster High Academy - Student Management")
    root.geometry("1100x720")
    root.configure(bg=THEME["bg_root"])

    student_service = StudentService()
    teacher_service = TeacherService()
    subject_service = SubjectService(teacher_service)

    grade_service = GradeService(
        student_service,
        subject_service
    )

    report_service = ReportService(
        student_service,
        subject_service,
        grade_service
    )

    pdf_generator = PDFGenerator()

    StudentScreen(
        root,
        student_service,
        grade_service,
        subject_service,
        report_service,
        pdf_generator
    )

    root.mainloop()
    
"""