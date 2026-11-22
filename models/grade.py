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
        self.__coursework = coursework
        self.__project = project
        self.__midterm = midterm
        self.__final_exam = final_exam
    
            
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
    
    # Setter method to update the coursework score.
    def set_coursework(self, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Coursework score must be a number.")

        if value < 0 or value > 100:
            raise ValueError("Coursework score must be between 0 and 100.")

        self.__coursework = value