import tkinter as tk
from tkinter import ttk, messagebox
from utils.validation import validate_college_code, validate_college_name

class CollegeManager:
    def __init__(self, parent, db, main_window_ref=None):
        self.parent = parent
        self.db = db
        self.main_window_ref = main_window_ref
        
        self.window = tk.Toplevel(parent)
        self.window.title("College Management")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        tk.Label(main_frame, text="Colleges", font=("Arial", 14, "bold")).pack(pady=10)
        
        # College table
        self.columns = ("College Code", "College Name", "Number of Courses")
        self.college_table = ttk.Treeview(main_frame, columns=self.columns, show="headings", height=15)
        
        for col in self.columns:
            self.college_table.heading(col, text=col)
            self.college_table.column(col, width=150)
        
        self.college_table.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Add College", command=self.add_college).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Edit College", command=self.edit_college).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete College", command=self.delete_college).pack(side=tk.LEFT, padx=5)
        
        # Search and sort controls
        self.setup_search_sort_controls(main_frame)
        
        # Bind click event
        self.college_table.bind("<Button-1>", self.on_click)
        self._last_selected = None
    
    def setup_search_sort_controls(self, parent):
        # Search frame
        search_frame = tk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_var.trace('w', self.on_search_change)
        
        # Sort frame
        sort_frame = tk.Frame(parent)
        sort_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(sort_frame, text="Sort by:").pack(side=tk.LEFT, padx=5)
        self.sort_var = tk.StringVar(value="College Code")
        sort_options = ttk.Combobox(
            sort_frame, 
            textvariable=self.sort_var,
            values=["College Code", "College Name", "Number of Courses"],
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
    
    def on_click(self, event):
        region = self.college_table.identify("region", event.x, event.y)
        if region != "cell":
            return
            
        item = self.college_table.identify_row(event.y)
        if not item:
            return
            
        if item == self._last_selected:
            self.college_table.selection_remove(item)
            self._last_selected = None
        else:
            self._last_selected = item
    
    def on_search_change(self, *args):
        self.refresh_table()
    
    def apply_sort(self):
        self.refresh_table()
    
    def refresh_table(self):
        self.college_table.delete(*self.college_table.get_children())
        
        try:
            # Get colleges with course counts
            query = """
            SELECT c.college_code, c.college_name, COUNT(co.course_code) as course_count
            FROM colleges c
            LEFT JOIN courses co ON c.college_code = co.college_code
            GROUP BY c.college_code, c.college_name
            """
            
            colleges = self.db.execute_query(query, fetch=True)
            
            # Apply search filter
            search_text = self.search_var.get().lower()
            if search_text:
                colleges = [
                    c for c in colleges 
                    if (search_text in c['college_code'].lower() or 
                        search_text in c['college_name'].lower())
                ]
            
            # Apply sorting
            sort_by = self.sort_var.get()
            reverse = self.sort_order.get() == "Descending"
            
            if sort_by == "College Code":
                colleges.sort(key=lambda x: x['college_code'], reverse=reverse)
            elif sort_by == "College Name":
                colleges.sort(key=lambda x: x['college_name'], reverse=reverse)
            else:  # Number of Courses
                colleges.sort(key=lambda x: x['course_count'], reverse=reverse)
            
            # Populate table
            for college in colleges:
                self.college_table.insert("", "end", values=(
                    college['college_code'],
                    college['college_name'],
                    college['course_count']
                ))
                
        except Exception as e:
            print(f"Error refreshing college table: {e}")
            messagebox.showerror("Error", "Failed to refresh college table")
    
    def add_college(self):
        add_dialog = tk.Toplevel(self.window)
        add_dialog.title("Add New College")
        add_dialog.geometry("400x200")
        add_dialog.transient(self.window)
        add_dialog.grab_set()
        
        tk.Label(add_dialog, text="College Code:").pack(pady=5)
        code_entry = tk.Entry(add_dialog)
        code_entry.pack(pady=5)
        
        tk.Label(add_dialog, text="College Name:").pack(pady=5)
        name_entry = tk.Entry(add_dialog, width=40)
        name_entry.pack(pady=5)
        
        def save():
            code = code_entry.get().strip().upper()
            name = name_entry.get().strip().title()
            
            if not all([code, name]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not validate_college_code(code):
                return
                
            if not validate_college_name(name):
                return
                
            # Check for duplicates
            existing = self.db.execute_query(
                "SELECT college_code FROM colleges WHERE college_code = %s",
                (code,),
                fetch=True
            )
            
            if existing:
                messagebox.showerror("Duplicate", f"College with code {code} already exists")
                return
            
            # Check for duplicate name
            existing_name = self.db.execute_query(
                "SELECT college_name FROM colleges WHERE college_name = %s",
                (name,),
                fetch=True
            )
            
            if existing_name:
                messagebox.showerror("Duplicate", f"College with name {name} already exists")
                return
            
            # Add to database
            if self.db.add_college(code, name):
                messagebox.showinfo("Success", "College added successfully")
                self.refresh_table()
                if self.main_window_ref:
                    self.main_window_ref.refresh_filter_values()
                add_dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add college")
        
        tk.Button(add_dialog, text="Save", command=save).pack(pady=10)
    
    def edit_college(self):
        selected = self.college_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a college to edit.")
            return
            
        values = self.college_table.item(selected)['values']
        if len(values) < 2:
            messagebox.showerror("Error", "Invalid selection data")
            return

        current_code, current_name = values[0], values[1]
        
        edit_dialog = tk.Toplevel(self.window)
        edit_dialog.title("Edit College")
        edit_dialog.geometry("400x200")
        edit_dialog.transient(self.window)
        edit_dialog.grab_set()
        
        tk.Label(edit_dialog, text="College Code:").pack(pady=5)
        code_entry = tk.Entry(edit_dialog)
        code_entry.insert(0, current_code)
        code_entry.pack(pady=5)
        
        tk.Label(edit_dialog, text="College Name:").pack(pady=5)
        name_entry = tk.Entry(edit_dialog, width=40)
        name_entry.insert(0, current_name)
        name_entry.pack(pady=5)
        
        def save():
            new_code = code_entry.get().strip().upper()
            new_name = name_entry.get().strip().title()

            if not all([new_code, new_name]):
                messagebox.showerror("Error", "All fields must be filled")
                return
                
            if not validate_college_code(new_code):
                return
                
            if not validate_college_name(new_name):
                return
                
            if new_code != current_code:
                # Check if new code already exists
                existing = self.db.execute_query(
                    "SELECT college_code FROM colleges WHERE college_code = %s",
                    (new_code,),
                    fetch=True
                )
                
                if existing:
                    messagebox.showerror("Duplicate", f"College with code {new_code} already exists")
                    return
            # Check for duplicate name
            if new_name != current_name:
                existing_name = self.db.execute_query(
                    "SELECT college_name FROM colleges WHERE college_name = %s",
                    (new_name,),
                    fetch=True
                )
                
                if existing_name:
                    messagebox.showerror("Duplicate", f"College with name {new_name} already exists")
                    return
            
            # Update in database
            if self.db.update_college(current_code, new_code, new_name):
                messagebox.showinfo("Success", "College updated successfully", parent=edit_dialog)
                self.refresh_table()
                if self.main_window_ref:
                    self.main_window_ref.refresh_filter_values()
                    self.main_window_ref.refresh_table()  # Add this line to refresh the student table
                edit_dialog.destroy()
            else:
                    messagebox.showerror("Error", "Failed to update college", parent=edit_dialog)
            
        tk.Button(edit_dialog, text="Save Changes", command=save).pack(pady=10)
    
    def delete_college(self):
        selected = self.college_table.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a college to delete.")
            return

        values = self.college_table.item(selected)['values']
        if len(values) < 2:
            messagebox.showerror("Error", "Invalid selection data")
            return

        college_code, college_name = values[0], values[1]
        
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete college '{college_code} - {college_name}'?\n"
            "All courses will be unassigned from this college."
        )
        
        if confirm:
            try:
                # First update students to remove college reference (keep course)
                update_students_query = """
                UPDATE students 
                SET college_code = NULL 
                WHERE college_code = %s
                """
                self.db.execute_query(update_students_query, (college_code,))
                
                # Then update courses to remove college reference
                update_courses_query = """
                UPDATE courses 
                SET college_code = NULL 
                WHERE college_code = %s
                """
                self.db.execute_query(update_courses_query, (college_code,))
                
                # Then delete the college
                delete_query = "DELETE FROM colleges WHERE college_code = %s"
                if self.db.execute_query(delete_query, (college_code,)):
                    messagebox.showinfo(
                        "College Deleted", 
                        f"College '{college_code} - {college_name}' has been deleted.\n"
                        "Courses were unassigned from this college."
                    )
                    self.refresh_table()
                    if self.main_window_ref:
                        self.main_window_ref.refresh_filter_values()
                        self.main_window_ref.refresh_table()
                else:
                    messagebox.showerror("Error", "Failed to delete college")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete college: {str(e)}")