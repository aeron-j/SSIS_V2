import tkinter as tk
from tkinter import messagebox
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

try:
    from gui.main_window import MainWindow
except ImportError:
    print("GUI module not found. Creating a simple test interface...")
    MainWindow = None

from database.mysql_db import MySQLDatabase
from config import DB_CONFIG

def initialize_database():
    db = MySQLDatabase()
    
    try:
        result = db.execute_query("SELECT 1 FROM colleges LIMIT 1", fetch=True)
        if result is False:  
            raise Exception("Could not access colleges table")
            
        result = db.execute_query("SELECT 1 FROM courses LIMIT 1", fetch=True)
        if result is False:  
            raise Exception("Could not access courses table")
            
        result = db.execute_query("SELECT 1 FROM students LIMIT 1", fetch=True)
        if result is False:  
            raise Exception("Could not access students table")
            
        print("Database validation successful")
        
    except Exception as e:
        print(f"Database validation failed: {e}")
        if messagebox.askyesno(
            "Database Error",
            "Required tables not found. Create new database structure?"
        ):
            from database.setup import setup_database
            if setup_database():
                print("Database setup completed")
            else:
                raise Exception("Database setup failed")
        else:
            raise Exception("Database validation failed and user declined setup")
    finally:
        db.close()

def create_simple_test_window(db):
    """Create a simple test window if the main GUI is not available"""
    root = tk.Tk()
    root.title("Student Management System - Test Mode")
    root.geometry("600x400")
    
    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(fill=tk.BOTH, expand=True)
    
    tk.Label(frame, text="Student Management System", font=("Arial", 16, "bold")).pack(pady=10)
    
    def test_colleges():
        colleges = db.get_colleges()
        if colleges:
            result = f"Found {len(colleges)} colleges:\n"
            for college in colleges[:5]:  
                result += f"- {college['college_code']}: {college['college_name']}\n"
            messagebox.showinfo("Colleges", result)
        else:
            messagebox.showwarning("Colleges", "No colleges found")
    
    def test_courses():
        courses = db.get_all_courses()
        if courses:
            result = f"Found {len(courses)} courses:\n"
            for course in courses[:5]:  
                result += f"- {course['course_code']}: {course['course_name']}\n"
            messagebox.showinfo("Courses", result)
        else:
            messagebox.showwarning("Courses", "No courses found")
    
    def test_students():
        students = db.get_students()
        if students:
            result = f"Found {len(students)} students:\n"
            for student in students[:5]:  
                result += f"- {student['student_id']}: {student['first_name']} {student['last_name']}\n"
            messagebox.showinfo("Students", result)
        else:
            messagebox.showwarning("Students", "No students found")
    
    tk.Button(frame, text="Test Colleges", command=test_colleges, width=20).pack(pady=5)
    tk.Button(frame, text="Test Courses", command=test_courses, width=20).pack(pady=5)
    tk.Button(frame, text="Test Students", command=test_students, width=20).pack(pady=5)
    
    tk.Label(frame, text="\nDatabase connection successful!", fg="green").pack(pady=10)
    tk.Label(frame, text="The main GUI module was not found, but the database is working.").pack()
    
    return root

def main():
    try:
        initialize_database()
        
        root = tk.Tk()
        root.title(DB_CONFIG.get('app_name', 'Student Management System'))
        
        try:
            icon = tk.PhotoImage(file='assets/icon.png')
            root.iconphoto(True, icon)
        except:
            pass  

        
        db = MySQLDatabase()
        
        
        if MainWindow:
            app = MainWindow(root, db)
        else:
            root.destroy()
            root = create_simple_test_window(db)
        
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to exit the application?"):
                if 'db' in locals():
                    db.close()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        messagebox.showerror(
            "Startup Error",
            f"Failed to start application:\n{str(e)}"
        )
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()