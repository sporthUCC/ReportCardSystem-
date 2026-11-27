
from repositories.grade_repository import GradeRepository
from models.grade import Grade

#imprting course assement weight from the setting.py
from config.settings import (
    COURSEWORK_WEIGHT,
    PROJECT_WEIGHT,
    MIDTERM_WEIGHT,
    FINAL_EXAM_WEIGHT
)

class GradeService:
    def __init__(self, student_service, subject_service):
        self.grade_repository = GradeRepository()
        self.student_service = student_service
        self.subject_service = subject_service

    # Retrieves all grades
    def get_all_grades(self):
        # Ask the repository to load all grades
        all_grades = self.grade_repository.get_all_grades()

        # Return all grades
        return all_grades

    # Generates a unique grade ID
    def generate_grade_id(self):
        # Retrieve all existing grades
        grades = self.grade_repository.get_all_grades()

        # Check if there are no existing grades
        if not grades:
            return "GRD001"

        # Extract the numeric portions of existing IDs
        grade_numbers = []

        for grade in grades:
            grade_number = int(grade["grade_id"][3:])
            grade_numbers.append(grade_number)

        # Find the highest existing grade number
        highest_number = max(grade_numbers)

        # Generate the next grade ID
        next_number = highest_number + 1

        return f"GRD{next_number:03d}"

    # Retrieves a grade by ID
    def get_grade_by_id(self, grade_id):
        # Ask the repository to find the grade
        grade = self.grade_repository.get_grade_by_id(grade_id)

        # Check whether the grade exists
        if grade is None:
            raise ValueError("Grade not found.")

        return grade

        # Adds a new grade
    def add_grade(self, student_id, subject_id, academic_year, academic_term,
                coursework, project, midterm, final_exam):
        try:
            # Validate academic year
            if not isinstance(academic_year, str) or not academic_year.strip():
                raise ValueError("Academic year must be valid text.")

            # Validate academic term
            if not isinstance(academic_term, str) or not academic_term.strip():
                raise ValueError("Academic term must be valid text.")

            # Check whether student exists
            self.student_service.get_student_by_id(student_id)

            # Check whether subject exists
            self.subject_service.get_subject_by_id(subject_id)

            # Generate a unique grade ID
            grade_id = self.generate_grade_id()

            # Create Grade object
            stu_grade = Grade(
                grade_id,
                student_id,
                subject_id,
                academic_year,
                academic_term,
                coursework,
                project,
                midterm,
                final_exam
            )

            # Save grade information
            self.grade_repository.add_grade(stu_grade)

            return "Grade added successfully."

        except ValueError as err:
            return str(err)

   
    # Updates an existing grade information
    def update_grade(self, grade_id, update_data):
        try:
            # Check whether grade exists
            grade = self.grade_repository.get_grade_by_id(grade_id)

            if grade is None:
                raise ValueError("Grade not found.")

            # Check whether update information was provided
            if not update_data:
                raise ValueError("No information provided for update.")

            # Validate academic year if provided
            if "academic_year" in update_data:
                academic_year = update_data["academic_year"]

                if not isinstance(academic_year, str) or not academic_year.strip():
                    raise ValueError("Academic year must be valid text.")

            # Validate academic term if provided
            if "academic_term" in update_data:
                academic_term = update_data["academic_term"]

                if not isinstance(academic_term, str) or not academic_term.strip():
                    raise ValueError("Academic term must be valid text.")

            # Validate coursework if provided
            if "coursework" in update_data:
                coursework = update_data["coursework"]

                if isinstance(coursework, bool) or not isinstance(coursework, (int, float)):
                    raise ValueError("Coursework must be a number.")

                if coursework < 0 or coursework > 100:
                    raise ValueError("Coursework must be between 0 and 100.")

            # Validate project if provided
            if "project" in update_data:
                project = update_data["project"]

                if isinstance(project, bool) or not isinstance(project, (int, float)):
                    raise ValueError("Project must be a number.")

                if project < 0 or project > 100:
                    raise ValueError("Project must be between 0 and 100.")

            # Validate midterm if provided
            if "midterm" in update_data:
                midterm = update_data["midterm"]

                if isinstance(midterm, bool) or not isinstance(midterm, (int, float)):
                    raise ValueError("Midterm must be a number.")

                if midterm < 0 or midterm > 100:
                    raise ValueError("Midterm must be between 0 and 100.")

            # Validate final exam if provided
            if "final_exam" in update_data:
                final_exam = update_data["final_exam"]

                if isinstance(final_exam, bool) or not isinstance(final_exam, (int, float)):
                    raise ValueError("Final exam must be a number.")

                if final_exam < 0 or final_exam > 100:
                    raise ValueError("Final exam must be between 0 and 100.")

            # Check for invalid fields
            allowed_fields = [
                "academic_year",
                "academic_term",
                "coursework",
                "project",
                "midterm",
                "final_exam"
            ]

            for field in update_data:
                if field not in allowed_fields:
                    raise ValueError(f"Invalid field: {field}")

            # Send updated information to the repository
            updated = self.grade_repository.update_grade(grade_id, update_data)

            if updated:
                return "Grade updated successfully."

            return "Unable to update grade."

        except ValueError as err:
            return str(err)

     
        # Retrieves grades belonging to a student
    def get_grades_by_student(self, student_id):
        # Retrieve all grades
        grades = self.grade_repository.get_all_grades()

        # Store grades belonging to the student
        student_grades = []

        for grade in grades:
            if grade["student_id"] == student_id:
                student_grades.append(grade)

        return student_grades

    # Deletes an existing grade
    def delete_grade(self, grade_id):
        try:
            # Check whether grade exists
            grade = self.grade_repository.get_grade_by_id(grade_id)

            if grade is None:
                raise ValueError("Grade not found.")

            # Ask repository to delete the grade
            deleted = self.grade_repository.delete_grade(grade_id)

            if deleted:
                return "Grade deleted successfully."

            return "Unable to delete grade."

        except ValueError as err:
            return str(err)
    def calculate_final_grade(self, grade):
        coursework = grade["coursework"] * COURSEWORK_WEIGHT
        project = grade["project"] * PROJECT_WEIGHT
        midterm = grade["midterm"] * MIDTERM_WEIGHT
        final_exam = grade["final_exam"] * FINAL_EXAM_WEIGHT

        final_grade = coursework + project + midterm + final_exam

        return round(final_grade, 2)
    # Assigns a letter grade and performance level
    def get_grade_classification(self, average):

        if average >= 90:
            return "A", "Outstanding"

        elif average >= 80:
            return "B", "Very Good"

        elif average >= 70:
            return "C", "Good"

        elif average >= 60:
            return "D", "Satisfactory"

        else:
            return "F", "Needs Improvement"