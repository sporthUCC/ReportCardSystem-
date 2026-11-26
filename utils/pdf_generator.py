import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

# School details and weights come from config/settings.py. The getattr defaults
# mean the generator still works if a setting has not been added yet.
import config.settings as settings

SCHOOL_NAME = getattr(settings, "SCHOOL_NAME", "School Name")
SCHOOL_ADDRESS = getattr(settings, "SCHOOL_ADDRESS", "School Address")
SCHOOL_PHONE = getattr(settings, "SCHOOL_PHONE", "School Phone")
SCHOOL_MOTTO = getattr(settings, "SCHOOL_MOTTO", "")
ACADEMIC_YEAR = getattr(settings, "ACADEMIC_YEAR", "2024 - 2025")
LOGO_FILE = getattr(settings, "LOGO_FILE", "assets/logo.png")
REPORTS_FOLDER = getattr(settings, "REPORTS_FOLDER", "reports")

COURSEWORK_WEIGHT = getattr(settings, "COURSEWORK_WEIGHT", 0.30)
PROJECT_WEIGHT = getattr(settings, "PROJECT_WEIGHT", 0.20)
MIDTERM_WEIGHT = getattr(settings, "MIDTERM_WEIGHT", 0.20)
FINAL_EXAM_WEIGHT = getattr(settings, "FINAL_EXAM_WEIGHT", 0.30)

# Colours used in the layout
PRIMARY = colors.HexColor("#2c3e50")
LIGHT_ROW = colors.HexColor("#f2f4f7")
GRID = colors.HexColor("#b0b7c3")

# Letter grade -> points on the 4.0 scale
GPA_POINTS = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}

PERFORMANCE = {"A": "Outstanding", "B": "Very Good", "C": "Good",
               "D": "Satisfactory", "F": "Needs Improvement"}

COMMENTS = {
    "A": "Outstanding performance! Keep up the excellent work.",
    "B": "Very good job! You're doing well, but there's room for improvement.",
    "C": "Good effort! Focus on areas that need improvement.",
    "D": "Below average. Consider seeking extra help to improve.",
    "F": "Needs significant improvement. Please consult with your teacher.",
}


# ---------- Small helpers ----------
def letter_grade(score):
    """Letter grade for a score, using the assignment's scale."""
    if score is None:
        return None
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _percent(weight):
    return f"{round(weight * 100)}%"
from fpdf import FPDF
from config.settings import (
    SCHOOL_ADDRESS,
    SCHOOL_PHONE,
    SCHOOL_EMAIL
)
from os import path, makedirs


# Store the letterhead file path.
LETTERHEAD_FILE = path.join("assets", "letter_head.jpeg")


class PDFGenerator(FPDF):

    def __init__(self):
        # Initialize the PDF document.
        super().__init__()

def _format_score(value):
    """Shows a score with one decimal place, or a dash when it is missing."""
    if value is None:
        return "-"
    return f"{float(value):.1f}"

        # Set margins so text stays inside the letterhead borders.
        self.set_margins(22, 15, 22)

        # Keep auto-page-break low so placing the comment in the bottom box stays on Page 1.
        self.set_auto_page_break(auto=True, margin=10)

    # Add the school letterhead and information to the report.
    def add_school_heading(self):

        # Add the letterhead background, which already contains the logo, title, and motto.
        self.image(LETTERHEAD_FILE, x=0, y=0, w=210, h=297)

        # Position below the top banner.
        self.set_y(82)

        # Display the school address and contact info centered above the divider.
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(75, 65, 90)
        self.cell(
            0, 4.5,
            f"{SCHOOL_ADDRESS}  |  Tel: {SCHOOL_PHONE}  |  {SCHOOL_EMAIL}",
            align="C", new_x="LMARGIN", new_y="NEXT"
        )

