import math
import tkinter as tk
from tkinter import ttk, messagebox

from services.grade_service import GradeService
from config.settings import THEME


class GradeScreen:

    def __init__(self, parent, grade_service):

        self.parent = parent
        self.grade_service = grade_service

        # GradeService already has these services connected.
        self.student_service = grade_service.student_service
        self.subject_service = grade_service.subject_service

        self.all_grades = []
        self.all_students = []
        self.all_subjects = []

        self.apply_monster_high_theme()
        self.build_screen()
        self.load_dropdown_data()
        self.load_grades()

    # ------------------------------------------------------------------
    # Theme and decoration helpers
    # ------------------------------------------------------------------

    # Applies the same Monster High colours and fonts used on the other screens.
    def apply_monster_high_theme(self):

        style = ttk.Style(self.parent)
        style.theme_use("clam")

        self.parent.option_add(
            "*TCombobox*Listbox.background",
            THEME["bg_root"]
        )
        self.parent.option_add(
            "*TCombobox*Listbox.foreground",
            THEME["text_main"]
        )
        self.parent.option_add(
            "*TCombobox*Listbox.selectBackground",
            THEME["accent_pink"]
        )
        self.parent.option_add(
            "*TCombobox*Listbox.selectForeground",
            THEME["text_main"]
        )
        self.parent.option_add(
            "*TCombobox*Listbox.font",
            ("Georgia", 10)
        )

        style.configure(
            ".",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 10),
            bordercolor=THEME["text_purple"],
            focuscolor=THEME["accent_pink"]
        )

        style.configure("MH.TFrame", background=THEME["bg_root"])
        style.configure("MH.Card.TFrame", background=THEME["bg_surface"])

        style.configure(
            "MH.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 10)
        )

        style.configure(
            "MH.Heading.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 22, "bold")
        )

        style.configure(
            "MH.Subheading.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_purple"],
            font=("Georgia", 14, "bold")
        )

        style.configure(
            "MH.Card.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            font=("Georgia", 10)
        )

        style.configure(
            "MH.CardTitle.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            font=("Georgia", 18, "bold")
        )

        style.configure(
            "MH.CardMuted.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["text_purple"],
            font=("Georgia", 9)
        )

        style.configure(
            "MH.CardBold.TLabel",
            background=THEME["bg_surface"],
            foreground=THEME["accent_pink"],
            font=("Georgia", 9, "bold")
        )

        style.configure(
            "MH.TLabelframe",
            background=THEME["bg_surface"],
            bordercolor=THEME["accent_pink"],
            borderwidth=1,
            relief="solid"
        )

        style.configure(
            "MH.TLabelframe.Label",
            background=THEME["bg_surface"],
            foreground=THEME["text_purple"],
            font=("Georgia", 10, "bold")
        )

        style.configure(
            "MH.TButton",
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            bordercolor=THEME["text_purple"],
            font=("Georgia", 10, "bold"),
            padding=(8, 5)
        )

        style.map(
            "MH.TButton",
            background=[("active", THEME["text_purple"])],
            foreground=[("active", THEME["bg_root"])]
        )

        style.configure(
            "MH.Pink.TButton",
            background=THEME["accent_pink"],
            foreground=THEME["text_main"],
            bordercolor=THEME["accent_pink"],
            font=("Georgia", 10, "bold"),
            padding=(10, 5)
        )

        style.map(
            "MH.Pink.TButton",
            background=[("active", THEME["text_purple"])],
            foreground=[("active", THEME["bg_root"])]
        )

        style.configure(
            "MH.Cyan.TButton",
            background=THEME["bg_surface"],
            foreground=THEME["text_purple"],
            bordercolor=THEME["text_purple"],
            font=("Georgia", 10, "bold"),
            padding=(8, 5)
        )

        style.map(
            "MH.Cyan.TButton",
            background=[("active", THEME["text_purple"])],
            foreground=[("active", THEME["bg_root"])]
        )

        style.configure(
            "MH.TEntry",
            fieldbackground=THEME["bg_root"],
            foreground=THEME["text_main"],
            insertcolor=THEME["text_main"],
            bordercolor=THEME["text_purple"],
            padding=5
        )

        style.map(
            "MH.TEntry",
            fieldbackground=[("readonly", THEME["bg_surface"])],
            foreground=[("readonly", THEME["text_purple"])]
        )

        style.configure(
            "MH.TCombobox",
            fieldbackground=THEME["bg_root"],
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            arrowcolor=THEME["accent_pink"],
            bordercolor=THEME["text_purple"],
            padding=5
        )

        style.map(
            "MH.TCombobox",
            fieldbackground=[("readonly", THEME["bg_root"])],
            foreground=[("readonly", THEME["text_main"])],
            selectbackground=[("readonly", THEME["bg_root"])],
            selectforeground=[("readonly", THEME["text_main"])]
        )

        style.configure(
            "MH.Treeview",
            background=THEME["bg_surface"],
            fieldbackground=THEME["bg_surface"],
            foreground=THEME["text_main"],
            bordercolor=THEME["text_purple"],
            rowheight=28,
            font=("Georgia", 9)
        )

        style.configure(
            "MH.Treeview.Heading",
            background=THEME["bg_root"],
            foreground=THEME["text_purple"],
            bordercolor=THEME["accent_pink"],
            font=("Georgia", 9, "bold"),
            padding=(5, 5)
        )

        style.map(
            "MH.Treeview",
            background=[("selected", THEME["accent_pink"])],
            foreground=[("selected", THEME["text_main"])]
        )

        style.map(
            "MH.Treeview.Heading",
            background=[("active", THEME["accent_pink"])],
            foreground=[("active", THEME["text_main"])]
        )

        # Keeps the table row colours working on newer Tk versions.
        def fixed_map(option):

            return [
                elm for elm in style.map(
                    "MH.Treeview",
                    query_opt=option
                )
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
            arrowcolor=THEME["accent_pink"]
        )

        style.configure(
            "MH.Horizontal.TScrollbar",
            background=THEME["bg_surface"],
            troughcolor=THEME["bg_root"],
            bordercolor=THEME["text_purple"],
            arrowcolor=THEME["accent_pink"]
        )

    # Draws the same spiderweb banner used on the other screens.
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

            canvas.create_rectangle(
                0, 0, width, height,
                fill=THEME["bg_surface"],
                outline=""
            )

            radius = int(70 * scale)

            # Draws a spiderweb in each corner.
            def draw_web(corner_x, direction):

                for angle in (0, 22, 45, 68, 90):

                    canvas.create_line(
                        corner_x, 0,
                        corner_x + direction * radius *
                        math.cos(math.radians(angle)),
                        radius * math.sin(math.radians(angle)),
                        fill=THEME["text_purple"]
                    )

                for ring in range(1, 5):

                    r = int(radius * ring / 4)

                    if direction == 1:

                        canvas.create_arc(
                            corner_x - r, -r,
                            corner_x + r, r,
                            start=270,
                            extent=90,
                            style="arc",
                            outline=THEME["text_purple"]
                        )

                    else:

                        canvas.create_arc(
                            corner_x - r, -r,
                            corner_x + r, r,
                            start=180,
                            extent=90,
                            style="arc",
                            outline=THEME["text_purple"]
                        )

            draw_web(0, 1)
            draw_web(width, -1)

            text_x = int(radius * 0.6) + 24

            title_y = (
                int(height * 0.42)
                if subtitle else int(height / 2)
            )

            canvas.create_text(
                text_x, title_y,
                text=title,
                anchor="w",
                fill=THEME["text_main"],
                font=(
                    "Georgia",
                    max(int(22 * scale), 14),
                    "bold"
                )
            )

            if subtitle:

                canvas.create_text(
                    text_x, int(height * 0.76),
                    text=subtitle,
                    anchor="w",
                    fill=THEME["text_purple"],
                    font=("Georgia", 10, "italic")
                )

            canvas.create_rectangle(
                0, height - 3, width, height,
                fill=THEME["accent_pink"],
                outline=""
            )

        canvas.bind(
            "<Configure>",
            lambda event: draw(event.width)
        )

        return canvas

    # Creates the pink divider line.
    def create_divider(self, parent):

        return tk.Frame(
            parent,
            height=2,
            bg=THEME["accent_pink"]
        )

    # Centres popups on the screen.
    def center_popup(self, popup, width, height):

        popup.update_idletasks()

        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        width = min(width, screen_width - 60)
        height = min(height, screen_height - 100)

        x = (screen_width - width) // 2
        y = max((screen_height - height) // 2 - 20, 10)

        popup.geometry(f"{width}x{height}+{x}+{y}")

    # Adds alternating colours to the table rows.
    def configure_row_tags(self, table):

        table.tag_configure(
            "even",
            background=THEME["bg_surface"]
        )

        table.tag_configure(
            "odd",
            background=THEME["bg_root"]
        )

    # ------------------------------------------------------------------
    # Main screen
    # ------------------------------------------------------------------

    # Builds the grade management screen.
    def build_screen(self):

        self.main_frame = ttk.Frame(
            self.parent,
            padding=15,
            style="MH.TFrame"
        )

        self.main_frame.pack(fill="both", expand=True)

        self.create_banner(
            self.main_frame,
            "Grade Management",
            "Monster High Academy student assessment records",
            height=80
        ).pack(fill="x")

        self.create_divider(
            self.main_frame
        ).pack(fill="x", pady=(0, 10))

        # The bottom frame keeps the action buttons visible.
        self.button_frame = ttk.Frame(
            self.main_frame,
            style="MH.TFrame"
        )

        self.button_frame.pack(
            side="bottom",
            fill="x",
            pady=(10, 0)
        )

        ttk.Button(
            self.button_frame,
            text="Add Grade",
            command=self.open_add_grade,
            style="MH.Pink.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            self.button_frame,
            text="Edit Grade",
            command=self.edit_grade,
            style="MH.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            self.button_frame,
            text="Delete Grade",
            command=self.delete_grade,
            style="MH.TButton"
        ).pack(side="left", padx=4)

        ttk.Button(
            self.button_frame,
            text="Refresh",
            command=self.refresh_data,
            style="MH.Cyan.TButton"
        ).pack(side="right", padx=4)

        # The table uses the space left between the banner and buttons.
        table_frame = ttk.Frame(
            self.main_frame,
            style="MH.TFrame"
        )

        table_frame.pack(
            side="top",
            fill="both",
            expand=True
        )

        # Student ID is now displayed separately from the student's name.
        columns = (
            "grade_id",
            "student_id",
            "student",
            "subject",
            "academic_year",
            "academic_term",
            "coursework",
            "project",
            "midterm",
            "final_exam",
            "final_grade",
            "letter_grade"
        )

        self.grade_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="MH.Treeview"
        )

        headings = {
            "grade_id": "Grade ID",
            "student_id": "Student ID",
            "student": "Student Name",
            "subject": "Subject",
            "academic_year": "Year",
            "academic_term": "Term",
            "coursework": "Coursework",
            "project": "Project",
            "midterm": "Midterm",
            "final_exam": "Final Exam",
            "final_grade": "Final Grade",
            "letter_grade": "Letter"
        }

        widths = {
            "grade_id": 85,
            "student_id": 90,
            "student": 150,
            "subject": 130,
            "academic_year": 70,
            "academic_term": 80,
            "coursework": 85,
            "project": 75,
            "midterm": 75,
            "final_exam": 85,
            "final_grade": 90,
            "letter_grade": 65
        }

        for column in columns:

            self.grade_table.heading(
                column,
                text=headings[column]
            )

            self.grade_table.column(
                column,
                width=widths[column],
                anchor="center",
                stretch=False
            )

        self.configure_row_tags(self.grade_table)

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.grade_table.yview,
            style="MH.Vertical.TScrollbar"
        )

        horizontal_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.grade_table.xview,
            style="MH.Horizontal.TScrollbar"
        )

        self.grade_table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )

        self.grade_table.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Loading records
    # ------------------------------------------------------------------

    # Loads students and subjects for the dropdown lists.
    def load_dropdown_data(self):

        try:

            self.all_students = (
                self.student_service.get_all_students()
            )

            self.all_subjects = (
                self.subject_service.get_all_subjects()
            )

        except Exception as err:

            messagebox.showerror(
                "Loading Error",
                f"Unable to load student or subject records:\n{err}"
            )

    # Loads all grade records.
    def load_grades(self):

        try:

            self.all_grades = self.grade_service.get_all_grades()

            self.display_grades(self.all_grades)

        except Exception as err:

            messagebox.showerror(
                "Loading Error",
                f"Unable to load grades:\n{err}"
            )

    # Refreshes the dropdown data and grade table.
    def refresh_data(self):

        self.load_dropdown_data()
        self.load_grades()

    # Gets the student's full name using the student ID.
    def get_student_name(self, student_id):

        for student in self.all_students:

            if student.get("person_id") == student_id:

                return (
                    student.get("first_name", "")
                    + " "
                    + student.get("last_name", "")
                ).strip()

        return student_id

    # Gets the subject name using the subject ID.
    def get_subject_name(self, subject_id):

        for subject in self.all_subjects:

            if subject.get("subject_id") == subject_id:

                return subject.get("subject_name", "")

        return subject_id

    # Displays grade records in the table.
    def display_grades(self, grades):

        for item in self.grade_table.get_children():
            self.grade_table.delete(item)

        for index, grade in enumerate(grades):

            final_grade = self.grade_service.calculate_final_grade(
                grade
            )

            letter_grade, performance = (
                self.grade_service.get_grade_classification(
                    final_grade
                )
            )

            student_name = self.get_student_name(
                grade.get("student_id")
            )

            subject_name = self.get_subject_name(
                grade.get("subject_id")
            )

            values = (
                grade.get("grade_id", ""),
                grade.get("student_id", ""),
                student_name,
                subject_name,
                grade.get("academic_year", ""),
                grade.get("academic_term", ""),
                grade.get("coursework", ""),
                grade.get("project", ""),
                grade.get("midterm", ""),
                grade.get("final_exam", ""),
                f"{final_grade:.2f}%",
                letter_grade
            )

            # Alternates the row colours.
            row_tag = "even" if index % 2 == 0 else "odd"

            self.grade_table.insert(
                "",
                "end",
                values=values,
                tags=(row_tag,)
            )

    # Gets the selected grade record.
    def get_selected_grade(self):

        selected_item = self.grade_table.selection()

        if not selected_item:

            messagebox.showwarning(
                "No Selection",
                "Please select a grade record first."
            )

            return None

        grade_id = self.grade_table.item(
            selected_item[0],
            "values"
        )[0]

        # Finds the selected record in the loaded grade list.
        for grade in self.all_grades:

            if grade.get("grade_id") == grade_id:
                return grade

        return None

    # ------------------------------------------------------------------
    # Add grade
    # ------------------------------------------------------------------

    # Opens the form for adding a grade.
    def open_add_grade(self):

        self.load_dropdown_data()

        if not self.all_students:

            messagebox.showwarning(
                "No Students",
                "Please add students before entering grades."
            )
            return

        if not self.all_subjects:

            messagebox.showwarning(
                "No Subjects",
                "Please add subjects before entering grades."
            )
            return

        self.open_grade_form("Add Student Grade")

    # ------------------------------------------------------------------
    # Edit grade
    # ------------------------------------------------------------------

    # Opens the form for editing a selected grade.
    def edit_grade(self):

        grade = self.get_selected_grade()

        if grade is None:
            return

        self.load_dropdown_data()

        self.open_grade_form(
            "Edit Student Grade",
            grade
        )

    # ------------------------------------------------------------------
    # Grade form
    # ------------------------------------------------------------------

    # Creates the form used to add or edit a grade.
    def open_grade_form(self, title, grade=None):

        popup = tk.Toplevel(self.parent)

        popup.title(title)
        popup.resizable(False, False)

        popup.configure(
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )

        popup.transient(self.parent.winfo_toplevel())

        self.center_popup(popup, 500, 680)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=25,
            style="MH.Card.TFrame"
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        self.create_banner(
            main_frame,
            title,
            "Enter the student's assessment marks",
            height=70
        ).pack(fill="x")

        self.create_divider(
            main_frame
        ).pack(fill="x", pady=(0, 12))

        form_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )

        form_frame.pack(fill="both", expand=True)

        form_frame.grid_columnconfigure(1, weight=1)

        # Student dropdown.
        ttk.Label(
            form_frame,
            text="Student",
            style="MH.CardBold.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=7)

        student_values = []
        student_lookup = {}

        for student in self.all_students:

            student_id = student.get("person_id")

            student_name = (
                student.get("first_name", "")
                + " "
                + student.get("last_name", "")
            ).strip()

            # Adds a small distinction if two students have the same name.
            display_name = student_name

            if display_name in student_lookup:
                display_name = f"{student_name} (2)"

            student_values.append(display_name)
            student_lookup[display_name] = student_id

        student_combo = ttk.Combobox(
            form_frame,
            values=student_values,
            state="readonly",
            width=30,
            style="MH.TCombobox"
        )

        student_combo.grid(
            row=0, column=1, sticky="ew", pady=7
        )

        # Subject dropdown.
        ttk.Label(
            form_frame,
            text="Subject",
            style="MH.CardBold.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=7)

        subject_values = []
        subject_lookup = {}

        for subject in self.all_subjects:

            subject_id = subject.get("subject_id")
            subject_name = subject.get("subject_name", "")

            # Keeps the subject ID internally while displaying the name.
            display_name = subject_name

            if display_name in subject_lookup:
                display_name = f"{subject_name} (2)"

            subject_values.append(display_name)
            subject_lookup[display_name] = subject_id

        subject_combo = ttk.Combobox(
            form_frame,
            values=subject_values,
            state="readonly",
            width=30,
            style="MH.TCombobox"
        )

        subject_combo.grid(
            row=1, column=1, sticky="ew", pady=7
        )

        # Academic year.
        ttk.Label(
            form_frame,
            text="Academic Year",
            style="MH.CardBold.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=7)

        year_entry = ttk.Entry(
            form_frame,
            width=32,
            style="MH.TEntry"
        )

        year_entry.grid(
            row=2, column=1, sticky="ew", pady=7
        )

        # Academic term.
        ttk.Label(
            form_frame,
            text="Academic Term",
            style="MH.CardBold.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=7)

        term_combo = ttk.Combobox(
            form_frame,
            values=("Term 1", "Term 2", "Term 3"),
            state="readonly",
            width=30,
            style="MH.TCombobox"
        )

        term_combo.grid(
            row=3, column=1, sticky="ew", pady=7
        )

        # Assessment marks.
        mark_entries = {}

        assessments = (
            ("Coursework", "coursework"),
            ("Project", "project"),
            ("Midterm", "midterm"),
            ("Final Exam", "final_exam")
        )

        for row, (label, field) in enumerate(assessments, start=4):

            ttk.Label(
                form_frame,
                text=label,
                style="MH.CardBold.TLabel"
            ).grid(
                row=row,
                column=0,
                sticky="w",
                pady=7
            )

            entry = ttk.Entry(
                form_frame,
                width=32,
                style="MH.TEntry"
            )

            entry.grid(
                row=row,
                column=1,
                sticky="ew",
                pady=7
            )

            mark_entries[field] = entry

        # Fills the fields when editing an existing grade.
        if grade:

            student_id = grade.get("student_id")
            subject_id = grade.get("subject_id")

            for display_name, saved_id in student_lookup.items():

                if saved_id == student_id:
                    student_combo.set(display_name)
                    break

            for display_name, saved_id in subject_lookup.items():

                if saved_id == subject_id:
                    subject_combo.set(display_name)
                    break

            # Student and subject cannot be changed when editing.
            student_combo.configure(state="disabled")
            subject_combo.configure(state="disabled")

            year_entry.insert(
                0,
                str(grade.get("academic_year", ""))
            )

            term_combo.set(
                grade.get("academic_term", "")
            )

            for field, entry in mark_entries.items():

                entry.insert(
                    0,
                    str(grade.get(field, ""))
                )

        else:

            year_entry.insert(0, "2026")

        ttk.Label(
            main_frame,
            text="Enter marks between 0 and 100.",
            style="MH.CardMuted.TLabel"
        ).pack(anchor="w", pady=(10, 5))

        # Saves the grade information.
        def save_grade():

            academic_year = year_entry.get().strip()
            academic_term = term_combo.get().strip()

            if not academic_year or not academic_term:

                messagebox.showwarning(
                    "Missing Information",
                    "Please enter the academic year and term.",
                    parent=popup
                )
                return

            if not grade:

                if not student_combo.get() or not subject_combo.get():

                    messagebox.showwarning(
                        "Missing Information",
                        "Please select a student and subject.",
                        parent=popup
                    )
                    return

            try:

                marks = {}

                for field, entry in mark_entries.items():

                    value = entry.get().strip()

                    if not value:
                        raise ValueError(
                            f"Please enter the {field.replace('_', ' ')} mark."
                        )

                    marks[field] = float(value)

                    if marks[field] < 0 or marks[field] > 100:
                        raise ValueError(
                            "Assessment marks must be between 0 and 100."
                        )

                if grade:

                    update_data = {
                        "academic_year": academic_year,
                        "academic_term": academic_term,
                        **marks
                    }

                    result = self.grade_service.update_grade(
                        grade.get("grade_id"),
                        update_data
                    )

                else:

                    student_id = student_lookup[
                        student_combo.get()
                    ]

                    subject_id = subject_lookup[
                        subject_combo.get()
                    ]

                    result = self.grade_service.add_grade(
                        student_id,
                        subject_id,
                        academic_year,
                        academic_term,
                        marks["coursework"],
                        marks["project"],
                        marks["midterm"],
                        marks["final_exam"]
                    )

                if "successfully" in str(result).lower():

                    messagebox.showinfo(
                        "Success",
                        result,
                        parent=popup
                    )

                    popup.destroy()
                    self.refresh_data()

                else:

                    messagebox.showerror(
                        "Error",
                        result,
                        parent=popup
                    )

            except (ValueError, KeyError) as err:

                messagebox.showerror(
                    "Invalid Information",
                    str(err),
                    parent=popup
                )

        # Form buttons.
        button_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )

        button_frame.pack(
            fill="x",
            pady=(12, 0)
        )

        ttk.Button(
            button_frame,
            text="Save Grade",
            command=save_grade,
            style="MH.Pink.TButton"
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            style="MH.TButton"
        ).pack(side="left")

    # ------------------------------------------------------------------
    # Delete grade
    # ------------------------------------------------------------------

    # Deletes the selected grade record.
    def delete_grade(self):

        grade = self.get_selected_grade()

        if grade is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete grade "
            f"{grade.get('grade_id')}?"
        )

        if not confirm:
            return

        result = self.grade_service.delete_grade(
            grade.get("grade_id")
        )

        if "successfully" in str(result).lower():

            messagebox.showinfo(
                "Success",
                result
            )

            self.refresh_data()

        else:

            messagebox.showerror(
                "Delete Error",
                result
            )


# Allows the screen to be tested on its own.
if __name__ == "__main__":

    from services.student_service import StudentService
    from services.teacher_service import TeacherService
    from services.subject_service import SubjectService

    root = tk.Tk()

    root.title("Monster High Academy - Grade Management")
    root.geometry("1200x720")
    root.minsize(850, 500)
    root.configure(bg=THEME["bg_root"])

    student_service = StudentService()

    teacher_service = TeacherService()

    subject_service = SubjectService(
        teacher_service
    )

    grade_service = GradeService(
        student_service,
        subject_service
    )

    GradeScreen(
        root,
        grade_service
    )

    root.mainloop()