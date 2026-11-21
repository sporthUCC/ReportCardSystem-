class Student:
    # ---------- Encapsulation: grade level ----------
    @property
    def grade_level(self):
        """Getter method to retrieve the grade level."""
        return self.__grade_level

    @grade_level.setter
    def grade_level(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Grade level must be an.")
        if value not in self.VALID_GRADE_LEVELS:
            raise ValueError(f"Grade level must be between 7 and 11.")
        self.__grade_level = value

    # keep your orginal methods for adding scores, calculating final grades, and generating report cards here
    def get_grade_level(self):
        """Getter method to retrieve the grade level."""
        return self.__grade_level

    # ---------- Encapsulation: parent contact (optional) ----------
    @property
    def parent_contact(self):
        """Getter method to retrieve the parent contact information."""
        return self.__parent_contact

    @parent_contact.setter
    def parent_contact(self, value):
        """Setter method to set the parent contact information."""
        self.__parent_contact = value

    # ---------- Grade entry ----------
    @staticmethod
    def validate_score(value):
        """Validate that the score is a number between 0 and 100."""
        if value is None or str(value).strip() == "":
            raise ValueError("Grade cannot be empty.")
        try:
            score = float(value)
        except ValueError:
            raise ValueError("Grade must be a number, not a letter.")
        if score < 0 or score > 100:
            raise ValueError("Grade must be between 0 and 100.")
        return score

    def set_score(self, subject, category, score):
        """Set the score for a specific subject and category."""
        category = category.lower()
        if category not in self.CATEGORIES:
            raise ValueError(f"Unkown category: {category}")
        score = self.validate_score(score)
        self.__subject_scores.setdefault(subject, {})[category] = score

    def get_score(self, subject):
        """Get the score for a specific subject and category."""
        return dict(self.__subject_scores.get(subject, {}))

    def get_subjects(self):
        """Get a list of subjects for which scores have been entered."""
        return list(self.__subject_scores.keys())

    # ---------- Calculations ----------
    def subject_grade(self, subject):
        """Weighted total for a subject, or None if any category is missing."""
        scores = self.__subject_scores.get(subject)
        if set(scores.keys()) != set(self.CATEGORIES.keys()):
            return None  # Missing category
        return sum(scores[cat] * weight for cat, weight in self.CATEGORIES.items())

    def calculate_average(self):
        """Sum of subject grades / number of subjects WITH grades."""
        grades = [grade for subject in self.__subject_scores 
                  if (grade := self.subject_grade(subject)) is not None]
        if not grades:
            return None  # No subjects with complete grades
        return sum(grades) / len(grades)

    @staticmethod
    def letter_grade(average):
        """Convert numeric average to letter grade."""
        if average is None:
            return None
        if average >= 90: return "A"
        if average >= 80: return "B"
        if average >= 70: return "C"
        if average >= 60: return "D"
        return "F"

    @staticmethod
    def performance_level(average):
        levels = {"A": "Excellent", "B": "Very Good", "C": "Good", 
                  "D": "Below Average", "F": "Needs Improvement"}
        return levels.get(Student.letter_grade(average), "No grade yet")

    def teachers_comments(self):
        """Generate teacher's comments based on the student's average."""
        average = self.calculate_average()
        comments = {
            "A": "Outstanding performance! Keep up the excellent work.",
            "B": "Very good job! You're doing well, but there's room for improvement.",
            "C": "Good effort! Focus on areas that need improvement.",
            "D": "Below average. Consider seeking extra help to improve.",
            "F": "Needs significant improvement. Please consult with your teacher."
        } 
        return comments.get(self.letter_grade(average), "No comment available.")

    # ---------- Polymorphism (overrides Person's abstract methods) ----------
    def get_person_details(self):
        details = super().get_person_details()
        details["grade_level"] = self.grade_level
        details["parent_contact"] = self.parent_contact
        return details

    def display_information(self):
        avg = self.calculate_average()
        avg_text = f"{avg:.1f}" if avg is not None else "N/A"
        return (f"student ID: {self.person_id}"
                 f"Name: {self.first_name} {self.last_name}, "
                 f"Grade: {self.grade_level} | Average: {avg_text}")