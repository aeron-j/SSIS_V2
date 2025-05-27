import sys
import os

# Add the parent directory to the Python path to find config module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_CONFIG
import mysql.connector
from mysql.connector import Error

def setup_database():
    try:
        # Connect without specifying a database
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
            print(f"Database {DB_CONFIG['database']} created successfully")
            
            # Switch to the database
            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # Create colleges table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS colleges (
                college_code VARCHAR(10) PRIMARY KEY,
                college_name VARCHAR(100) NOT NULL
            )
            """)
            print("Colleges table created successfully")
            
            # Create courses table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                course_code VARCHAR(20) PRIMARY KEY,
                course_name VARCHAR(100) NOT NULL,
                college_code VARCHAR(10),
                FOREIGN KEY (college_code) REFERENCES colleges(college_code)
            )
            """)
            print("Courses table created successfully")
            
            # Create students table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(20) PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                age INT NOT NULL,
                gender ENUM('Male', 'Female', 'Others') NOT NULL,
                year_level ENUM('1st', '2nd', '3rd', '4th', '5+') NOT NULL,
                college_code VARCHAR(10),
                course_code VARCHAR(20),
                FOREIGN KEY (college_code) REFERENCES colleges(college_code) ON DELETE SET NULL,
                FOREIGN KEY (course_code) REFERENCES courses(course_code) ON DELETE SET NULL
            )
            """)
            print("Students table created successfully")
            
            connection.commit()
            
            # Close cursor and connection
            cursor.close()
            connection.close()
            
            print("Database setup completed successfully!")
            
    except Error as e:
        print(f"Error setting up database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    setup_database()