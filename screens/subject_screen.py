import tkinter as tk
from tkinter import ttk, messagebox

from services.subject_service import SubjectService
from services.teacher_service import TeacherService
from config.settings import THEME


class SubjectScreen:
    """
    Handles the Subject Management page for Monster High Academy.
    Lets the admin view all subjects, see who is teaching each one,
    and add, edit, or delete subject records.
    """

    def __init__(self, parent, subject_service, teacher_service):
        self.parent = parent
        self.subject_service = subject_service
        self.teacher_service = teacher_service

        # Keeping both lists cached on self so we don't keep hitting the JSON files
        # every time the table redraws or a popup opens.
        self.all_subjects = []
        self.teachers = []

        self.apply_monster_high_theme()
        self.build_screen()
        self.load_subjects()

    def apply_monster_high_theme(self):
        """
        Configures all the Monster High colours and Georgia fonts for ttk widgets.
        Using 'clam' because the default Windows theme ignores custom background
        and border colours on buttons and table headers.
        """
        style = ttk.Style(self.parent)
        style.theme_use("clam")

        """
        The dropdown list inside a ttk.Combobox is actually a classic Tk Listbox
        under the hood, so style.configure won't touch it—have to use option_add.
        """
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

        # Base fallback styling for any ttk widget that doesn't get a custom style name
        style.configure(
            ".",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 10),
            bordercolor=THEME["text_purple"],
            focuscolor=THEME["accent_pink"]
        )

        style.configure(
            "MH.TFrame",
            background=THEME["bg_root"]
        )

        # Slightly lighter surface colour used inside popups so they stand out from the main window
        style.configure(
            "MH.Card.TFrame",
            background=THEME["bg_surface"]
        )

        style.configure(
            "MH.TLabel",
            background=THEME["bg_root"],
            foreground=THEME["text_main"],
            font=("Georgia", 10)
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

        # Pink bold labels make required form fields easier to spot
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

        # Primary action button style (Add / Save)
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

        style.configure(
            "MH.TCombobox",
            fieldbackground=THEME["bg_root"],
            background=THEME["bg_surface"],
            foreground=THEME["text_main"],
            arrowcolor=THEME["accent_pink"],
            bordercolor=THEME["text_purple"],
            padding=5
        )

        # Stops the combobox from turning bright white/blue when readonly is selected
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

        style.configure(
            "MH.Vertical.TScrollbar",
            background=THEME["bg_surface"],
            troughcolor=THEME["bg_root"],
            bordercolor=THEME["text_purple"],
            arrowcolor=THEME["accent_pink"]
        )

    def create_banner(self, parent, title, subtitle="", height=90):
        """
        Draws a custom header banner with spiderweb corners and a pink bottom accent.
        Built on a Canvas so it stretches cleanly whenever the window resizes.
        """
        canvas = tk.Canvas(
            parent,
            height=height,
            bg=THEME["bg_surface"],
            highlightthickness=0
        )

        def draw(width):

            import math

            # Clear old drawings first so resizing doesn't stack duplicate lines
            canvas.delete("all")

            canvas.create_rectangle(
                0, 0, width, height,
                fill=THEME["bg_surface"],
                outline=""
            )

            # Scale the web radius to the banner height so smaller popup banners stay proportional
            radius = int(70 * height / 90)

            def draw_web(corner_x, direction):
                # Spoke lines radiating out from the top corner
                for angle in (0, 22, 45, 68, 90):

                    canvas.create_line(
                        corner_x,
                        0,
                        corner_x + direction * radius *
                        math.cos(math.radians(angle)),
                        radius * math.sin(math.radians(angle)),
                        fill=THEME["text_purple"]
                    )

                # Curved rings connecting the spokes; start angle flips for the right corner
                for ring in range(1, 5):

                    r = int(radius * ring / 4)

                    canvas.create_arc(
                        corner_x - r,
                        -r,
                        corner_x + r,
                        r,
                        start=270 if direction == 1 else 180,
                        extent=90,
                        style="arc",
                        outline=THEME["text_purple"]
                    )

            draw_web(0, 1)
            draw_web(width, -1)

            # Push the title slightly past the left web so the text never overlaps the lines
            text_x = int(radius * 0.6) + 24
            title_y = int(height * 0.42) if subtitle else height / 2

            canvas.create_text(
                text_x,
                title_y,
                text=title,
                anchor="w",
                fill=THEME["text_main"],
                font=("Georgia", max(int(22 * height / 90), 14), "bold")
            )

            if subtitle:

                canvas.create_text(
                    text_x,
                    int(height * 0.76),
                    text=subtitle,
                    anchor="w",
                    fill=THEME["text_purple"],
                    font=("Georgia", 10, "italic")
                )

            # Thin pink accent bar along the bottom edge
            canvas.create_rectangle(
                0,
                height - 3,
                width,
                height,
                fill=THEME["accent_pink"],
                outline=""
            )

        canvas.bind(
            "<Configure>",
            lambda event: draw(event.width)
        )

        return canvas

    def create_divider(self, parent):
        # Thin pink strip used to separate the banner from the form or table below
        return tk.Frame(
            parent,
            height=2,
            bg=THEME["accent_pink"]
        )

    def center_popup(self, popup, width, height):
        """
        Calculates the middle of the user's monitor and moves the popup there.
        Also caps the width/height so popups don't clip off smaller laptop screens.
        """
        popup.update_idletasks()

        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        width = min(width, screen_width - 60)
        height = min(height, screen_height - 100)

        x = (screen_width - width) // 2
        y = max((screen_height - height) // 2 - 20, 10)  # nudged slightly up so it feels balanced

        popup.geometry(f"{width}x{height}+{x}+{y}")

    def configure_row_tags(self, table):
        # Alternating row colours make long tables way easier to scan across
        table.tag_configure(
            "even",
            background=THEME["bg_surface"]
        )

        table.tag_configure(
            "odd",
            background=THEME["bg_root"]
        )

    # ------------------------------------------------------------------
    # Main subject screen
    # ------------------------------------------------------------------

    def build_screen(self):
        """
        Sets up the main Subject Management layout: top banner, refresh button,
        bottom action bar, and the expanding Treeview table in the middle.
        """
        self.main_frame = ttk.Frame(
            self.parent,
            padding=20,
            style="MH.TFrame"
        )
        self.main_frame.pack(fill="both", expand=True)

        self.create_banner(
            self.main_frame,
            "Subject Management",
            "Monster High Academy subject records",
            height=90
        ).pack(fill="x")

        self.create_divider(
            self.main_frame
        ).pack(fill="x", pady=(0, 15))

        # Sits above the table on the right so the user can sync after adding teachers
        ttk.Button(
            self.main_frame,
            text="Refresh",
            command=self.load_subjects,
            style="MH.TButton"
        ).pack(
            anchor="e",
            pady=(0, 10)
        )

        """
        Packed with side='bottom' BEFORE the table so the buttons stay pinned
        at the bottom even when the window is resized smaller.
        """
        button_frame = ttk.Frame(
            self.main_frame,
            style="MH.TFrame"
        )
        button_frame.pack(
            side="bottom",
            fill="x",
            pady=15
        )

        ttk.Button(
            button_frame,
            text="Add Subject",
            command=self.open_add_subject,
            style="MH.Pink.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Edit Subject",
            command=self.edit_subject,
            style="MH.Cyan.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Delete Subject",
            command=self.delete_subject,
            style="MH.TButton"
        ).pack(side="left", padx=5)

        # Table container takes up all remaining vertical space
        table_frame = ttk.Frame(
            self.main_frame,
            style="MH.TFrame"
        )
        table_frame.pack(fill="both", expand=True)

        columns = (
            "subject_id",
            "subject_name",
            "teacher_name"
        )

        self.subject_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="MH.Treeview"
        )

        self.configure_row_tags(self.subject_table)

        self.subject_table.heading(
            "subject_id",
            text="Subject ID"
        )

        self.subject_table.heading(
            "subject_name",
            text="Subject Name"
        )

        self.subject_table.heading(
            "teacher_name",
            text="Assigned Teacher"
        )

        self.subject_table.column(
            "subject_id",
            width=130,
            anchor="center"
        )

        self.subject_table.column(
            "subject_name",
            width=250
        )

        self.subject_table.column(
            "teacher_name",
            width=250
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.subject_table.yview,
            style="MH.Vertical.TScrollbar"
        )

        self.subject_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.subject_table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

    # ------------------------------------------------------------------
    # Loading and displaying records
    # ------------------------------------------------------------------

    def load_teachers(self):
        # Pulls fresh teacher records so we can match teacher_id to a real name
        try:
            self.teachers = self.teacher_service.get_all_teachers()
            return self.teachers

        except Exception as err:
            messagebox.showerror(
                "Teacher Records",
                f"Unable to load teachers:\n{err}"
            )
            return []

    def get_teacher_name(self, teacher_id):
        """
        Subjects only store teacher_id in JSON, so this looks up the teacher's
        first and last name to show something readable in the table.
        """
        for teacher in self.teachers:

            if teacher.get("person_id") == teacher_id:

                full_name = (
                    f"{teacher.get('first_name', '')} "
                    f"{teacher.get('last_name', '')}"
                ).strip()

                return full_name or teacher_id

        return "Teacher not found"

    def load_subjects(self):
        # Loads teachers right before displaying subjects so assigned names stay up to date
        try:
            self.all_subjects = self.subject_service.get_all_subjects()

            self.load_teachers()
            self.display_subjects(self.all_subjects)

        except Exception as err:
            messagebox.showerror(
                "Error",
                f"Unable to load subjects:\n{err}"
            )

    def display_subjects(self, subjects):
        # Wipe existing rows first so refreshing doesn't duplicate everything
        for item in self.subject_table.get_children():
            self.subject_table.delete(item)

        for index, subject in enumerate(subjects):

            teacher_name = self.get_teacher_name(
                subject.get("teacher_id", "")
            )

            self.subject_table.insert(
                "",
                "end",
                values=(
                    subject.get("subject_id", ""),
                    subject.get("subject_name", ""),
                    teacher_name
                ),
                tags=("even" if index % 2 == 0 else "odd",)
            )

    def get_teacher_options(self):
        """
        Builds a dictionary mapping 'Full Name (ID)' -> 'ID' for the Combobox.
        Doing it this way avoids splitting strings later and handles teachers
        who happen to share the same name.
        """
        self.load_teachers()

        teacher_options = {}

        for teacher in self.teachers:

            teacher_id = teacher.get("person_id", "")

            full_name = (
                f"{teacher.get('first_name', '')} "
                f"{teacher.get('last_name', '')}"
            ).strip()

            if teacher_id and full_name:

                display_name = f"{full_name} ({teacher_id})"

                teacher_options[display_name] = teacher_id

        return teacher_options

    # ------------------------------------------------------------------
    # Add subject
    # ------------------------------------------------------------------

    def open_add_subject(self):
        """
        Opens a modal popup to register a new subject.
        Blocks the popup early if no teachers exist yet since every subject
        needs an assigned teacher.
        """
        teacher_options = self.get_teacher_options()

        if not teacher_options:

            messagebox.showwarning(
                "No Teachers Available",
                "Please add a teacher before registering a subject."
            )
            return

        popup = tk.Toplevel(self.parent)
        popup.title("Add New Subject")
        popup.resizable(False, False)

        popup.configure(
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )

        # Keeps the popup attached to the main window and locks clicks until closed
        popup.transient(self.parent.winfo_toplevel())

        self.center_popup(popup, 520, 330)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=25,
            style="MH.Card.TFrame"
        )
        main_frame.pack(fill="both", expand=True)

        self.create_banner(
            main_frame,
            "New Subject",
            "Enter the subject information below",
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

        # Subject name field.
        ttk.Label(
            form_frame,
            text="Subject Name *",
            style="MH.CardBold.TLabel"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=10
        )

        subject_name_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        subject_name_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=10
        )

        # Teacher dropdown.
        ttk.Label(
            form_frame,
            text="Assigned Teacher *",
            style="MH.CardBold.TLabel"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=10
        )

        teacher_combo = ttk.Combobox(
            form_frame,
            values=list(teacher_options.keys()),
            state="readonly",
            width=32,
            style="MH.TCombobox"
        )
        teacher_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=10
        )

        # Default to the first teacher so the dropdown isn't blank on open
        teacher_combo.current(0)

        ttk.Label(
            main_frame,
            text="* Both fields are required.",
            style="MH.CardMuted.TLabel"
        ).pack(
            anchor="w",
            pady=(12, 10)
        )

        def save_subject():

            subject_name = subject_name_entry.get().strip()
            selected_teacher = teacher_combo.get().strip()

            # Pass parent=popup so the alert doesn't pop behind the modal window
            if not subject_name or selected_teacher not in teacher_options:

                messagebox.showwarning(
                    "Missing Information",
                    "Please enter a subject name and select a teacher.",
                    parent=popup
                )
                return

            teacher_id = teacher_options[selected_teacher]

            result = self.subject_service.add_subject(
                subject_name,
                teacher_id
            )

            if result == "Subject added successfully.":

                messagebox.showinfo(
                    "Success",
                    result,
                    parent=popup
                )

                self.load_subjects()
                popup.destroy()

            else:

                messagebox.showerror(
                    "Registration Error",
                    result,
                    parent=popup
                )

        # Buttons for saving or cancelling the form.
        button_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )
        button_frame.pack(
            fill="x",
            pady=(10, 0)
        )

        ttk.Button(
            button_frame,
            text="Save Subject",
            command=save_subject,
            style="MH.Pink.TButton"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            style="MH.TButton"
        ).pack(side="left")

        # Put cursor straight into the text box so the admin can start typing right away
        subject_name_entry.focus_set()

    # ------------------------------------------------------------------
    # Selecting a subject
    # ------------------------------------------------------------------

    def get_selected_subject(self):
        """
        Grabs the currently highlighted row from the Treeview and fetches
        the full subject dictionary from SubjectService.
        """
        selected_item = self.subject_table.selection()

        if not selected_item:

            messagebox.showwarning(
                "No Selection",
                "Please select a subject first."
            )
            return None

        subject_id = self.subject_table.item(
            selected_item[0],
            "values"
        )[0]

        try:
            return self.subject_service.get_subject_by_id(subject_id)

        except ValueError as err:

            messagebox.showerror(
                "Error",
                str(err)
            )
            return None

    # ------------------------------------------------------------------
    # Edit subject
    # ------------------------------------------------------------------

    def edit_subject(self):
        """
        Opens the edit modal pre-filled with the selected subject's details.
        Subject ID stays readonly so existing grade records don't lose their link.
        """
        subject = self.get_selected_subject()

        if subject is None:
            return

        teacher_options = self.get_teacher_options()

        if not teacher_options:

            messagebox.showwarning(
                "No Teachers Available",
                "There are no teacher records available."
            )
            return

        popup = tk.Toplevel(self.parent)
        popup.title("Edit Subject")
        popup.resizable(False, False)

        popup.configure(
            bg=THEME["bg_surface"],
            highlightbackground=THEME["accent_pink"],
            highlightthickness=2
        )

        popup.transient(self.parent.winfo_toplevel())

        self.center_popup(popup, 520, 390)
        popup.grab_set()

        main_frame = ttk.Frame(
            popup,
            padding=25,
            style="MH.Card.TFrame"
        )
        main_frame.pack(fill="both", expand=True)

        self.create_banner(
            main_frame,
            "Edit Subject",
            "Update the subject information below",
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

        # Insert the ID first, then lock the Entry to readonly so the user can see it but not edit it
        ttk.Label(
            form_frame,
            text="Subject ID",
            style="MH.CardBold.TLabel"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=10
        )

        subject_id_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        subject_id_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=10
        )

        subject_id_entry.insert(
            0,
            subject.get("subject_id", "")
        )

        subject_id_entry.configure(state="readonly")

        # Displays the current subject name.
        ttk.Label(
            form_frame,
            text="Subject Name *",
            style="MH.CardBold.TLabel"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=10
        )

        subject_name_entry = ttk.Entry(
            form_frame,
            width=35,
            style="MH.TEntry"
        )
        subject_name_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=10
        )

        subject_name_entry.insert(
            0,
            subject.get("subject_name", "")
        )

        # Displays the available teachers.
        ttk.Label(
            form_frame,
            text="Assigned Teacher *",
            style="MH.CardBold.TLabel"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=10
        )

        teacher_combo = ttk.Combobox(
            form_frame,
            values=list(teacher_options.keys()),
            state="readonly",
            width=32,
            style="MH.TCombobox"
        )
        teacher_combo.grid(
            row=2,
            column=1,
            sticky="ew",
            pady=10
        )

        # Match the stored teacher_id back to its formatted dropdown label
        current_teacher_id = subject.get("teacher_id", "")

        for teacher_name, teacher_id in teacher_options.items():

            if teacher_id == current_teacher_id:

                teacher_combo.set(teacher_name)
                break

        ttk.Label(
            main_frame,
            text="The subject ID cannot be changed.",
            style="MH.CardMuted.TLabel"
        ).pack(
            anchor="w",
            pady=(12, 10)
        )

        def save_changes():

            subject_name = subject_name_entry.get().strip()
            selected_teacher = teacher_combo.get().strip()

            if not subject_name or selected_teacher not in teacher_options:

                messagebox.showwarning(
                    "Missing Information",
                    "Please enter a subject name and select a teacher.",
                    parent=popup
                )
                return

            update_data = {
                "subject_name": subject_name,
                "teacher_id": teacher_options[selected_teacher]
            }

            result = self.subject_service.update_subject(
                subject.get("subject_id"),
                update_data
            )

            if result == "Subject updated successfully.":

                messagebox.showinfo(
                    "Update Successful",
                    result,
                    parent=popup
                )

                self.load_subjects()
                popup.destroy()

            else:

                messagebox.showerror(
                    "Update Error",
                    result,
                    parent=popup
                )

        # Buttons for saving or cancelling the changes.
        button_frame = ttk.Frame(
            main_frame,
            style="MH.Card.TFrame"
        )
        button_frame.pack(
            fill="x",
            pady=(10, 0)
        )

        ttk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes,
            style="MH.Pink.TButton"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        ttk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            style="MH.TButton"
        ).pack(side="left")

        subject_name_entry.focus_set()

    # ------------------------------------------------------------------
    # Delete subject
    # ------------------------------------------------------------------

    def delete_subject(self):
        # Prompts for confirmation first so a misclick doesn't wipe a subject record
        subject = self.get_selected_subject()

        if subject is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete "
            f"{subject.get('subject_name', '')}?"
        )

        if not confirm:
            return

        result = self.subject_service.delete_subject(
            subject.get("subject_id")
        )

        if result == "Subject deleted successfully.":

            messagebox.showinfo(
                "Success",
                result
            )

            self.load_subjects()

        else:

            messagebox.showerror(
                "Delete Error",
                result
            )


# Standalone entry point so I can test the subject screen directly without logging in
if __name__ == "__main__":

    root = tk.Tk()
    root.title("Monster High Academy - Subject Management")
    root.geometry("1100x720")
    root.configure(bg=THEME["bg_root"])

    teacher_service = TeacherService()
    subject_service = SubjectService(teacher_service)

    SubjectScreen(
        root,
        subject_service,
        teacher_service
    )

    root.mainloop()