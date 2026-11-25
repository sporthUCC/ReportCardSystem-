from repositories.subject_repository import SubjectRepository
from models.subject import Subject

class SubjectService:
    def __init__(self, teacher_service):
        self.subject_repository = SubjectRepository()
        self.teacher_service = teacher_service
        
        
    def generate_subject_id(self):
        # Retrieve all existing subject records
        subjects = self.subject_repository.get_all_subjects()

        # Assign the first ID if no subjects exist
        if not subjects:
            return "SUB001"

        # Store the numeric portions of existing IDs
        numbers = []

        # Extract the number from each subject ID
        for subject in subjects:
            number = int(subject["subject_id"][3:])
            numbers.append(number)

        # Find the highest existing subject number
        highest_id = max(numbers)

        # Generate and return the next subject ID
        return f"SUB{highest_id + 1:03d}" 
        
         
    #loading all subjects
    def get_all_subjects(self):
        subjects = self.subject_repository.get_all_subjects()
        #providing all the subjects
        return subjects

    def get_subject_by_id(self, subject_id):
        """Retrieves a subject using its ID."""

        subject = self.subject_repository.get_subject_by_id(subject_id)

        if subject is None:
            raise ValueError("Subject not found.")

        return subject

    def add_subject(self, subject_name, teacher_id):
        try:
            # Generate a unique subject ID
            subject_id = self.generate_subject_id()

            # Validate subject name
            if not isinstance(subject_name, str) or not subject_name.strip():
                raise ValueError("Subject name cannot be empty.")

            # Validate teacher ID
            if not isinstance(teacher_id, str) or not teacher_id.strip():
                raise ValueError("Teacher ID cannot be empty.")

            # Check if teacher exists
            teacher = self.teacher_service.get_teacher_by_id(teacher_id)

            if not teacher:
                raise ValueError("Teacher not found.")

            # Create Subject object
            subject = Subject(subject_id, subject_name, teacher_id)

            # Save subject information
            self.subject_repository.add_subject(subject)

            return "Subject added successfully."

        except ValueError as err:
            return str(err)    
  #update subject
    def update_subject(self, subject_id, update_data):
      try:
          # Retrieve subject by ID
          subject = self.subject_repository.get_subject_by_id(subject_id)

          if not subject:
              raise ValueError("Subject not found.")

          # Validate subject name if provided
          if "subject_name" in update_data:
              subject_name = update_data["subject_name"]

              if not isinstance(subject_name, str) or not subject_name.strip():
                  raise ValueError("Subject name cannot be empty.")

          # Validate teacher ID if provided
          if "teacher_id" in update_data:
              teacher_id = update_data["teacher_id"]

              if not isinstance(teacher_id, str) or not teacher_id.strip():
                  raise ValueError("Teacher ID cannot be empty.")

              teacher = self.teacher_service.get_teacher_by_id(teacher_id)

              if not teacher:
                  raise ValueError("Teacher not found.")

          # Update subject information
          updated = self.subject_repository.update_subject(subject_id, update_data)

          if not updated:
              raise ValueError("Unable to update subject.")

          return "Subject updated successfully."

      except ValueError as err:
          return str(err)
    
    # Delete subject
    def delete_subject(self, subject_id):
        try:
            # Check whether the subject exists
            subject = self.subject_repository.get_subject_by_id(subject_id)

            if subject is None:
                raise ValueError("Subject not found.")

            # Ask repository to delete the subject
            deleted = self.subject_repository.delete_subject(subject_id)

            if deleted:
                return "Subject deleted successfully."

            return "Unable to delete subject."

        except ValueError as err:
            return str(err)

