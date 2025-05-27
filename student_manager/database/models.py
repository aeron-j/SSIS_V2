class Student:
    def __init__(self, idno, first_name, last_name, age, gender, year_level, college, course):
        self.idno = idno
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.year_level = year_level
        self.college = college
        self.course = course

    def to_tuple(self):
        return (
            self.idno,
            self.first_name,
            self.last_name,
            self.age,
            self.gender,
            self.year_level,
            self.college,
            self.course
        )

    @classmethod
    def from_tuple(cls, student_tuple):
        return cls(*student_tuple)

class College:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def to_tuple(self):
        return (self.code, self.name)

    @classmethod
    def from_tuple(cls, college_tuple):
        return cls(*college_tuple)

class Course:
    def __init__(self, code, name, college_code):
        self.code = code
        self.name = name
        self.college_code = college_code

    def to_tuple(self):
        return (self.code, self.name, self.college_code)

    @classmethod
    def from_tuple(cls, course_tuple):
        return cls(*course_tuple)