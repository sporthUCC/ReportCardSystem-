import pytest

from models.administrator import Administrator
from models.student import Student
from models.teacher import Teacher


def test_student_gender_is_optional():
    student = Student("S001", "Sam", "Lee", "sam@example.com", grade_level=10)

    assert student.gender is None


def test_teacher_gender_is_optional():
    teacher = Teacher(
        "T001", "Taylor", "Lee", "taylor@example.com", subject_taught="Math"
    )

    assert teacher.gender is None


def test_administrator_gender_is_optional():
    administrator = Administrator(
        "A001", "Alex", "Lee", "alex@example.com", access_level="Full Access"
    )

    assert administrator.gender is None


def test_subclasses_keep_positional_gender_compatibility():
    student = Student("S002", "Sam", "Lee", "sam@example.com", "Female", 10)
    teacher = Teacher("T002", "Taylor", "Lee", "taylor@example.com", "Male", "Math")
    administrator = Administrator(
        "A002", "Alex", "Lee", "alex@example.com", "Female", "Full Access"
    )

    assert student.gender == "Female"
    assert teacher.gender == "Male"
    assert administrator.gender == "Female"
