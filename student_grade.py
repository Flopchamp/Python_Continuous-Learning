def get_student_grade(students, name):
    try:
        # get the grade from the dictionary
            grade = students[name]

    except KeyError:
        # handle missing student
        return "Student not found"

    except TypeError:
        # handle wrong type
        return "Invalid input type"

    else:
        # return grade if no error
        return grade