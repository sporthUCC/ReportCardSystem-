from models.administrator import Administrator
from services.admin_service import AdminService


# ---------- Fake services ----------
# AdminService only passes work on to the other services, so we test it with
# fake ones. They record every call, which means no real files are touched.
class FakeService:
    def __init__(self):
        self.calls = []

    def __getattr__(self, method_name):
        def method(*args, **kwargs):
            self.calls.append((method_name, args))
            return f"result of {method_name}"
        return method


class NotAnAdmin:
    """Stands in for any user who is not an Administrator (for example a teacher)."""
    pass


# ---------- Helpers that print PASS or FAIL ----------
def check(label, condition):
    print("PASS -" if condition else "FAIL -", label)


def expect_blocked(label, function, *args):
    try:
        function(*args)
        print("FAIL -", label, "(no error was raised)")
    except PermissionError:
        print("PASS -", label)


def build(user):
    """Creates an AdminService with fresh fake services for the given user."""
    students, subjects, grades = FakeService(), FakeService(), FakeService()
    return AdminService(user, students, subjects, grades), students, subjects, grades


admin_user = Administrator("A001", "Mary", "Smith", "mary@email.com", "Female", "Full Access")

# ---------- 1. Non-administrators must be refused ----------
print("--- Permissions ---")
blocked, students, subjects, grades = build(NotAnAdmin())
expect_blocked("view_students", blocked.view_students)
expect_blocked("register_student", blocked.register_student, "student")
expect_blocked("update_student", blocked.update_student, "S001", {})
expect_blocked("delete_student", blocked.delete_student, "S001")
expect_blocked("search_student", blocked.search_student, "Sara")
expect_blocked("view_subjects", blocked.view_subjects)
expect_blocked("add_subject", blocked.add_subject, "Maths", "T001")
expect_blocked("edit_subject", blocked.edit_subject, "SUB001", {})
expect_blocked("delete_subject", blocked.delete_subject, "SUB001")
expect_blocked("view_records", blocked.view_records)
check("Nothing reached the services when blocked",
      not students.calls and not subjects.calls and not grades.calls)

# ---------- 2. An administrator's requests reach the right service ----------
print("\n--- Student management ---")
service, students, subjects, grades = build(admin_user)

check("view_students", service.view_students() == "result of get_all_students")
check("register_student", service.register_student("new student") == "result of add_student")
check("register_student sent the student on", students.calls[-1] == ("add_student", ("new student",)))
check("update_student", service.update_student("S001", {"grade_level": 9}) == "result of update_student")
check("update_student sent the right data",
      students.calls[-1] == ("update_student", ("S001", {"grade_level": 9})))
check("delete_student", service.delete_student("S001") == "result of delete_student")
check("delete_student sent the right ID", students.calls[-1] == ("delete_student", ("S001",)))
check("search_student", service.search_student("Sara") == "result of search_student")
check("search_student sent the right term", students.calls[-1] == ("search_student", ("Sara",)))

print("\n--- Subject management ---")
check("view_subjects", service.view_subjects() == "result of get_all_subjects")
check("add_subject", service.add_subject("Maths", "T001") == "result of add_subject")
check("add_subject sent name and teacher", subjects.calls[-1] == ("add_subject", ("Maths", "T001")))
check("edit_subject", service.edit_subject("SUB001", {"teacher_id": "T002"}) == "result of update_subject")
check("edit_subject sent the right data",
      subjects.calls[-1] == ("update_subject", ("SUB001", {"teacher_id": "T002"})))
check("delete_subject", service.delete_subject("SUB001") == "result of delete_subject")
check("delete_subject sent the right ID", subjects.calls[-1] == ("delete_subject", ("SUB001",)))

print("\n--- Academic records ---")
check("view_records", service.view_records() == "result of get_all_grades")

print("\nDone. Every line above should start with PASS.")