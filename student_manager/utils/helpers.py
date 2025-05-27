import os
import csv
import re
from config import CSV_FILE, COLLEGE_CSV, COURSE_CSV

def load_college_courses_from_csv():
    college_courses = {}
    college_courses["_orphaned_"] = []
    
    try:
        if os.path.exists(COLLEGE_CSV):
            with open(COLLEGE_CSV, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    if row and len(row) >= 2:
                        code = row[0]
                        name = row[1]
                        college_key = f"{code} - {name}"
                        college_courses[college_key] = []

        if os.path.exists(COURSE_CSV):
            with open(COURSE_CSV, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    if row and len(row) >= 3:
                        course_code = row[0]
                        course_name = row[1]
                        college_code = row[2]
                        course_entry = f"{course_code} - {course_name}"
                        
                        if college_code == "N/A":
                            college_courses["_orphaned_"].append(course_entry)
                        else:
                            college_key = next(
                                (k for k in college_courses if k.startswith(f"{college_code} -")),
                                None
                            )
                            if college_key:
                                college_courses[college_key].append(course_entry)
                            else:
                                college_courses["_orphaned_"].append(course_entry)
    except Exception as e:
        print(f"Error loading data: {e}")
        raise e

    return college_courses

def load_students_from_csv():
    students = []
    try:
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    if row and len(row) >= 8:
                        students.append(tuple(row))
    except Exception as e:
        print(f"Error loading student data: {e}")
        raise e

    return students

def save_students_to_csv(students):
    try:
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Year Level", "College", "Course"])
            writer.writerows(students)
    except Exception as e:
        print(f"Error saving student data: {e}")
        raise e

def save_colleges_to_csv(college_courses):
    try:
        colleges_to_save = []
        for college_key in college_courses:
            parts = college_key.split(' - ', 1)
            if len(parts) == 2:
                code, name = parts
                colleges_to_save.append([code, name])
        
        with open(COLLEGE_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Code", "Name"])
            for college in colleges_to_save:
                writer.writerow(college)
    except Exception as e:
        print(f"Error saving colleges: {e}")
        raise e

def save_courses_to_csv(college_courses):
    try:
        courses_to_save = []
        for college_key, course_list in college_courses.items():
            college_code = college_key.split(' - ', 1)[0] if college_key != "_orphaned_" else "N/A"
            for course_entry in course_list:
                course_parts = course_entry.split(' - ', 1)
                if len(course_parts) == 2:
                    course_code, course_name = course_parts
                    courses_to_save.append([course_code, course_name, college_code])

        with open(COURSE_CSV, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Course Code", "Course Name", "College Code"])
            writer.writerows(courses_to_save)
    except Exception as e:
        print(f"Error saving courses: {e}")
        raise e