# ---------- Working out the figures the report data does not include ----------
def summarize(report_data):
    """Adds a letter grade and GPA points to every subject and works out the
    overall average, GPA, letter and comment.

    report_data is the dictionary returned by ReportService.prepare_report():
        {"student": {...},
         "subjects": [{"subject_name", "coursework", "project", "midterm",
                       "final_exam", "final_grade"}, ...]}
    If the report data already holds overall_average, overall_gpa or comment,
    those values are used instead of being calculated here."""
    rows = []
    for subject in report_data.get("subjects", []):
        final_grade = subject.get("final_grade")
        letter = letter_grade(final_grade)
        rows.append({
            "subject_name": subject.get("subject_name"),
            "coursework": subject.get("coursework"),
            "project": subject.get("project"),
            "midterm": subject.get("midterm"),
            "final_exam": subject.get("final_exam"),
            "final_grade": final_grade,
            "letter": letter,
            "gpa_points": GPA_POINTS.get(letter),
        })

    graded = [row for row in rows if row["final_grade"] is not None]

    overall_average = report_data.get("overall_average")
    if overall_average is None and graded:
        overall_average = sum(r["final_grade"] for r in graded) / len(graded)

    overall_gpa = report_data.get("overall_gpa")
    if overall_gpa is None and graded:
        overall_gpa = sum(r["gpa_points"] for r in graded) / len(graded)

    overall_letter = letter_grade(overall_average)
    comment = report_data.get("comment") or COMMENTS.get(overall_letter, "")

    return {
        "rows": rows,
        "overall_average": overall_average,
        "overall_gpa": overall_gpa,
        "overall_letter": overall_letter,
        "comment": comment,
    }


# ---------- Page sections ----------
def _build_header(styles):
    """School logo, name, address, contact and motto."""
    elements = []
        # Thin hot-pink accent rule separating header from report metadata.
        line_y = self.get_y() + 2
        self.set_draw_color(255, 30, 142)
        self.set_line_width(0.5)
        self.line(22, line_y, 188, line_y)

        # Compact Academic Year & Term bar directly below the rule.
        self.set_y(line_y + 2.5)
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(88, 28, 135)
        self.cell(
            83, 5,
            f"ACADEMIC YEAR: {self.academic_year}",
            align="L"
        )
        self.cell(
            83, 5,
            f"TERM: {self.academic_term.upper()}",
            align="R", new_x="LMARGIN", new_y="NEXT"
        )

        # Subtle bottom rule under the term strip.
        sub_y = self.get_y() + 1
        self.set_draw_color(220, 205, 235)
        self.set_line_width(0.3)
        self.line(22, sub_y, 188, sub_y)

        self.set_y(sub_y + 4)

    # Add the student's information in a clean, borderless two-column transcript grid.
    def add_student_information(self, student):

        start_y = self.get_y()

        # --- LEFT COLUMN: Student Identity ---
        # Label & Value: Student Name
        self.set_xy(22, start_y)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(120, 105, 135)
        self.cell(28, 5, "STUDENT NAME:")
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(25, 20, 35)
        self.cell(65, 5, f"{student['first_name']} {student['last_name']}")

        # Label & Value: Student ID
        self.set_xy(22, start_y + 6)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(120, 105, 135)
        self.cell(28, 5, "STUDENT ID:")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(35, 30, 45)
        self.cell(65, 5, str(student["person_id"]))

        # Label & Value: Date of Birth
        self.set_xy(22, start_y + 12)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(120, 105, 135)
        self.cell(28, 5, "DATE OF BIRTH:")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(35, 30, 45)
        self.cell(65, 5, str(student.get("date_of_birth") or "Not provided"))

