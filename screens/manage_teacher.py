
import math
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from services.teacher_service import TeacherService
from config.settings import THEME


class TeacherScreen:

    def __init__(self, parent, teacher_service):

        self.parent = parent
        self.teacher_service = teacher_service

        self.all_teachers = []

        self.apply_monster_high_theme()
        self.build_screen()
        self.load_teachers()

    # ------------------------------------------------------------------
    # Theme and decoration helpers
    # ------------------------------------------------------------------

    # Applies the same Monster High colours and fonts used on the other screens.
    def apply_monster_high_theme(self):

        style = ttk.Style(self.parent)
        style.theme_use("clam")

        # Dark dropdown lists for comboboxes
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
            padding=(12, 6)
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
            padding=(14, 6)
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
            padding=(12, 6)
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
            font=("Georgia", 10)
        )

        style.configure(
            "MH.Treeview.Heading",
            background=THEME["bg_root"],
            foreground=THEME["text_purple"],
            bordercolor=THEME["accent_pink"],
            font=("Georgia", 10, "bold"),
            padding=(8, 6)
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

        # Keeps the table row colours working on newer Tk versions
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

    # Draws the same spiderweb banner used on the student screen.
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

            # Pink line at the bottom of the banner.
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

    # Builds the teacher management screen.
    def build_screen(self):

        self.main_frame = ttk.Frame(
            self.parent,
            padding=20,
            style="MH.TFrame"
        )
        self.main_frame.pack(fill="both", expand=True)

        self.create_banner(
            self.main_frame,
            "Teacher Management",
            "Monster High Academy teacher records",
            height=90
        ).pack(fill="x")

        self.create_divider(
            self.main_frame
        ).pack(fill="x", pady=(0, 15))

        # Action buttons.
        button_frame = ttk.Frame(
            self.main_frame,
            style="MH.TFrame"
        )
        button_frame.pack(side="bottom", fill="x", pady=15)

        ttk.Button(
            button_frame,
            text="Add Teacher",
            command=self.open_add_teacher,
            style="MH.Pink.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Edit Teacher",
            command=self.edit_teacher,
            style="MH.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Delete Teacher",
            command=self.delete_teacher,
            style="MH.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.load_teachers,
            style="MH.Cyan.TButton"
        ).pack(side="left", padx=5)

        # Teacher table.
        table_frame = ttk.Frame(
            self.main_frame,
            style="MH.TFrame"
        )
        table_frame.pack(fill="both", expand=True)

        columns = (
            "teacher_id",
            "first_name",
            "last_name",
            "email",
            "subject_taught"
        )

        self.teacher_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="MH.Treeview"
        )

        self.configure_row_tags(self.teacher_table)

        self.teacher_table.heading(
            "teacher_id",
            text="Teacher ID"
        )
        self.teacher_table.heading(
            "first_name",
            text="First Name"
        )
        self.teacher_table.heading(
            "last_name",
            text="Last Name"
        )
        self.teacher_table.heading(
            "email",
            text="Email"
        )
        self.teacher_table.heading(
            "subject_taught",
            text="Subject Taught"
        )

        self.teacher_table.column(
            "teacher_id",
            width=110
        )
        self.teacher_table.column(
            "first_name",
            width=150
        )
        self.teacher_table.column(
            "last_name",
            width=150
        )
        self.teacher_table.column(
            "email",
            width=220
        )
        self.teacher_table.column(
            "subject_taught",
            width=180
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.teacher_table.yview,
            style="MH.Vertical.TScrollbar"
        )

        self.teacher_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.teacher_table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # ------------------------------------------------------------------
    # Teacher records
    # ------------------------------------------------------------------

    # Retrieves all teacher records.
    def load_teachers(self):

        try:

            self.all_teachers = (
                self.teacher_service.get_all_teachers()
            )

            self.display_teachers(self.all_teachers)

        except Exception as err:

            messagebox.showerror(
                "Error",
                f"Unable to load teachers:\n{err}"
            )

    # Displays teacher records in the table.
    def display_teachers(self, teachers):

        for item in self.teacher_table.get_children():
            self.teacher_table.delete(item)

        for index, teacher in enumerate(teachers):

            self.teacher_table.insert(
                "",
                "end",
                values=(
                    teacher.get("person_id", ""),
                    teacher.get("first_name", ""),
                    teacher.get("last_name", ""),
                    teacher.get("email") or "",
                    teacher.get("subject_taught", "")
                ),
                tags=(
                    "even" if index % 2 == 0 else "odd",
                )
            )

    # Gets the selected teacher from the table.
    def get_selected_teacher(self):

        selected_item = self.teacher_table.selection()

        if not selected_item:

            messagebox.showwarning(
                "No Selection",
                "Please select a teacher first."
            )

            return None

        teacher_id = self.teacher_table.item(
            selected_item[0],
            "values"
        )[0]

        try:

            return self.teacher_service.get_teacher_by_id(
                teacher_id
            )

        except ValueError as err:

            messagebox.showerror("Error", str(err))
            return None

    # ------------------------------------------------------------------
    # Add teacher
    # ------------------------------------------------------------------

    # Opens the teacher registration window.
    def open_add_teacher(self):

        popup = tk.Toplevel(self.parent)
        popup.title("Register New Teacher")
        popup.resizable(False, False)

        popup.configure(
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )

        popup.transient(self.parent.winfo_toplevel())

        self.center_popup(popup, 500, 590)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=25,
            style="MH.Card.TFrame"
        )
        main_frame.pack(fill="both", expand=True)

        self.create_banner(
            main_frame,
            "New Teacher",
            "Enter the teacher's information below",
            height=70
        ).pack(fill="x")

        self.create_divider(
            main_frame
        ).pack(fill="x", pady=(0, 15))

        form_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )
        form_frame.pack(fill="x")

        # First name.
        ttk.Label(
            form_frame,
            text="First Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=7)

        first_name_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        first_name_entry.grid(
            row=0, column=1, sticky="ew", pady=7
        )

        # Last name.
        ttk.Label(
            form_frame,
            text="Last Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=7)

        last_name_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        last_name_entry.grid(
            row=1, column=1, sticky="ew", pady=7
        )

        # Email.
        ttk.Label(
            form_frame,
            text="Email",
            style="MH.CardBold.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=7)

        email_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        email_entry.grid(
            row=2, column=1, sticky="ew", pady=7
        )

        # Subject taught.
        ttk.Label(
            form_frame,
            text="Subject Taught *",
            style="MH.CardBold.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=7)

        subject_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        subject_entry.grid(
            row=3, column=1, sticky="ew", pady=7
        )

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
        gender_combo.grid(
            row=4, column=1, sticky="ew", pady=7
        )

        # Date of birth.
        ttk.Label(
            form_frame,
            text="Date of Birth",
            style="MH.CardBold.TLabel"
        ).grid(row=5, column=0, sticky="w", pady=7)

        dob_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        dob_entry.grid(
            row=5, column=1, sticky="ew", pady=7
        )
        dob_entry.insert(0, "YYYY-MM-DD")

        ttk.Label(
            main_frame,
            text="* Required fields. Date format: YYYY-MM-DD",
            style="MH.CardMuted.TLabel"
        ).pack(anchor="w", pady=(12, 15))

        # Saves the teacher using TeacherService.
        def save_teacher():

            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            subject = subject_entry.get().strip()
            gender = gender_combo.get().strip()
            dob_text = dob_entry.get().strip()

            # Check the required fields.
            if not first_name or not last_name or not subject:

                messagebox.showwarning(
                    "Missing Information",
                    "Please complete the first name, last name "
                    "and subject taught.",
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
                        "Example: 1985-05-18",
                        parent=popup
                    )
                    return

            # Send the information to TeacherService.
            result = self.teacher_service.add_teacher(
                first_name,
                last_name,
                email or None,
                subject,
                gender or None,
                date_of_birth=dob
            )

            if result == "Teacher added successfully.":

                messagebox.showinfo(
                    "Registration Successful",
                    result,
                    parent=popup
                )

                self.load_teachers()
                popup.destroy()

            else:

                messagebox.showerror(
                    "Registration Error",
                    result,
                    parent=popup
                )

        # Form buttons.
        button_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            button_frame,
            text="Register Teacher",
            command=save_teacher,
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
    # Edit teacher
    # ------------------------------------------------------------------

    # Opens a form to edit the selected teacher.
    def edit_teacher(self):

        teacher = self.get_selected_teacher()

        if teacher is None:
            return

        popup = tk.Toplevel(self.parent)
        popup.title("Edit Teacher")
        popup.resizable(False, False)

        popup.configure(
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )

        popup.transient(self.parent.winfo_toplevel())

        self.center_popup(popup, 500, 630)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=25,
            style="MH.Card.TFrame"
        )
        main_frame.pack(fill="both", expand=True)

        self.create_banner(
            main_frame,
            "Edit Teacher",
            "Update the teacher's information below",
            height=70
        ).pack(fill="x")

        self.create_divider(
            main_frame
        ).pack(fill="x", pady=(0, 12))

        form_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )
        form_frame.pack(fill="x")

        # Teacher ID cannot be changed.
        ttk.Label(
            form_frame,
            text="Teacher ID",
            style="MH.CardBold.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=7)

        teacher_id_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        teacher_id_entry.grid(
            row=0, column=1, sticky="ew", pady=7
        )

        teacher_id_entry.insert(
            0,
            teacher.get("person_id", "")
        )
        teacher_id_entry.configure(state="readonly")

        # First name.
        ttk.Label(
            form_frame,
            text="First Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=7)

        first_name_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        first_name_entry.grid(
            row=1, column=1, sticky="ew", pady=7
        )
        first_name_entry.insert(
            0,
            teacher.get("first_name", "")
        )

        # Last name.
        ttk.Label(
            form_frame,
            text="Last Name *",
            style="MH.CardBold.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=7)

        last_name_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        last_name_entry.grid(
            row=2, column=1, sticky="ew", pady=7
        )
        last_name_entry.insert(
            0,
            teacher.get("last_name", "")
        )

        # Email.
        ttk.Label(
            form_frame,
            text="Email",
            style="MH.CardBold.TLabel"
        ).grid(row=3, column=0, sticky="w", pady=7)

        email_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        email_entry.grid(
            row=3, column=1, sticky="ew", pady=7
        )
        email_entry.insert(
            0,
            teacher.get("email") or ""
        )

        # Subject taught.
        ttk.Label(
            form_frame,
            text="Subject Taught *",
            style="MH.CardBold.TLabel"
        ).grid(row=4, column=0, sticky="w", pady=7)

        subject_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        subject_entry.grid(
            row=4, column=1, sticky="ew", pady=7
        )
        subject_entry.insert(
            0,
            teacher.get("subject_taught", "")
        )

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
        gender_combo.grid(
            row=5, column=1, sticky="ew", pady=7
        )
        gender_combo.set(teacher.get("gender") or "")

        # Date of birth.
        ttk.Label(
            form_frame,
            text="Date of Birth",
            style="MH.CardBold.TLabel"
        ).grid(row=6, column=0, sticky="w", pady=7)

        dob_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        dob_entry.grid(
            row=6, column=1, sticky="ew", pady=7
        )

        existing_dob = teacher.get("date_of_birth")

        if existing_dob:
            dob_entry.insert(0, str(existing_dob)[:10])

        ttk.Label(
            main_frame,
            text="* Required fields. Date format: YYYY-MM-DD",
            style="MH.CardMuted.TLabel"
        ).pack(anchor="w", pady=(12, 15))

        # Saves the updated teacher information.
        def save_changes():

            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            subject = subject_entry.get().strip()
            gender = gender_combo.get().strip()
            dob_text = dob_entry.get().strip()

            # Check the required fields.
            if not first_name or not last_name or not subject:

                messagebox.showwarning(
                    "Missing Information",
                    "Please complete the first name, last name "
                    "and subject taught.",
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
                        "Example: 1985-05-18",
                        parent=popup
                    )
                    return

            update_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email or None,
                "subject_taught": subject,
                "gender": gender or None,
                "date_of_birth": dob
            }

            result = self.teacher_service.update_teacher(
                teacher.get("person_id"),
                update_data
            )

            if result == "Teacher updated successfully.":

                messagebox.showinfo(
                    "Update Successful",
                    result,
                    parent=popup
                )

                self.load_teachers()
                popup.destroy()

            else:

                messagebox.showerror(
                    "Update Error",
                    result,
                    parent=popup
                )

        # Form buttons.
        button_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )
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

    # ------------------------------------------------------------------
    # Delete teacher
    # ------------------------------------------------------------------

    # Deletes the selected teacher.
    def delete_teacher(self):

        teacher = self.get_selected_teacher()

        if teacher is None:
            return

        teacher_name = (
            f"{teacher.get('first_name', '')} "
            f"{teacher.get('last_name', '')}"
        )

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {teacher_name}?"
        )

        if not confirm:
            return

        result = self.teacher_service.delete_teacher(
            teacher["person_id"]
        )

        if isinstance(result, str) and "successfully" in result.lower():

            messagebox.showinfo("Success", result)
            self.load_teachers()

        else:

            messagebox.showerror("Delete Error", str(result))


# Allows the screen to be tested on its own.
if __name__ == "__main__":

    root = tk.Tk()
    root.title("Monster High Academy - Teacher Management")
    root.geometry("1100x720")
    root.configure(bg=THEME["bg_root"])

    teacher_service = TeacherService()

    TeacherScreen(
        root,
        teacher_service
    )

    root.mainloop()
