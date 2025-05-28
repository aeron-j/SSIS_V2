import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database.mysql_db import MySQLDatabase
from utils.validation import validate_id_format
from .widgets import ValidatedEntry, LabelInput
from .college_manager import CollegeManager
from .course_manager import CourseManager

class MainWindow:
    def __init__(self, root, db):
        self.root = root
        self.db = MySQLDatabase()
        self.setup_ui()
        self.load_initial_data()
        
    def setup_ui(self):
        self.root.title("Student Data")
        self.root.geometry("1400x600")
        self.root.configure(bg="#8B0000")
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#8B0000")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel (Control frame)
        self.control_frame = tk.Frame(main_frame, bg="#8B0000", width=150)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.control_frame.pack_propagate(False)
        
        # Button styling to match image
        button_style = {
            'bg': '#A0522D',
            'fg': 'white',
            'font': ('Arial', 9),
            'width': 15,
            'height': 1,
            'relief': 'raised',
            'bd': 2
        }
        
        # Add buttons
        tk.Button(self.control_frame, text="Add Student", command=self.add_student, **button_style).pack(pady=5, padx=5)
        tk.Button(self.control_frame, text="Delete Student", command=self.delete_student, **button_style).pack(pady=5, padx=5)
        tk.Button(self.control_frame, text="Update Student", command=self.update_student, **button_style).pack(pady=5, padx=5)
        
        # Search controls
        tk.Label(self.control_frame, text="Search by:", bg="#8B0000", fg="white", font=('Arial', 9)).pack(pady=(15, 5))
        
        self.search_var = tk.StringVar(value="ID#")
        search_by = ttk.Combobox(
            self.control_frame, 
            textvariable=self.search_var,
            values=["ID#", "First Name", "Last Name"],
            state='readonly',
            width=12,
            font=('Arial', 8)
        )
        search_by.pack(pady=2)
        
        self.entry_search = tk.Entry(self.control_frame, width=15, font=('Arial', 8))
        self.entry_search.bind("<KeyRelease>", self.search_student)
        self.entry_search.pack(pady=5)
        
        # Clear Data button (matching the image)
        tk.Button(self.control_frame, text="Clear Data", **button_style).pack(pady=10, padx=5)
        
        # Management buttons
        tk.Button(self.control_frame, text="Manage Colleges", command=self.open_college_manager, **button_style).pack(pady=5, padx=5)
        tk.Button(self.control_frame, text="Manage Courses", command=self.open_course_manager, **button_style).pack(pady=5, padx=5)
        
        # Right panel (Table frame)
        self.table_frame = tk.Frame(main_frame, bg="#8B0000")
        self.table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Filter and sort controls
        self.setup_filter_sort_controls()
        
        # Student table
        self.setup_student_table()
        
        # Pagination controls
        self.setup_pagination()
        
    def setup_filter_sort_controls(self):
        # Controls frame
        controls_frame = tk.Frame(self.table_frame, bg="#8B0000", height=80)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        controls_frame.pack_propagate(False)
        
        # Filter controls frame
        filter_frame = tk.Frame(controls_frame, bg="#8B0000")
        filter_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(filter_frame, text="Filter by:", bg="#8B0000", fg="white", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.college_var = tk.StringVar()
        self.college_filter = ttk.Combobox(
            filter_frame,
            textvariable=self.college_var,
            values=["All Colleges"],
            state='readonly', 
            width=25,
            font=('Arial', 8)
        )
        self.college_filter.pack(side=tk.LEFT, padx=2)
        
        self.year_var = tk.StringVar()
        self.year_filter = ttk.Combobox(
            filter_frame, 
            textvariable=self.year_var,
            values=["All Years", "1st", "2nd", "3rd", "4th", "5+"],
            state='readonly',
            width=10,
            font=('Arial', 8)
        )
        self.year_filter.set("All Years")
        self.year_filter.pack(side=tk.LEFT, padx=2)
        
        self.gender_var = tk.StringVar()
        self.gender_filter = ttk.Combobox(
            filter_frame, 
            textvariable=self.gender_var,
            values=["All Genders", "Male", "Female", "Others"],
            state='readonly',
            width=12,
            font=('Arial', 8)
        )
        self.gender_filter.set("All Genders")
        self.gender_filter.pack(side=tk.LEFT, padx=2)
        
        # Filter buttons
        filter_button_style = {
            'bg': '#A0522D',
            'fg': 'white',
            'font': ('Arial', 8),
            'relief': 'raised',
            'bd': 1,
            'padx': 8,
            'pady': 2
        }
        
        tk.Button(
            filter_frame, 
            text="Apply Filters", 
            command=self.apply_filters,
            **filter_button_style
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            filter_frame, 
            text="Clear Filters", 
            command=self.clear_filters,
            **filter_button_style
        ).pack(side=tk.LEFT, padx=2)
        
        # Sort controls frame
        sort_frame = tk.Frame(controls_frame, bg="#8B0000")
        sort_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(sort_frame, text="Sort by:", bg="#8B0000", fg="white", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.primary_sort = ttk.Combobox(
            sort_frame, 
            values=["Original Order", "ID#", "First Name", "Last Name", "Age", "Gender", "Year Level", "College", "Course"],
            state="readonly",
            width=15,
            font=('Arial', 8)
        )
        self.primary_sort.set("Original Order")
        self.primary_sort.pack(side=tk.LEFT, padx=2)
        
        self.sort_order = ttk.Combobox(
            sort_frame, 
            values=["Ascending", "Descending"],
            state="readonly",
            width=10,
            font=('Arial', 8)
        )
        self.sort_order.set("Ascending")
        self.sort_order.pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            sort_frame, 
            text="Apply Sort", 
            command=self.apply_sort,
            **filter_button_style
        ).pack(side=tk.LEFT, padx=2)
    
    def setup_student_table(self):
        # Table container
        table_container = tk.Frame(self.table_frame, bg="#8B0000")
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID#", "First Name", "Last Name", "Age", "Gender", "Year Level", "College", "Course")
        self.table = ttk.Treeview(table_container, columns=columns, show="headings", height=20)
        
        # Configure column widths to match image
        column_widths = {
            "ID#": 80, 
            "First Name": 120, 
            "Last Name": 120, 
            "Age": 60, 
            "Gender": 80, 
            "Year Level": 90, 
            "College": 80, 
            "Course": 80
        }
        
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.table.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.table.xview)
        self.table.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double click to clear selection
        self.table.bind("<Double-1>", lambda e: self.table.selection_remove(self.table.selection()))
    
    def setup_pagination(self):
        pagination_frame = tk.Frame(self.table_frame, bg="#8B0000", height=30)
        pagination_frame.pack(fill=tk.X, pady=(5, 0))
        pagination_frame.pack_propagate(False)
        
        # Pagination button style
        pagination_style = {
            'bg': '#A0522D',
            'fg': 'white',
            'font': ('Arial', 8),
            'width': 3,
            'height': 1,
            'relief': 'raised',
            'bd': 1
        }
        
        self.btn_first = tk.Button(
            pagination_frame, 
            text="<<", 
            command=lambda: self.go_to_page(1),
            **pagination_style
        )
        self.btn_first.pack(side=tk.LEFT, padx=2)
        
        self.btn_prev = tk.Button(
            pagination_frame, 
            text="<", 
            command=lambda: self.go_to_page(self.current_page - 1),
            **pagination_style
        )
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        
        self.page_info = tk.Label(
            pagination_frame, 
            text="Page 1 of 1 | Total: 0 students", 
            bg="#8B0000", 
            fg="white",
            font=('Arial', 9)
        )
        self.page_info.pack(side=tk.LEFT, padx=10)
        
        self.btn_next = tk.Button(
            pagination_frame, 
            text=">", 
            command=lambda: self.go_to_page(self.current_page + 1),
            **pagination_style
        )
        self.btn_next.pack(side=tk.LEFT, padx=2)
        
        self.btn_last = tk.Button(
            pagination_frame, 
            text=">>", 
            command=lambda: self.go_to_page(self.total_pages),
            **pagination_style
        )
        self.btn_last.pack(side=tk.LEFT, padx=2)
        
        # Initialize pagination variables
        self.current_page = 1
        self.rows_per_page = 20
        self.total_pages = 1
    
    def load_initial_data(self):
        # Load colleges for filter dropdown
        colleges = self.db.get_colleges()
        college_values = ["All Colleges"] + [f"{col['college_code']} - {col['college_name']}" for col in colleges]
        self.college_filter['values'] = college_values
        
        # Load initial student data
        self.refresh_table()
    
    def refresh_table(self, students=None):
        if students is None:
            filters = self.get_current_filters()
            students = self.db.get_students(filters)
        
        self.table.delete(*self.table.get_children())
        
        # Calculate pagination
        self.total_pages = max(1, (len(students) + self.rows_per_page - 1) // self.rows_per_page)
        self.current_page = min(self.current_page, self.total_pages)
        
        start_idx = (self.current_page - 1) * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(students))
        
        for student in students[start_idx:end_idx]:
            college_display = "N/A"
            if student['college_code']:
                college_display = student['college_code']
                
            # Handle course display
            course_display = "N/A"
            if student['course_code']:
                course_display = student['course_code']
                
            display_values = (
                student['student_id'],
                student['first_name'],
                student['last_name'],
                student['age'],
                student['gender'],
                student['year_level'],
                college_display,
                course_display
            )
            self.table.insert("", "end", values=display_values)
        
        self.update_pagination_info(len(students))
    
    def update_pagination_info(self, total_students):
        self.page_info.config(text=f"Page {self.current_page} of {self.total_pages} | Total: {total_students} students")
        
        self.btn_first.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.config(state="normal" if self.current_page < self.total_pages else "disabled")
        self.btn_last.config(state="normal" if self.current_page < self.total_pages else "disabled")
    
    def go_to_page(self, page_num):
        if 1 <= page_num <= self.total_pages:
            self.current_page = page_num
            self.refresh_table()
    
    def get_current_filters(self):
        filters = {}
    
        # College filter
        selected_college = self.college_var.get()
        if selected_college and selected_college != "All Colleges":
            college_code = selected_college.split(' - ')[0]
            filters['college'] = college_code
        
        # Year level filter
        selected_year = self.year_var.get()
        if selected_year and selected_year != "All Years":
            filters['year_level'] = selected_year
        
        # Gender filter
        selected_gender = self.gender_var.get()
        if selected_gender and selected_gender != "All Genders":
            filters['gender'] = selected_gender
        
        # Search filter - modified to use the selected search criteria
        search_text = self.entry_search.get().strip()
        if search_text:
            search_by = self.search_var.get()
            if search_by == "ID#":
                filters['search_id'] = search_text
            elif search_by == "First Name":
                filters['search_first_name'] = search_text
            elif search_by == "Last Name":
                filters['search_last_name'] = search_text
        
        # Sort options
        sort_by = self.primary_sort.get()
        if sort_by and sort_by != "Original Order":
            # Map display names to database column names
            sort_mapping = {
                "ID#": "student_id",
                "First Name": "first_name",
                "Last Name": "last_name",
                "Age": "age",
                "Gender": "gender",
                "Year Level": "year_level",
                "College": "college_code",
                "Course": "course_code"
            }
            filters['sort_by'] = sort_mapping.get(sort_by, "last_name")
            filters['sort_order'] = self.sort_order.get()
        
        return filters
    
    def apply_filters(self):
        self.current_page = 1
        self.refresh_table()
    
    def clear_filters(self):
        self.college_var.set("")
        self.year_var.set("All Years")
        self.gender_var.set("All Genders")
        self.entry_search.delete(0, tk.END)
        self.primary_sort.set("Original Order")
        self.sort_order.set("Ascending")
        self.current_page = 1
        self.refresh_table()
    
    def apply_sort(self):
        self.refresh_table()
    
    def search_student(self, event=None):
        self.current_page = 1
        self.refresh_table()
    
    def add_student(self):
        add_dialog = tk.Toplevel(self.root)
        add_dialog.title("Add New Student")
        add_dialog.geometry("450x300")
        add_dialog.transient(self.root)
        add_dialog.grab_set()

        # ID Number
        tk.Label(add_dialog, text="ID# (YYYY-NNNN):").grid(row=0, column=0, padx=5, pady=5)
        id_entry = ValidatedEntry(add_dialog, validate_type="id")
        id_entry.grid(row=0, column=1, padx=5, pady=5)

        # First Name
        tk.Label(add_dialog, text="First Name:").grid(row=1, column=0, padx=5, pady=5)
        first_name_entry = ValidatedEntry(add_dialog, validate_type="text")
        first_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Last Name
        tk.Label(add_dialog, text="Last Name:").grid(row=2, column=0, padx=5, pady=5)
        last_name_entry = ValidatedEntry(add_dialog, validate_type="text")
        last_name_entry.grid(row=2, column=1, padx=5, pady=5)

        # Age
        tk.Label(add_dialog, text="Age:").grid(row=3, column=0, padx=5, pady=5)
        age_entry = tk.Entry(add_dialog)
        age_entry.grid(row=3, column=1, padx=5, pady=5)

        # Gender
        tk.Label(add_dialog, text="Gender:").grid(row=4, column=0, padx=5, pady=5)
        gender_var = tk.StringVar()
        gender_dropdown = ttk.Combobox(add_dialog, textvariable=gender_var, 
                                    values=["Male", "Female", "Others"], state='readonly')
        gender_dropdown.grid(row=4, column=1, padx=5, pady=5)

        # Year Level
        tk.Label(add_dialog, text="Year Level:").grid(row=5, column=0, padx=5, pady=5)
        year_var = tk.StringVar()
        year_dropdown = ttk.Combobox(add_dialog, textvariable=year_var, 
                                    values=["1st", "2nd", "3rd", "4th", "5+"], state='readonly')
        year_dropdown.grid(row=5, column=1, padx=5, pady=5)

        # College
        tk.Label(add_dialog, text="College:").grid(row=6, column=0, padx=5, pady=5)
        college_var = tk.StringVar()
        colleges = self.db.get_colleges()
        college_options = [f"{col['college_code']} - {col['college_name']}" for col in colleges]
        college_dropdown = ttk.Combobox(add_dialog, textvariable=college_var, 
                                    values=college_options, state='readonly')
        college_dropdown.grid(row=6, column=1, padx=5, pady=5)

        # Course - Will be populated based on college selection
        tk.Label(add_dialog, text="Course:").grid(row=7, column=0, padx=5, pady=5)
        course_var = tk.StringVar()
        course_dropdown = ttk.Combobox(add_dialog, textvariable=course_var, state='readonly')
        course_dropdown.grid(row=7, column=1, padx=5, pady=5)

        def update_courses(*args):
            selected_college = college_var.get()
            if not selected_college:
                course_dropdown['values'] = []
                return
            
            college_code = selected_college.split(' - ')[0]
            courses = self.db.get_courses_by_college(college_code)
            course_options = [f"{course['course_code']} - {course['course_name']}" for course in courses]
            course_dropdown['values'] = course_options

        college_var.trace('w', update_courses)

        def save_student():
            # Get all values
            student_id = id_entry.get()
            first_name = first_name_entry.get().strip().upper()
            last_name = last_name_entry.get().strip().upper()
            age = age_entry.get()
            gender = gender_var.get()
            year_level = year_var.get()
            college = college_var.get()
            course = course_var.get()

            # Validation
            if not all([student_id, first_name, last_name, age, gender, year_level, college, course]):
                messagebox.showerror("Error", "All fields are required", parent=add_dialog)
                return

            if not validate_id_format(student_id, parent=add_dialog):
                return

            try:
                age = int(age)
                if age <= 0 or age > 120:
                    messagebox.showerror("Error", "Age must be between 1 and 120", parent=add_dialog)
                    return
            except ValueError:
                messagebox.showerror("Error", "Age must be a number", parent=add_dialog)
                return

            # Check if student ID already exists
            existing = self.db.execute_query(
                "SELECT student_id FROM students WHERE student_id = %s",
                (student_id,),
                fetch=True
            )
            if existing:
                messagebox.showerror("Error", "Student ID already exists", parent=add_dialog)
                return

            # Extract college and course codes
            college_code = college.split(' - ')[0]
            course_code = course.split(' - ')[0]

            # Prepare student data
            student_data = (
                student_id,
                first_name,
                last_name,
                age,
                gender,
                year_level,
                college_code,
                course_code
            )

            # Save to database
            if self.db.add_student(student_data):
                messagebox.showinfo("Success", "Student added successfully", parent=add_dialog)
                self.refresh_table()
                add_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add student", parent=add_dialog)

        tk.Button(add_dialog, text="Save", command=save_student).grid(row=8, column=0, columnspan=2, pady=10)

    
    def update_student(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a student to update.")
            return

        # Get current student data
        student_id = self.table.item(selected_item)['values'][0]
        student_data = self.db.execute_query(
            "SELECT * FROM students WHERE student_id = %s",
            (student_id,),
            fetch=True
        )
        
        if not student_data:
            messagebox.showerror("Error", "Student not found")
            return
        
        student_data = student_data[0]

        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Update Student")
        edit_dialog.geometry("450x300")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()

        # ID Number (read-only)
        tk.Label(edit_dialog, text="ID# (YYYY-NNNN):").grid(row=0, column=0, padx=5, pady=5)
        id_entry = ValidatedEntry(edit_dialog, validate_type="id")
        id_entry.insert(0, student_data['student_id'])
        id_entry.grid(row=0, column=1, padx=5, pady=5)

        # First Name
        tk.Label(edit_dialog, text="First Name:").grid(row=1, column=0, padx=5, pady=5)
        first_name_entry = ValidatedEntry(edit_dialog, validate_type="text")
        first_name_entry.insert(0, student_data['first_name'])
        first_name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Last Name
        tk.Label(edit_dialog, text="Last Name:").grid(row=2, column=0, padx=5, pady=5)
        last_name_entry = ValidatedEntry(edit_dialog, validate_type="text")
        last_name_entry.insert(0, student_data['last_name'])
        last_name_entry.grid(row=2, column=1, padx=5, pady=5)

        # Age
        tk.Label(edit_dialog, text="Age:").grid(row=3, column=0, padx=5, pady=5)
        age_entry = tk.Entry(edit_dialog)
        age_entry.insert(0, student_data['age'])
        age_entry.grid(row=3, column=1, padx=5, pady=5)

        # Gender
        tk.Label(edit_dialog, text="Gender:").grid(row=4, column=0, padx=5, pady=5)
        gender_var = tk.StringVar(value=student_data['gender'])
        gender_dropdown = ttk.Combobox(edit_dialog, textvariable=gender_var, 
                                    values=["Male", "Female", "Others"], state='readonly')
        gender_dropdown.grid(row=4, column=1, padx=5, pady=5)

        # Year Level
        tk.Label(edit_dialog, text="Year Level:").grid(row=5, column=0, padx=5, pady=5)
        year_var = tk.StringVar(value=student_data['year_level'])
        year_dropdown = ttk.Combobox(edit_dialog, textvariable=year_var, 
                                    values=["1st", "2nd", "3rd", "4th", "5+"], state='readonly')
        year_dropdown.grid(row=5, column=1, padx=5, pady=5)

        # College
        tk.Label(edit_dialog, text="College:").grid(row=6, column=0, padx=5, pady=5)
        college_var = tk.StringVar()
        colleges = self.db.get_colleges()
        college_options = [f"{col['college_code']} - {col['college_name']}" for col in colleges]
        college_dropdown = ttk.Combobox(edit_dialog, textvariable=college_var, 
                                    values=college_options, state='readonly')
        
        # Set current college if exists
        if student_data['college_code']:
            current_college = next(
                (f"{col['college_code']} - {col['college_name']}" 
                for col in colleges 
                if col['college_code'] == student_data['college_code']),
                None
            )
            if current_college:
                college_var.set(current_college)
        
        college_dropdown.grid(row=6, column=1, padx=5, pady=5)

        # Course
        tk.Label(edit_dialog, text="Course:").grid(row=7, column=0, padx=5, pady=5)
        course_var = tk.StringVar()
        course_dropdown = ttk.Combobox(edit_dialog, textvariable=course_var, state='readonly')
        
        # Set current course if exists
        if student_data['course_code'] and student_data['college_code']:
            courses = self.db.get_courses_by_college(student_data['college_code'])
            current_course = next(
                (f"{course['course_code']} - {course['course_name']}" 
                for course in courses 
                if course['course_code'] == student_data['course_code']),
                None
            )
            if current_course:
                course_var.set(current_course)
        
        course_dropdown.grid(row=7, column=1, padx=5, pady=5)

        def update_courses(*args):
            selected_college = college_var.get()
            if not selected_college:
                course_dropdown['values'] = []
                return
            
            college_code = selected_college.split(' - ')[0]
            courses = self.db.get_courses_by_college(college_code)
            course_options = [f"{course['course_code']} - {course['course_name']}" for course in courses]
            course_dropdown['values'] = course_options

        college_var.trace('w', update_courses)

        def save_changes():
            new_student_id = id_entry.get()
            first_name = first_name_entry.get().strip().upper()
            last_name = last_name_entry.get().strip().upper()
            age = age_entry.get()
            gender = gender_var.get()
            year_level = year_var.get()
            college = college_var.get()
            course = course_var.get()

            # Validation
            if not all([new_student_id, first_name, last_name, age, gender, year_level, college, course]):
                messagebox.showerror("Error", "All fields are required", parent=edit_dialog)
                return

            if not validate_id_format(new_student_id, parent=edit_dialog):
                return

            try:
                age = int(age)
                if age <= 0 or age > 120:
                    messagebox.showerror("Error", "Age must be between 1 and 120", parent=edit_dialog)
                    return
            except ValueError:
                messagebox.showerror("Error", "Age must be a number", parent=edit_dialog)
                return

            # Check if new student ID already exists (and it's not the current student's ID)
            if new_student_id != student_data['student_id']:
                existing = self.db.execute_query(
                    "SELECT student_id FROM students WHERE student_id = %s",
                    (new_student_id,),
                    fetch=True
                )
                if existing:
                    messagebox.showerror("Error", "Student ID already exists", parent=edit_dialog)
                    return

            # Extract college and course codes
            college_code = college.split(' - ')[0]
            course_code = course.split(' - ')[0]

            # Prepare updated student data
            updated_data = (
                new_student_id,
                first_name,
                last_name,
                age,
                gender,
                year_level,
                college_code,
                course_code
            )

            try:
                if self.db.update_student(student_data['student_id'], updated_data):
                    messagebox.showinfo("Success", "Student updated successfully", parent=edit_dialog)
                    self.refresh_table()
                    edit_dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update student", parent=edit_dialog)
            except Exception as e:
                messagebox.showerror("Database Error", f"Error updating student: {str(e)}", parent=edit_dialog)

        tk.Button(edit_dialog, text="Save Changes", command=save_changes).grid(row=8, column=0, columnspan=2, pady=10)
    
    def delete_student(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a student to delete.")
            return
        
        student_id = self.table.item(selected_item)['values'][0]
        
        confirm = messagebox.askyesno("Delete Confirmation", "Are you sure you want to delete this student?")
        if confirm:
            if self.db.delete_student(student_id):
                self.refresh_table()
                messagebox.showinfo("Success", "Student deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete student")
    
    def open_college_manager(self):
        CollegeManager(self.root, self.db, self)
    
    def open_course_manager(self):
        CourseManager(self.root, self.db, self)
    
    def refresh_filter_values(self):
        colleges = self.db.get_colleges()
        college_values = ["All Colleges"] + [f"{col['college_code']} - {col['college_name']}" for col in colleges]
        self.college_filter['values'] = college_values
        self.college_filter.set("All Colleges")