def _build_grades_table(summary, styles):
    """One row per subject: the four scores, the final grade, letter and GPA points."""
    header = [
        "Subject",
        f"Coursework\n({_percent(COURSEWORK_WEIGHT)})",
        f"Project\n({_percent(PROJECT_WEIGHT)})",
        f"Mid-Term\n({_percent(MIDTERM_WEIGHT)})",
        f"Final Exam\n({_percent(FINAL_EXAM_WEIGHT)})",
        "Final\nGrade",
        "Letter\nGrade",
        "GPA\nPoints",
    ]
    rows = [header]

    if not summary["rows"]:
        rows.append(["No grades recorded yet"] + [""] * 7)
    else:
        for row in summary["rows"]:
            rows.append([
                Paragraph(_clean(row["subject_name"]), styles["cell"]),
                _format_score(row["coursework"]),
                _format_score(row["project"]),
                _format_score(row["midterm"]),
                _format_score(row["final_exam"]),
                _format_score(row["final_grade"]),
                _clean(row["letter"]),
                _format_score(row["gpa_points"]),
            ])

    # Overall row at the bottom
    rows.append(["Overall", "", "", "", "",
                 _format_score(summary["overall_average"]),
                 _clean(summary["overall_letter"]),
                 "-" if summary["overall_gpa"] is None else f"{summary['overall_gpa']:.2f}"])

    col_widths = [4.1 * cm, 2.0 * cm, 1.8 * cm, 1.9 * cm, 2.1 * cm,
                  1.6 * cm, 1.3 * cm, 1.4 * cm]
    table = Table(rows, colWidths=col_widths, repeatRows=1)

    last = len(rows) - 1
    style = [
        # Header row
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        # Body
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        # Overall row
        ("BACKGROUND", (0, last), (-1, last), LIGHT_ROW),
        ("FONTNAME", (0, last), (-1, last), "Helvetica-Bold"),
        ("SPAN", (0, last), (4, last)),
        ("ALIGN", (0, last), (0, last), "RIGHT"),
    ]
    # Zebra striping on the subject rows
    for row_index in range(2, last, 2):
        style.append(("BACKGROUND", (0, row_index), (-1, row_index), LIGHT_ROW))
    if not summary["rows"]:
        style.append(("SPAN", (0, 1), (-1, 1)))
        # Vertical subtle divider between left and right columns
        self.set_draw_color(220, 205, 235)
        self.set_line_width(0.3)
        self.line(118, start_y, 118, start_y + 17)

        # --- RIGHT COLUMN: Academic Placement & Term Average ---
        # Label & Value: Grade Level
        self.set_xy(123, start_y)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(120, 105, 135)
        self.cell(26, 5, "GRADE LEVEL:")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(25, 20, 35)
        self.cell(39, 5, str(student["grade_level"]), align="R")

        # Label & Value: Gender
        self.set_xy(123, start_y + 6)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(120, 105, 135)
        self.cell(26, 5, "GENDER:")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(35, 30, 45)
        self.cell(39, 5, str(student.get("gender") or "Not provided"), align="R")

        # Label & Value: Highlighted Term Average
        self.set_xy(123, start_y + 12)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(88, 28, 135)
        self.cell(26, 5, "TERM AVERAGE:")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(219, 39, 119)
        self.cell(39, 5, f"{self.final_average:.2f}%", align="R")

        # Bottom separator line under the student info block
        end_y = start_y + 19.5
        self.set_draw_color(220, 205, 235)
        self.line(22, end_y, 188, end_y)

        # Position cleanly for the grades table
        self.set_y(end_y + 5)

    # Add the column headings for the student grades.
    def add_table_header(self):

        # Set the font style.
        self.set_font("Helvetica", "B", 8)

        # Set the table heading colours.
        self.set_fill_color(45, 16, 56)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(255, 30, 142)
        self.set_line_width(0.4)

        # Add the table column headings.
        self.cell(38, 8.5, " Subject", border=1, align="L", fill=True)
        self.cell(26, 8.5, "Term Grade", border=1, align="C", fill=True)
        self.cell(26, 8.5, "Exam Grade", border=1, align="C", fill=True)
        self.cell(26, 8.5, "Average", border=1, align="C", fill=True)
        self.cell(25, 8.5, "Letter Grade", border=1, align="C", fill=True)
        self.cell(25, 8.5, "Performance", border=1, align="C", fill=True)

        # Move to the next line.
        self.ln()

    # Add student grades to the report table.
    def add_table_rows(self, subjects):

        # Set the table border colour.
        self.set_draw_color(216, 180, 254)
        self.set_line_width(0.25)

        # Loop through each subject with alternating row shading.
        for index, subject in enumerate(subjects):

            if index % 2 == 1:
                self.set_fill_color(249, 245, 252)
            else:
                self.set_fill_color(255, 255, 255)

            # Add the subject name.
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(25, 25, 35)
            self.cell(
                38, 7.8, f" {subject['subject_name']}",
                border=1, align="L", fill=True
            )

            # Add the term grade.
            self.set_font("Helvetica", "", 8)
            self.set_text_color(40, 40, 50)
            self.cell(
                26, 7.8, f"{subject['term_grade']:.2f}",
                border=1, align="C", fill=True
            )

            # Add the exam grade.
            self.cell(
                26, 7.8, str(subject["exam_grade"]),
                border=1, align="C", fill=True
            )

            # Add the subject average.
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(45, 16, 56)
            self.cell(
                26, 7.8, f"{subject['average']:.2f}",
                border=1, align="C", fill=True
            )

            # Add the letter grade.
            self.set_text_color(219, 39, 119)
            self.cell(
                25, 7.8, str(subject["letter_grade"]),
                border=1, align="C", fill=True
            )

            # Add the performance rating.
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(40, 40, 50)
            self.cell(
                25, 7.8, str(subject["performance_rating"]),
                border=1, align="C", fill=True
            )

