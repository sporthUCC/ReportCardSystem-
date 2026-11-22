from storage.json_storage import JSONStorage
from config.settings import SUBJECT_FILE
"""
The SubjectRepository is responsible for managing and manipulating subject records. It handles adding, retrieving, updating, and deleting subject data stored in the JSON file
"""
class SubjectRepository:
    def __init__(self):
        self.storage = JSONStorage(SUBJECT_FILE)
    def add_subject(self, subject):
       subjects = self.storage.load_data()
       
       for subject_data in subjects:
           if subject_data["subject_id"]==subject.get_subject_id():
               raise ValueError("Subject ID already exists")
              
           if subject_data["subject_name"].lower() == subject.get_subject_name().lower():
               raise ValueError("Subject already exists")  
       # Convert the Subject object into a dictionary containing its details
       subject_data = subject.get_subject_details()

       # Add the new subject dictionary to the existing list of subjects
       subjects.append(subject_data)

      # Save the updated subject records to the JSON file
       self.storage.save_data(subjects)
          
    def get_subject_by_id(self, subject_id):
        subjects = self.storage.load_data()
        #remove trailing spaces from the entered ID
        subject_id = subject_id.strip()
        for subject_data in subjects:
           
            #check whether the Subject ID matches 
            if subject_data["subject_id"].upper() ==subject_id.upper() :
                return subject_data
        
        #return None if no matching subject is found
        return None   
       
   
    def update_subject(self, subject_id, update_data):
        """
        Updates the subject name or assigned teacher using the subject ID.
        Returns True if the subject is updated, otherwise False.
        """

        # Load all subjects from the JSON file
        subjects = self.storage.load_data()

        # Go through each subject in the list
        for subject_data in subjects:

            # Check if the subject ID matches
            if subject_data["subject_id"] == subject_id:

                # Update the subject name if provided
                if "subject_name" in update_data:
                    subject_data["subject_name"] = update_data["subject_name"]

                # Update the teacher ID if provided
                if "teacher_id" in update_data:
                    subject_data["teacher_id"] = update_data["teacher_id"]

                # Save the updated subject list
                self.storage.save_data(subjects)
                return True

        # Return False if the subject was not found
        return False

    
    def delete_subject(self, subject_id):
        """
        Deletes a subject using its ID.
        Returns True if the subject is deleted, otherwise False.
        """

        # Load all subject records
        subjects = self.storage.load_data()

        # Loop through the subject records
        for subject_data in subjects:

            # Check if the subject ID matches the ID provided
            if subject_data["subject_id"] == subject_id:

                # Remove the matching subject
                subjects.remove(subject_data)

                # Save the updated subject list to JSON
                self.storage.save_data(subjects)
                return True

        # Return False if the subject was not found
        return False
   
    def search_subject(self, search_term):
        """
        Searches for a subject using its ID.
        Returns the matching subject if found, otherwise None.
        """

        # Load all subject records
        subjects = self.storage.load_data()

        # Remove any leading or trailing spaces
        search_term = search_term.strip()

        # Loop through the subject records
        for subject_data in subjects:

            # Compare subject IDs without considering capitalization
            if subject_data["subject_id"].upper() == search_term.upper():
                return subject_data

        # Return None if no matching subject is found
        return None

     