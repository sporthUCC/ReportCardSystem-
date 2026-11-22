from storage.json_storage import JSONStorage
from config.settings import ADMIN_FILE
# This administrator repository is responsible for saving the administrator records
class AdministratorRepository:
    def __init__(self):
        self.storage = JSONStorage(ADMIN_FILE)

    def add_administrator(self, administrator):
        administrators = self.storage.load_data()

        # Check for duplicate ID first
        for admin_data in administrators:
            if admin_data["person_id"] == administrator.get_person_id():
                raise ValueError("Administrator ID already exists")
            
        # Convert the Administrator object into a dictionary of its details
        admin_data = administrator.get_person_details()
        # Add the new administrator to the list
        administrators.append(admin_data)
        # Save the updated administrator records
        self.storage.save_data(administrators)

    def get_administrator_by_id(self, admin_id):
        administrators = self.storage.load_data()
        # Remove leading and trailing spaces
        admin_id = admin_id.strip()
        for admin_data in administrators:
            if admin_data["person_id"].upper() == admin_id.upper():
                return admin_data
        # Return None if no matching administrator is found
        return None

    def update_administrator(self, admin_id, update_data):
        administrators = self.storage.load_data()
        for admin_data in administrators:
            if admin_data["person_id"] == admin_id:
                # Update the administrator's first name if provided
                if "first_name" in update_data:
                    admin_data["first_name"] = update_data["first_name"]
                # Update the administrator's last name if provided
                if "last_name" in update_data:
                    admin_data["last_name"] = update_data["last_name"]
                # Update the administrator's email if provided
                if "email" in update_data:
                    admin_data["email"] = update_data["email"]
                # Update the administrator's access level if provided
                if "access_level" in update_data:
                    admin_data["access_level"] = update_data["access_level"]
                # Save the updated administrator records
                self.storage.save_data(administrators)
                return True
        # Return False if the administrator was not found
        return False

    def delete_administrator(self, admin_id):
        # Load all administrator records
        administrators = self.storage.load_data()
        for admin_data in administrators:
            # Compare the stored ID with the ID of the administrator to delete
            if admin_data["person_id"] == admin_id:
                administrators.remove(admin_data)
                self.storage.save_data(administrators)
                return True
        # Return False if the administrator was not found
        return False

    def search_administrator(self, search_term):
        administrators = self.storage.load_data()
        # Remove leading and trailing spaces
        search_term = search_term.strip()
        for admin_data in administrators:
            # Search by ID, first name or last name
            if (admin_data["person_id"].upper() == search_term.upper()
                    or admin_data["first_name"].lower() == search_term.lower()
                    or admin_data["last_name"].lower() == search_term.lower()):
                return admin_data
        # Return None if there are no matching administrators
        return None    