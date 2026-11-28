from services.grade_service import GradeService


# ---------- Fake helpers (no real files are touched) ----------
class FakeStudentService:
    """Behaves like StudentService: returns a record, or raises ValueError."""
    def get_student_by_id(self, student_id):
        students = {
            "S100": {"person_id": "S100", "first_name": "Test", "last_name": "Student"},
            "S101": {"person_id": "S101", "first_name": "Other", "last_name": "Student"},
        }
        if student_id not in students:
            raise ValueError("Student not found.")
        return students[student_id]


class FakeSubjectService:
    """Behaves like SubjectServices after the 'return subject' fix."""
    def get_subject_by_id(self, subject_id):
        subjects = {
            "SUB100": {"subject_id": "SUB100", "subject_name": "Mathematics"},
            "SUB101": {"subject_id": "SUB101", "subject_name": "English Language"},
        }
        if subject_id not in subjects:
            raise ValueError("Subject not found")
        return subjects[subject_id]


class FakeGradeRepository:
    """Keeps grades in memory instead of grades.json."""
    def __init__(self):
        self.grades = []

    def get_all_grades(self):
        return list(self.grades)

    def get_grade_by_id(self, grade_id):
        for grade in self.grades:
            if grade["grade_id"] == grade_id.strip():
                return grade
        return None

    def add_grade(self, grade):
        details = grade.get_grade_details()
        for existing in self.grades:
            if (existing["student_id"] == details["student_id"]
                    and existing["subject_id"] == details["subject_id"]):
                raise ValueError("Grade record already exists for this student and subject.")
        self.grades.append(details)

    def update_grade(self, grade_id, update_data):
        for grade in self.grades:
            if grade["grade_id"] == grade_id:
                grade.update(update_data)
                return True
        return False

    def delete_grade(self, grade_id):
        for grade in self.grades:
            if grade["grade_id"] == grade_id:
                self.grades.remove(grade)
                return True
        return False


# ---------- Helpers that print PASS or FAIL ----------
def check(label, condition):
    print("PASS -" if condition else "FAIL -", label)


service = GradeService(FakeStudentService(), FakeSubjectService())
service.grade_repository = FakeGradeRepository()   # use memory, not the real file

# ---------- Adding grades ----------
print("--- Adding grades ---")
check("Add a valid grade", service.add_grade("S100", "SUB100", 80, 90, 70, 85) == "Grade added successfully.")
check("First grade ID is GRD001", service.get_all_grades()[0]["grade_id"] == "GRD001")
check("Second grade is added", service.add_grade("S100", "SUB101", 60, 60, 60, 60) == "Grade added successfully.")
check("Second grade ID is GRD002", service.get_all_grades()[1]["grade_id"] == "GRD002")
check("Duplicate student + subject is rejected",
      service.add_grade("S100", "SUB100", 50, 50, 50, 50) == "Grade record already exists for this student and subject.")
check("Unknown student is rejected", service.add_grade("S999", "SUB100", 80, 80, 80, 80) == "Student not found.")
check("Unknown subject is rejected", service.add_grade("S100", "SUB999", 80, 80, 80, 80) == "Subject not found")

# ---------- Bad scores ----------
print("\n--- Bad scores must not be saved ---")
for bad_value in [-5, 101, "abc", None]:
    before = len(service.get_all_grades())
    try:
        result = service.add_grade("S101", "SUB100", bad_value, 80, 80, 80)
        saved = result == "Grade added successfully."
        check(f"Score {bad_value!r} is rejected", (not saved) and len(service.get_all_grades()) == before)
    except Exception as error:
        print("FAIL -", f"Score {bad_value!r} crashed the program:", repr(error))

# ---------- Updating grades ----------
print("\n--- Updating grades ---")
check("Valid update", service.update_grade("GRD001", {"coursework": 95}) == "Grade updated successfully.")
check("Coursework changed to 95", service.get_grade_by_id("GRD001")["coursework"] == 95)
check("Score over 100 is rejected", service.update_grade("GRD001", {"project": 150}) == "Project must be between 0 and 100.")
check("Negative score is rejected", service.update_grade("GRD001", {"midterm": -1}) == "Midterm must be between 0 and 100.")
check("Letters are rejected", service.update_grade("GRD001", {"final_exam": "abc"}) == "Final exam must be a number.")
check("Unknown field is rejected", service.update_grade("GRD001", {"nickname": 5}) == "Invalid field: nickname")
check("Empty update is rejected", service.update_grade("GRD001", {}) == "No information provided for update.")
check("Missing grade ID is rejected", service.update_grade("GRD999", {"coursework": 50}) == "Grade not found.")
check("Rejected updates changed nothing", service.get_grade_by_id("GRD001")["project"] == 90)

# ---------- Finding and deleting ----------
print("\n--- Finding and deleting ---")
check("get_grades_by_student finds both of S100's grades", len(service.get_grades_by_student("S100")) == 2)
check("get_grades_by_student gives nothing for S101", service.get_grades_by_student("S101") == [])
try:
    service.get_grade_by_id("GRD999")
    print("FAIL - get_grade_by_id should raise for a missing ID")
except ValueError:
    print("PASS - get_grade_by_id raises for a missing ID")
check("Delete a grade", service.delete_grade("GRD002") == "Grade deleted successfully.")
check("Deleted grade is gone", len(service.get_grades_by_student("S100")) == 1)
check("Deleting a missing grade is rejected", service.delete_grade("GRD002") == "Grade not found.")

print("\nDone. A line starting with FAIL needs attention.")