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

        # Add the student's subject grades.
        self.add_table_rows(report_data["subjects"])

        # Add the automated academic comment.
        self.add_academic_comment(report_data["academic_comment"])

        # Save the PDF report to the reports folder and return the saved path.
        output_path = path.join("reports", file_name)
        self.output(output_path)
        return output_path