import tkinter as tk
from config.settings import THEME


class AdminDashboard:

    def __init__(self, root):

        # Store the main application window.
        self.root = root

        # Configure the dashboard window.
        self.root.title("Monster High Academy | Administrator Dashboard")
        #window size
        self.root.geometry("1100x700")
        self.root.configure(bg=THEME["bg_root"])
    
        def create_sidebar(self):
            pass 