import re
from tkinter import messagebox

def validate_id_format(id_no, field_name="ID#", parent=None):
    if not re.match(r'^\d{4}-\d{4}$', id_no):
        messagebox.showerror("Invalid Format", f"{field_name} must be in the format YYYY-NNNN", parent=parent)
        return False
    return True

def validate_text_only(text, field_name):
    if any(char.isdigit() for char in text):
        messagebox.showerror("Invalid Input", f"{field_name} must not contain numbers")
        return False
    return True

def validate_college_code(code):
    if not code.isalpha():
        messagebox.showerror("Invalid Format", "College code must contain only letters")
        return False
    return True

def validate_college_name(name):
    return validate_text_only(name, "College name")

def validate_course_code(code):
    if not re.match(r'^[A-Z0-9\-]+$', code):
        messagebox.showerror("Invalid Format", 
                           "Course code must contain only letters, numbers, and hyphens")
        return False
    return True

def validate_course_name(name):
    return validate_text_only(name, "Course name")

def validate_age(age):
    try:
        age_num = int(age)
        if age_num <= 0 or age_num > 120:
            messagebox.showerror("Invalid Age", "Age must be between 1 and 120")
            return False
        return True
    except ValueError:
        messagebox.showerror("Invalid Age", "Age must be a number")
        return False