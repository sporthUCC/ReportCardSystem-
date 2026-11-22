from config.settings import (
   COURSEWORK_WEIGHT,
    PROJECT_WEIGHT,
    MIDTERM_WEIGHT,
    FINAL_EXAM_WEIGHT
)

class Grade:
    def __init__(self, grade_id, student_id, subject_id, coursework, project, midterm, final_exam):
        self.__grade_id = grade_id
        self.__student_id = student_id
        self.__subject_id = subject_id
        self.set_coursework(coursework)
        self.set_project(project)
        self.set_midterm(midterm)
        self.set_final_exam(final_exam)
            
            
    # Getter method to retrieve the grade ID.
    def get_grade_id(self):
        return self.__grade_id

    # Getter method to retrieve the student ID.
    def get_student_id(self):
        return self.__student_id

    # Getter method to retrieve the subject ID.
    def get_subject_id(self):
        return self.__subject_id

    # Getter method to retrieve the coursework score.
    def get_coursework(self):
        return self.__coursework

    # Getter method to retrieve the project score.
    def get_project(self):
        return self.__project

    # Getter method to retrieve the midterm score.
    def get_midterm(self):
        return self.__midterm

    # Getter method to retrieve the final exam score.
    def get_final_exam(self):
        return self.__final_exam
    
    #Setter method to update the coursework score.
    def set_coursework(self, value):
        """
       Check to see if the value is a whole number or decimal, since those are the two acceptable data types for a coursework score.
       """
        
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Coursework score must be a number.")

        if value < 0 or value > 100:
            raise ValueError("Coursework score must be between 0 and 100.")

        self.__coursework = value
    # Setter method to update the project score.
    def set_project(self, value):

        # Check to see if the value is a whole number or decimal, since those are the two acceptable data types for a project score.
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Project score must be a number.")

        # Check if the score is within the accepted range.
        if value < 0 or value > 100:
            raise ValueError("Project score must be between 0 and 100.")

        self.__project = value
        
    # Setter method to update the midterm score.
    def set_midterm(self, value):

        # Check to see if the value is a whole number or decimal, since those are the two acceptable data types for a midterm score.
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Midterm score must be a number.")

        # Check if the score is within the accepted range.
        if value < 0 or value > 100:
            raise ValueError("Midterm score must be between 0 and 100.")

        self.__midterm = value
        
   # Setter method to update the final exam score.
    def set_final_exam(self, value):

        # Check to see if the value is a whole number or decimal, since those are the two acceptable data types for final_exam scores.
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Final Exam score must be a number.")

        # Check if the score is within the accepted range.
        if value < 0 or value > 100:
            raise ValueError("Final Exam score must be between 0 and 100.")

        self.__final_exam = value
        
    def calculate_final_grade(self):
        return (
            self.__coursework * COURSEWORK_WEIGHT
            + self.__project * PROJECT_WEIGHT
            + self.__midterm * MIDTERM_WEIGHT
            + self.__final_exam *FINAL_EXAM_WEIGHT
        )
    def get_grade_details(self):
        return {
            "grade_id": self.get_grade_id(),
            "student_id": self.get_student_id(),
            "subject_id": self.get_subject_id(),
            "coursework": self.get_coursework(),
            "project": self.get_project(),
            "midterm": self.get_midterm(),
            "final_exam": self.get_final_exam(),
            "final_grade": self.calculate_final_grade()
        }