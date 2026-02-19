#Build a simple Library system:

#A Book class with title, author, is_available (default True)
#A Library class with a books list and these methods:

#add_book(book) — adds a book to the library
#borrow_book(title) — marks book as unavailable, prints confirmation
#return_book(title) — marks book as available again
#show_books() — prints all books and whether they are available
#Add two methods to your Library class:

#save_to_file(filename) — saves all books to a text file, one per line, as title,author,is_available
#load_from_file(filename) — reads the file and adds books back to the library
#Replace the text file system in your Library with JSON. JSON is cleaner and handles special characters in titles much better:
#Upgrade save_to_file and load_from_file to use JSON instead of plain text
import json
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
        self.is_available = True
class Library:
    def __init__(self):
        self.books = []
    def add_book(self, book):
        self.books.append(book)
    def borrow_book(self, title):
        for book in self.books:
            if book.title == title and book.is_available:
                book.is_available = False
                print(f"You have borrowed '{book.title}' by {book.author}.")
                return
        print(f"Sorry, '{title}' is not available.")
    def return_book(self, title):
        for book in self.books:
            if book.title == title and not book.is_available:
                book.is_available = True
                print(f"You have returned '{book.title}' by {book.author}.")
                return
        print(f"Sorry, '{title}' was not borrowed.")
    def show_books(self):
        for book in self.books:
            status = "Available" if book.is_available else "Not Available"
            print(f"'{book.title}' by {book.author} - {status}")
    def save_json(self, filename):
        with open(filename, "w") as file:
            json.dump([{"title": book.title, "author": book.author, "is_available": book.is_available} for book in self.books], file)
    def load_json(self, filename):
        with open(filename, "r") as file:
            data = json.load(file)
            for item in data:
                book = Book(item["title"], item["author"])
                book.is_available = item["is_available"]
                self.books.append(book)