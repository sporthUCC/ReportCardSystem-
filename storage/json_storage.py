
import json

"""
This file handles saving and retrieving student, grade, and subject data
in JSON format so that records can be accessed later.
"""

# Handles saving and retrieving data in JSON format
class JSONStorage:

    def __init__(self, file_path):
        self.file_path = file_path

    # Load data from a JSON file
    def load_data(self):
        try:
            with open(self.file_path, "r") as file:
                return json.load(file)

        # Handles if the file does not exist
        except FileNotFoundError:
            return []

        # Handles invalid JSON format
        except json.JSONDecodeError:
            return []

    # Opens the file in write mode and saves the data
    def save_data(self, data):
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)
