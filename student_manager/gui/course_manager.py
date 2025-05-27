import tkinter as tk
from tkinter import ttk, messagebox
from utils.validation import validate_course_code, validate_course_name

class CourseManager:
    def __init__(self, parent, db, main_window_ref=None):
        self.parent = parent
        self.db = db
        self.main_window_ref = main_window_ref
        self.window = tk.Toplevel(parent)
        self.window.title("Course Management")
        self.window.geometry("800x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Filter controls
        filter_frame = tk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(filter_frame, text="Filter by College:").pack(side=tk.LEFT, padx=5)
        
        self.college_filter_var = tk.StringVar(value="All Colleges")
        self.college_filter = ttk.Combobox(
            filter_frame,
            textvariable=self.college_filter_var,
            values=["All Colleges"],
            state='readonly',
            width=30
        )
        self.college_filter.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            filter_frame, 
            text="Apply Filter", 
            command=self.refresh_table
        ).pack(side=tk.LEFT, padx=5)
        
        # Course table
        self.columns = ("Course Code", "Course Name", "College")
        self.course_table = ttk.Treeview(main_frame, columns=self.columns, show="headings")
        
        for col in self.columns:
            self.course_table.heading(col, text=col)
            if col == "Course Name":
                self.course_table.column(col, width=300)
            else:
                self.course_table.column(col, width=150)
        
        self.course_table.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add Course", command=self.add_course).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit Course", command=self.edit_course).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Course", command=self.delete_course).pack(side=tk.LEFT, padx=5)
        
        # Search and sort controls
        self.setup_search_sort_controls(main_frame)
        
        # Bind click event
        self.course_table.bind("<Button-1>", self.on_click)
        self._last_selected = None
        
        # Load college filter options
        self.load_college_filter_options()

    def setup_search_sort_controls(self, parent):
        # Search frame
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_by_var = tk.StringVar(value="Course Code")
        search_by_options = ttk.Combobox(
            search_frame, 
            textvariable=self.search_by_var,
            values=["Course Code", "Course Name"],
            state='readonly',
            width=15
        )
        search_by_options.pack(side=tk.LEFT, padx=5)
        
        self.search_var.trace('w', self.on_search_change)
        
        # Sort frame
        sort_frame = tk.Frame(parent)
        sort_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="Course Code")
        sort_options = ttk.Combobox(
            sort_frame, 
            textvariable=self.sort_var,
            values=["Course Code", "Course Name", "College"],
            state='readonly',
            width=15
        )
        sort_options.pack(side=tk.LEFT, padx=5)
        
        self.sort_order = tk.StringVar(value="Ascending")
        order_options = ttk.Combobox(
            sort_frame, 
            textvariable=self.sort_order,
            values=["Ascending", "Descending"],
            state='readonly',
            width=10
        )
        order_options.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            sort_frame, 
            text="Apply Sort", 
            command=self.apply_sort
        ).pack(side=tk.LEFT, padx=5)

    def load_college_filter_options(self):
        colleges = self.db.get_colleges()
        college_values = ["All Colleges"] + [f"{col['college_code']} - {col['college_name']}" for col in colleges]
        self.college_filter['values'] = college_values

    def on_click(self, event):
        region = self.course_table.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        item = self.course_table.identify_row(event.y)
        if not item:
            return
            
        if item == self._last_selected:
            self.course_table.selection_remove(item)
            self._last_selected = None
        else:
            self._last_selected = item

    def on_search_change(self, *args):
        self.refresh_table()

    def apply_sort(self):
        self.refresh_table()

    def refresh_table(self):
        self.course_table.delete(*self.course_table.get_children())
        
        try:
            # Get courses with college information
            query = """
            SELECT c.course_code, c.course_name, co.college_code, co.college_name
            FROM courses c
            LEFT JOIN colleges co ON c.college_code = co.college_code
            """
            
            # Apply college filter
            selected_college = self.college_filter_var.get()
            if selected_college and selected_college != "All Colleges":
                college_code = selected_college.split(' - ')[0]
                query += " WHERE c.college_code = %s"
                params = (college_code,)
            else:
                params = None
            
            courses = self.db.execute_query(query, params, fetch=True)
            
            # Apply search filter
            search_text = self.search_var.get().lower()
            search_by = self.search_by_var.get()
            
            if search_text:
                if search_by == "Course Code":
                    courses = [c for c in courses if search_text in c['course_code'].lower()]
                elif search_by == "Course Name":
                    courses = [c for c in courses if search_text in c['course_name'].lower()]
            
            # Apply sorting
            sort_by = self.sort_var.get()
            reverse = self.sort_order.get() == "Descending"
            
            if sort_by == "Course Code":
                courses.sort(key=lambda x: x['course_code'], reverse=reverse)
            elif sort_by == "Course Name":
                courses.sort(key=lambda x: x['course_name'], reverse=reverse)
            else:  # College
                courses.sort(key=lambda x: x['college_name'] or "", reverse=reverse)
            
            # Populate table
            for course in courses:
                self.course_table.insert("", "end", values=(
                    course['course_code'],
                    course['course_name'],
                    f"{course['college_code']} - {course['college_name']}" if course['college_code'] else "N/A"
                ))
                
        except Exception as e:
            print(f"Error refreshing course table: {e}")
            messagebox.showerror("Error", "Failed to refresh course table")

    def add_course(self):
        add_dialog = tk.Toplevel(self.window)
        add_dialog.title("Add New Course")
        add_dialog.geometry("500x250")
        add_dialog.transient(self.window)
        add_dialog.grab_set()
        
        tk.Label(add_dialog, text="Course Code:").pack(pady=5)
        code_entry = tk.Entry(add_dialog)
        code_entry.pack(pady=5)
        
        tk.Label(add_dialog, text="Course Name:").pack(pady=5)
        name_entry = tk.Entry(add_dialog, width=40)
        name_entry.pack(pady=5)
        
        tk.Label(add_dialog, text="Select College:").pack(pady=5)
        
        self.college_var = tk.StringVar()
        colleges = self.db.get_colleges()
        college_options = [f"{col['college_code']} - {col['college_name']}" for col in colleges]
        college_dropdown = ttk.Combobox(
            add_dialog, 
            textvariable=self.college_var,
            values=college_options,
            state='readonly',
            width=40
        )
        college_dropdown.pack(pady=5)
        
        if self.college_filter_var.get() != "All Colleges":
            self.college_var.set(self.college_filter_var.get())
        
        def save():
            code = code_entry.get().strip().upper()
            name = name_entry.get().strip().title()
            college = self.college_var.get()
            
            if not all([code, name, college]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not validate_course_code(code):
                return
                
            if not validate_course_name(name):
                return
                
            college_code = college.split(' - ')[0]
            
            # Check for duplicate course code
            existing = self.db.execute_query(
                "SELECT course_code FROM courses WHERE course_code = %s",
                (code,),
                fetch=True
            )
            
            if existing:
                messagebox.showerror("Duplicate", f"Course with code {code} already exists")
                return
            
            # Add to database
            if self.db.add_course(code, name, college_code):
                messagebox.showinfo("Success", "Course added successfully")
                self.refresh_table()
                if self.main_window_ref:
                    self.main_window_ref.refresh_table()
                add_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add course")
        
        tk.Button(add_dialog, text="Save", command=save).pack(pady=10)

    def edit_course(self):
        selected = self.course_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a course to edit.")
            return
            
        values = self.course_table.item(selected)['values']
        if len(values) < 3:
            messagebox.showerror("Error", "Invalid selection data")
            return

        current_code, current_name, current_college = values
        
        edit_dialog = tk.Toplevel(self.window)
        edit_dialog.title("Edit Course")
        edit_dialog.geometry("500x250")
        edit_dialog.transient(self.window)
        edit_dialog.grab_set()
        
        tk.Label(edit_dialog, text="Course Code:").pack(pady=5)
        code_entry = tk.Entry(edit_dialog)
        code_entry.insert(0, current_code)
        code_entry.pack(pady=5)
        
        tk.Label(edit_dialog, text="Course Name:").pack(pady=5)
        name_entry = tk.Entry(edit_dialog, width=40)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=5)
        
        tk.Label(edit_dialog, text="Select College:").pack(pady=5)
        
        self.college_var = tk.StringVar()
        colleges = self.db.get_colleges()
        college_options = [f"{col['college_code']} - {col['college_name']}" for col in colleges]
        college_dropdown = ttk.Combobox(
            edit_dialog, 
            textvariable=self.college_var,
            values=college_options,
            state='readonly',
            width=40
        )
        college_dropdown.pack(pady=5)
        
        if current_college != "N/A":
            self.college_var.set(current_college)
        
        def save():
            new_code = code_entry.get().strip().upper()
            new_name = name_entry.get().strip().title()
            college = self.college_var.get()
            
            if not all([new_code, new_name, college]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not validate_course_code(new_code):
                return
                
            if not validate_course_name(new_name):
                return
                
            college_code = college.split(' - ')[0]
            
            if new_code != current_code:
                # Check if new code already exists
                existing = self.db.execute_query(
                    "SELECT course_code FROM courses WHERE course_code = %s",
                    (new_code,),
                    fetch=True
                )
                
                if existing:
                    messagebox.showerror("Duplicate", f"Course with code {new_code} already exists")
                    return

            # Update in database
            if self.db.update_course(current_code, new_code, new_name, college_code):
                messagebox.showinfo("Success", "Course updated successfully")
                self.refresh_table()
                if self.main_window_ref:
                    self.main_window_ref.refresh_table()
                edit_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update course")
            
        tk.Button(edit_dialog, text="Save Changes", command=save).pack(pady=10)

    def delete_course(self):
        selected = self.course_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a course to delete.")
            return

        values = self.course_table.item(selected)['values']
        if len(values) < 1:
            messagebox.showerror("Error", "Invalid selection data")
            return

        course_code = values[0]
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete course '{values[0]} - {values[1]}'?"
        )
        
        if confirm:
            if self.db.delete_course(course_code):
                messagebox.showinfo(
                    "Success", 
                    f"Course '{values[0]} - {values[1]}' deleted successfully"
                )
                self.refresh_table()
                if self.main_window_ref:
                    self.main_window_ref.refresh_table()
            else:
                messagebox.showerror("Error", "Failed to delete course")