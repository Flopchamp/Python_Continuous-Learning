class Student:

    def __init__(self, name, grade):
        # save name and grade to self
        self.name = name
        self.grade = grade

    def show_info(self):
        # print name and grade
        print(f"Name: {self.name}, Grade: {self.grade}")

    def is_passing(self):
        # return True if grade >= 50, False if not
        return self.grade >= 50