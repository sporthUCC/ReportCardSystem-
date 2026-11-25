
from storage.json_storage import JSONStorage
from config.settings import GRADE_FILE

"""
This GradeRepository class is responsible for managing grade records,
including adding, retrieving, updating, searching, and deleting grades.
It uses JSONStorage to save and retrieve grade information from the
grades.json file so that records remain available even after the
application is closed.
"""

class GradeRepository:

    def __init__(self):
        self.storage = JSONStorage(GRADE_FILE)

    #get all the grades
    def get_all_grades(self):
        #return all grades
        return self.storage.load_data()
        
    
    # Add a grade record.
    def add_grade(self, grade):

        grades = self.storage.load_data()

        # Check if a grade already exists for this student, subject and academic period.
        for grade_data in grades:
            if (
                grade_data["student_id"] == grade.get_student_id()
                and grade_data["subject_id"] == grade.get_subject_id()
                and grade_data.get("academic_year") == grade.get_academic_year()
                and grade_data.get("academic_term") == grade.get_academic_term()
            ):
                raise ValueError(
                    "Grade record already exists for this student, subject and academic period."
                )

        # Convert the Grade object into a dictionary.
        grade_data = grade.get_grade_details()

        # Add the dictionary to the existing list.
        grades.append(grade_data)

        # Save the updated list back to grades.json.
        self.storage.save_data(grades)

    # Retrieve a grade using its grade ID.
    def get_grade_by_id(self, grade_id):

        grades = self.storage.load_data()

        # Remove leading and trailing spaces.
        grade_id = grade_id.strip()

        # Loop through the grade records.
        for grade_data in grades:
            if grade_data["grade_id"] == grade_id:
                return grade_data

        # Return None if the grade ID does not exist.
        return None

    # Retrieve all grades belonging to a student.
    def get_grades_by_student_id(self, student_id):

        # Load all existing grade records.
        grades = self.storage.load_data()

        # Create an empty list to store matching grades.
        student_grades = []

        # Remove leading and trailing spaces.
        student_id = student_id.strip().upper()

        # Loop through all grade records.
        for grade_data in grades:

            # Check if the student ID matches.
            if grade_data["student_id"].upper() == student_id:

                # Add the matching grade to the list.
                student_grades.append(grade_data)

        # Return all matching grades.
        return student_grades

   # Update an existing grade record
    def update_grade(self, grade_id, update_data):

        # Load all existing grade records
        grades = self.storage.load_data()

        # Remove leading and trailing spaces
        grade_id = grade_id.strip()

        # Loop through each grade record
        for grade_data in grades:

            # Check if the grade ID matches
            if grade_data["grade_id"].upper() == grade_id.upper():

                # Update student ID if provided
                if "student_id" in update_data:
                    grade_data["student_id"] = update_data["student_id"]

                # Update subject ID if provided
                if "subject_id" in update_data:
                    grade_data["subject_id"] = update_data["subject_id"]

                # Update coursework if provided
                if "coursework" in update_data:
                    grade_data["coursework"] = update_data["coursework"]

                # Update project if provided
                if "project" in update_data:
                    grade_data["project"] = update_data["project"]

                # Update midterm if provided
                if "midterm" in update_data:
                    grade_data["midterm"] = update_data["midterm"]

                # Update final exam if provided
                if "final_exam" in update_data:
                    grade_data["final_exam"] = update_data["final_exam"]
                # Update academic year if provided
                if "academic_year" in update_data:
                    grade_data["academic_year"] = update_data["academic_year"]

                # Update academic term if provided
                if "academic_term" in update_data:
                    grade_data["academic_term"] = update_data["academic_term"]

                # Save the updated grade records
                self.storage.save_data(grades)

                return True

        return False
    # Delete a grade record using its grade ID.
    def delete_grade(self, grade_id):

        # Load all grade records.
        grades = self.storage.load_data()

        # Remove leading and trailing spaces.
        grade_id = grade_id.strip()

        # Loop through the grade records.
        for grade_data in grades:

            # Check if the grade ID matches.
            if grade_data["grade_id"] == grade_id:

                # Remove the matching grade record.
                grades.remove(grade_data)

                # Save the updated grades list.
                self.storage.save_data(grades)

                return True

        # Return False if the grade was not found.
        return False

    # Search grades using either grade ID or student ID.
    def search_grades(self, search_term):

        # Load all grade records.
        grades = self.storage.load_data()

        # Remove leading and trailing spaces.
        search_term = search_term.strip().upper()

        # Store matching student grades.
        matching_grades = []

        # Loop through the grade records.
        for grade_data in grades:

            # Search using grade ID.
            if grade_data["grade_id"].upper() == search_term:
                return grade_data

            # Search using student ID.
            if grade_data["student_id"].upper() == search_term:
                matching_grades.append(grade_data)

        # Return all matching grades if found.
        if matching_grades:
            return matching_grades

        # Return None if no matching records are found.
        return None