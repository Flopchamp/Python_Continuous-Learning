#Build a class system for a school:

#A Person class with name and age, and a method introduce() that prints "Hi I am Alice and I am 20 years old"
#A Student class that inherits from Person, adds grade, and overrides introduce() to also print "I am a student with grade 85"
#A Teacher class that inherits from Person, adds subject, and overrides introduce() to also print "I teach Math" 


class Person:

    def __init__(self, name, age):
        # save name and age to self
        self.name = name
        self.age = age

    def introduce(self):
            print(f"Hi I am {self.name} and I am {self.age} years old")
class Student(Person):
    def __init__(self, name, age, grade):
        super().__init__(name, age)
        self.grade = grade

    def introduce(self):
        super().introduce()
        print(f"I am a student with grade {self.grade}")

class Teacher(Person):
    def __init__(self, name, age, subject):
        self.subject = subject
        super().__init__(name, age)

    def introduce(self):
        super().introduce()
        print(f"I teach {self.subject}")

    