def _build_summary(summary, styles):
    letter = summary["overall_letter"]
    text = (f"<b>Overall Average:</b> {_format_score(summary['overall_average'])}% "
            f"&nbsp;&nbsp; <b>Grade:</b> {_clean(letter)} "
            f"&nbsp;&nbsp; <b>Performance:</b> {PERFORMANCE.get(letter, 'No grades yet')}")
    if summary["overall_gpa"] is not None:
        text += f" &nbsp;&nbsp; <b>GPA (4.0 scale):</b> {summary['overall_gpa']:.2f}"
    return [Spacer(1, 8), Paragraph(text, styles["body"])]

        # Move to the next row.
        self.ln()

    # Add the student's automated academic comment inside the letterhead's built-in box.
    def add_academic_comment(self, academic_comment):

        # Pushed down slightly inside the letterhead's decorative bottom box on Page 1.
        self.set_y(236)
        self.set_x(30)

        # Clean heading without drawing an extra rectangle.
        self.set_font("Times", "B", 10.5)
        self.set_text_color(45, 16, 56)
        self.cell(
            150, 5.5, "ACADEMIC PERFORMANCE COMMENT",
            align="L", new_x="LMARGIN", new_y="NEXT"
        )

def _build_signatures():
    line = "_" * 32
    table = Table([[line, line], ["Teacher's Signature", "Principal's Signature"]],
                  colWidths=[8.0 * cm, 8.0 * cm])
    table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 1), (-1, 1), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 28),
    ]))
    return [Spacer(1, 10), table]

        # Display the comment underlined on regular lines inside the letterhead's box.
        self.set_x(30)
        self.set_font("Helvetica", "U", 9)
        self.set_text_color(35, 35, 45)
        self.multi_cell(150, 5.5, academic_comment, align="L")

    # Generate the student's PDF report saved strictly by student ID.
    def generate_report(self, report_data):

        # Ensure the reports folder exists before saving.
        makedirs("reports", exist_ok=True)

        # Save dynamically as <student_id>.pdf.
        student_id = report_data["student"]["person_id"]
        file_name = f"{student_id}.pdf"

# ---------- Public function ----------
def generate_report_card(report_data, comment=None, output_folder=None):
    """Builds the PDF report card and returns the path of the saved file.

    report_data    the dictionary from ReportService.prepare_report(student_id)
    comment        optional teacher's comment; when left out, one is written
                   from the student's overall average
    output_folder  where to save; defaults to the reports folder

    Raises ValueError if report_data is not a dictionary. prepare_report()
    returns a text message instead of a dictionary when something is wrong
    (for example "Student not found."), and that message is used as the error."""
    if not isinstance(report_data, dict):
        raise ValueError(str(report_data))

    student = report_data["student"]
    summary = summarize(report_data)
    if comment:
        summary["comment"] = comment

    folder = output_folder or REPORTS_FOLDER
    os.makedirs(folder, exist_ok=True)  # creates the reports folder if it is missing
        # Store the academic year, term and final average.
        self.academic_year = report_data["academic_year"]
        self.academic_term = report_data["academic_term"]
        self.final_average = report_data["final_average"]

        # Add a new page to the PDF.
        self.add_page()

        # Add the school letterhead and information.
        self.add_school_heading()

        # Add the student's information.
        self.add_student_information(report_data["student"])

        # Add the academic results table heading.
        self.add_table_header()

    styles = _styles()
    story = []
    story += _build_header(styles)
    story += _build_student_info(student, styles, generated_on)
    story += _build_grades_table(summary, styles)
    story += _build_summary(summary, styles)
    story += _build_comment(summary["comment"], styles)
    story += _build_signatures()
        # Add the student's subject grades.
        self.add_table_rows(report_data["subjects"])

        # Add the automated academic comment.
        self.add_academic_comment(report_data["academic_comment"])

if __name__ == "__main__":
    # Quick test with data in the same shape ReportService.prepare_report() returns.
    # Run with:  python -m utils.pdf_generator
    sample_report = {
        "student": {
            "person_id": "S002", "first_name": "Saraijah", "last_name": "Porth",
            "email": "saraijah@email.com", "date_of_birth": None, "gender": "Female",
            "grade_level": 11, "parent_contact": None,
        },
        "subjects": [
            {"subject_name": "Mathematics", "coursework": 80, "project": 90,
             "midterm": 70, "final_exam": 85, "final_grade": 81.5},
            {"subject_name": "English Language", "coursework": 60, "project": 60,
             "midterm": 60, "final_exam": 60, "final_grade": 60.0},
            {"subject_name": "Information Technology", "coursework": 95, "project": 92,
             "midterm": 90, "final_exam": 94, "final_grade": 93.1},
        ],
    }
    print("Saved:", generate_report_card(sample_report))
        # Save the PDF report to the reports folder and return the saved path.
        output_path = path.join("reports", file_name)
        self.output(output_path)
        return output_path

