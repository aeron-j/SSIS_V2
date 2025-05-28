import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class MySQLDatabase:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            print("MySQL Database connection successful")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            
    def execute_query(self, query, params=None, fetch=False):
        cursor = None
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                return cursor.fetchall()
            
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Error executing query: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
                
    def get_colleges(self):
        query = "SELECT * FROM colleges ORDER BY college_name"
        return self.execute_query(query, fetch=True)
        
    def get_courses_by_college(self, college_code):
        query = """
        SELECT course_code, course_name 
        FROM courses 
        WHERE college_code = %s
        ORDER BY course_name
        """
        return self.execute_query(query, (college_code,), fetch=True)
        
    def get_all_courses(self):
        query = """
        SELECT c.course_code, c.course_name, co.college_name 
        FROM courses c
        JOIN colleges co ON c.college_code = co.college_code
        ORDER BY co.college_name, c.course_name
        """
        return self.execute_query(query, fetch=True)
        
    def get_students(self, filters=None):
        query = """
        SELECT s.*, co.college_name, c.course_name
        FROM students s
        LEFT JOIN colleges co ON s.college_code = co.college_code
        LEFT JOIN courses c ON s.course_code = c.course_code
        """
        
        params = []
        where_clauses = []
        
        if filters:
            if filters.get('college'):
                where_clauses.append("s.college_code = %s")
                params.append(filters['college'])
            if filters.get('year_level'):
                where_clauses.append("s.year_level = %s")
                params.append(filters['year_level'])
            if filters.get('gender'):
                where_clauses.append("s.gender = %s")
                params.append(filters['gender'])
            
            if filters.get('search_id'):
                where_clauses.append("s.student_id LIKE %s")
                params.append(f"%{filters['search_id']}%")
            elif filters.get('search_first_name'):
                where_clauses.append("s.first_name LIKE %s")
                params.append(f"%{filters['search_first_name']}%")
            elif filters.get('search_last_name'):
                where_clauses.append("s.last_name LIKE %s")
                params.append(f"%{filters['search_last_name']}%")
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        if filters and filters.get('sort_by'):
            sort_order = "DESC" if filters.get('sort_order') == "Descending" else "ASC"
            query += f" ORDER BY {filters['sort_by']} {sort_order}"
        else:
            query += " ORDER BY s.last_name, s.first_name"
            
        return self.execute_query(query, params, fetch=True)
        
    def add_student(self, student_data):
        query = """
        INSERT INTO students 
        (student_id, first_name, last_name, age, gender, year_level, college_code, course_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, student_data)
        
    def update_student(self, old_student_id, student_data):
        query = """
        UPDATE students 
        SET student_id = %s, first_name = %s, last_name = %s, age = %s, gender = %s, 
            year_level = %s, college_code = %s, course_code = %s
        WHERE student_id = %s
        """

        params = (*student_data, old_student_id)
        return self.execute_query(query, params)
        
    def delete_student(self, student_id):
        query = "DELETE FROM students WHERE student_id = %s"
        return self.execute_query(query, (student_id,))
        
    def add_college(self, college_code, college_name):
        query = "INSERT INTO colleges (college_code, college_name) VALUES (%s, %s)"
        return self.execute_query(query, (college_code, college_name))
        
    def update_college(self, old_code, college_code, college_name):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            cursor.execute("""
                UPDATE students 
                SET college_code = %s 
                WHERE college_code = %s
            """, (college_code, old_code))
            
            cursor.execute("""
                UPDATE courses 
                SET college_code = %s 
                WHERE college_code = %s
            """, (college_code, old_code))
            
            cursor.execute("""
                UPDATE colleges 
                SET college_code = %s, college_name = %s 
                WHERE college_code = %s
            """, (college_code, college_name, old_code))
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Error updating college: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()

        
    def delete_college(self, college_code):
        try:
            update_students_query = """
            UPDATE students 
            SET college_code = NULL 
            WHERE college_code = %s
            """
            self.execute_query(update_students_query, (college_code,))
            
            update_courses_query = """
            UPDATE courses 
            SET college_code = NULL 
            WHERE college_code = %s
            """
            self.execute_query(update_courses_query, (college_code,))
            
            delete_query = "DELETE FROM colleges WHERE college_code = %s"
            return self.execute_query(delete_query, (college_code,))
        except Exception as e:
            print(f"Error deleting college: {e}")
            return False
        
    def add_course(self, course_code, course_name, college_code):
        query = """
        INSERT INTO courses (course_code, course_name, college_code)
        VALUES (%s, %s, %s)
        """
        return self.execute_query(query, (course_code, course_name, college_code))
        
    def update_course(self, old_code, course_code, course_name, college_code):
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            cursor.execute("""
                UPDATE students 
                SET course_code = %s 
                WHERE course_code = %s
            """, (course_code, old_code))
            
            cursor.execute("""
                UPDATE courses 
                SET course_code = %s, course_name = %s, college_code = %s
                WHERE course_code = %s
            """, (course_code, course_name, college_code, old_code))
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            
            self.connection.commit()
            return True
            
        except Error as e:
            print(f"Error updating course: {e}")
            self.connection.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
        
    def delete_course(self, course_code):
        update_query = """
        UPDATE students 
        SET course_code = NULL 
        WHERE course_code = %s
        """
        self.execute_query(update_query, (course_code,))
        
        delete_query = "DELETE FROM courses WHERE course_code = %s"
        return self.execute_query(delete_query, (course_code,))
    
    def clear_all_students(self):
        """Delete all student records from the database"""
        query = "DELETE FROM students"
        return self.execute_query(query)
        
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            