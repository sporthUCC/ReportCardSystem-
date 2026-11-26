
import tkinter as tk
from config.settings import THEME


class AdminDashboard:

    def __init__(self, root):

        # Store the main application window.
        self.root = root

        # Configure the dashboard window.
        self.root.title("Monster High Academy | Administrator Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg=THEME["bg_root"])
<<<<<<< HEAD
    
        def create_sidebar(self):
            pass 
=======

        # Call methods to build the dashboard.
        self.create_sidebar()
        self.create_main_content()
        self.create_dashboard_heading()
        self.create_summary_cards()

    def create_sidebar(self):

        # Create the sidebar container.
        self.sidebar = tk.Frame(
            self.root,
            bg=THEME["bg_surface"],
            width=230
        )

        # Position the sidebar on the left side of the window.
        self.sidebar.pack(side="left", fill="y")

        # Prevent the sidebar from changing its set width.
        self.sidebar.pack_propagate(False)

    def create_main_content(self):

        # Create the main content area.
        self.main_content = tk.Frame(
            self.root,
            bg=THEME["bg_root"]
        )

        # Position the main content beside the sidebar.
        self.main_content.pack(
            side="left",
            fill="both",
            expand=True
        )

    def create_dashboard_heading(self):

        # Display the dashboard heading.
        self.heading = tk.Label(
            self.main_content,
            text="Admin Dashboard Overview",
            bg=THEME["bg_root"],
            fg=THEME["text_main"],
            font=("Georgia", 24, "bold")
        )

        # Position the heading at the top of the main content area.
        self.heading.pack(
            anchor="w",
            padx=30,
            pady=25
        )

    def create_summary_cards(self):

        # Create a container to hold the summary cards.
        self.cards_container = tk.Frame(
            self.main_content,
            bg=THEME["bg_root"]
        )

        # Position the summary card container below the heading.
        self.cards_container.pack(
            fill="x",
            padx=15,
            pady=10
        )

        # Create the student summary card.
        self.student_card = tk.Frame(
            self.cards_container,
            bg=THEME["bg_surface"],
            width=190,
            height=110
        )

        # Position the student card inside the container.
        self.student_card.pack(
            side="left",
            padx=15,
            pady=10
        )

        # Keep the card at its specified width and height.
        self.student_card.pack_propagate(False)

        # Display the total number of students.
        self.student_count = tk.Label(
            self.student_card,
            text="120",
            bg=THEME["bg_surface"],
            fg=THEME["accent_pink"],
            font=("Georgia", 24, "bold")
        )

        self.student_count.pack(pady=(15, 0))

        # Display the description beneath the student count.
        self.student_label = tk.Label(
            self.student_card,
            text="Total Students",
            bg=THEME["bg_surface"],
            fg=THEME["text_main"],
            font=("Arial", 11)
        )

        self.student_label.pack(pady=5)


# Run the dashboard independently for testing.
if __name__ == "__main__":

    root = tk.Tk()
    app = AdminDashboard(root)
    root.mainloop()
>>>>>>> 9a1961309f21a2e74ade1b3f03624f647e4f3be2
