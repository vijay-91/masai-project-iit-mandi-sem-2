from uuid import uuid4
import csv
from datetime import datetime, timedelta

class Book:
    def __init__(self, book_id, title, author, quantity):
        self.book_id = book_id or uuid4().hex
        self.title = title
        self.author = author
        self.quantity = int(quantity)

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "quantity": self.quantity
        }

    def __str__(self):
        return f"Book -> ID: {self.book_id}; Title: {self.title}; Author: {self.author}; Quantity: {self.quantity}"

class Member:
    def __init__(self, member_id, name, contact):
        self.member_id = member_id or uuid4().hex
        self.name = name
        self.contact = contact

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "contact": self.contact
        }

    def __str__(self):
        return f"Member -> ID: {self.member_id}; Name: {self.name}; Contact: {self.contact}"

class BookAssignment:
    def __init__(self, assignment_id, member_id, book_id, issue_date, due_date, returned="No"):
        self.assignment_id = assignment_id or uuid4().hex
        self.member_id = member_id
        self.book_id = book_id
        self.issue_date = issue_date
        self.due_date = due_date
        self.returned = returned

    def to_dict(self):
        return {
            "assignment_id": self.assignment_id,
            "member_id": self.member_id,
            "book_id": self.book_id,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "returned": self.returned
        }

    def __str__(self):
        return (f"Assignment -> ID: {self.assignment_id}; Member ID: {self.member_id}; Book ID: {self.book_id}; "
                f"Issue Date: {self.issue_date}; Due Date: {self.due_date}; Returned: {self.returned}")

class LibraryManager:
    BOOKS_FILE = "books.csv"
    MEMBERS_FILE = "members.csv"
    ASSIGNMENTS_FILE = "assignments.csv"

    def __init__(self):
        self.books = self.load_data(self.BOOKS_FILE, Book)
        self.members = self.load_data(self.MEMBERS_FILE, Member)
        self.assignments = self.load_data(self.ASSIGNMENTS_FILE, BookAssignment)

    def load_data(self, filename, cls):
        data = []
        try:
            with open(filename, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(cls(**row))
        except FileNotFoundError:
            with open(filename, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=cls(None, None, None, None).to_dict().keys())
                writer.writeheader()
        return data

    def save_data(self, filename, data):
        with open(filename, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=data[0].to_dict().keys() if data else [])
            writer.writeheader()
            for item in data:
                writer.writerow(item.to_dict())

    def list_books(self):
        for book in self.books:
            print(book)

    def add_book(self, title, author, quantity):
        book = Book(None, title, author, quantity)
        self.books.append(book)
        self.save_data(self.BOOKS_FILE, self.books)

    def update_book(self, book_id, title=None, author=None, quantity=None):
        for book in self.books:
            if book.book_id == book_id:
                if title: book.title = title
                if author: book.author = author
                if quantity: book.quantity = int(quantity)
                self.save_data(self.BOOKS_FILE, self.books)
                print("Book updated successfully.")
                return
        print("Book not found.")

    def delete_book(self, book_id):
        self.books = [book for book in self.books if book.book_id != book_id]
        self.save_data(self.BOOKS_FILE, self.books)
        print("Book deleted successfully.")

    def list_members(self):
        for member in self.members:
            print(member)

    def add_member(self, name, contact):
        member = Member(None, name, contact)
        self.members.append(member)
        self.save_data(self.MEMBERS_FILE, self.members)

    def update_member(self, member_id, name=None, contact=None):
        for member in self.members:
            if member.member_id == member_id:
                if name: member.name = name
                if contact: member.contact = contact
                self.save_data(self.MEMBERS_FILE, self.members)
                print("Member updated successfully.")
                return
        print("Member not found.")

    def delete_member(self, member_id):
        self.members = [member for member in self.members if member.member_id != member_id]
        self.save_data(self.MEMBERS_FILE, self.members)
        print("Member deleted successfully.")

    def assign_book(self, member_id, book_id, due_date=None):
        for book in self.books:
            if book.book_id == book_id and book.quantity > 0:
                for member in self.members:
                    if member.member_id == member_id:
                        issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # If no due date provided, set it to 14 days from the issue date
                        if not due_date:
                            due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Create the assignment with the due date
                        assignment = BookAssignment(None, member_id, book_id, issue_date, due_date)
                        self.assignments.append(assignment)

                        book.quantity -= 1
                        self.save_data(self.BOOKS_FILE, self.books)
                        self.save_data(self.ASSIGNMENTS_FILE, self.assignments)
                        print(f"Book '{book.title}' assigned to {member.name}. Due date: {due_date}.")
                        return
                print("Member not found.")
                return
        print("Book not available.")


    def list_assigned_books(self):
        print("Assigned Books:")
        for assignment in self.assignments:
            if assignment.returned == "No":
                member_name = next((member.name for member in self.members if member.member_id == assignment.member_id), "Unknown Member")
                book_title = next((book.title for book in self.books if book.book_id == assignment.book_id), "Unknown Book")
                print(f"Member: {member_name}, Book: {book_title}, Issue Date: {assignment.issue_date}, Due Date: {assignment.due_date}")

    def list_assigned_books_to_members(self):
        print("Assigned Books to Members:")
        for assignment in self.assignments:
            if assignment.returned == "No":
                member_name = next((member.name for member in self.members if member.member_id == assignment.member_id), "Unknown Member")
                book_title = next((book.title for book in self.books if book.book_id == assignment.book_id), "Unknown Book")
                print(f"Member ID: {assignment.member_id}, Member Name: {member_name}, Book Name: {book_title}, Assigned Date and Time: {assignment.issue_date}, Due Date: {assignment.due_date}")

    def return_book(self, assignment_id):
        for assignment in self.assignments:
            if assignment.assignment_id == assignment_id and assignment.returned == "No":
                assignment.returned = "Yes"
                for book in self.books:
                    if book.book_id == assignment.book_id:
                        book.quantity += 1
                        break
                self.save_data(self.BOOKS_FILE, self.books)
                self.save_data(self.ASSIGNMENTS_FILE, self.assignments)
                print("Book returned successfully.")
                return
        print("Invalid assignment ID or book already returned.")

    def check_book_available(self, title):
        title_lower = title.lower()  # Convert the input title to lowercase for case-insensitive comparison
        matched_books = []

        for book in self.books:
            if title_lower in book.title.lower():  # Access title using dot notation
                matched_books.append(book)

        if matched_books:
            for book in matched_books:
                if book.quantity > 0:
                    print(f"Book '{book.title}' is available with Book ID: {book.book_id}. Quantity: {book.quantity}")
                else:
                    print(f"Book '{book.title}' is not available. Quantity: {book.quantity}")
        else:
            print("No book found with that title.")
    
if __name__ == "__main__":
    manager = LibraryManager()

    while True:
        print("Enter your choices")
        print("1. List all Books")
        print("2. Add a Book")
        print("3. Update a Book")
        print("4. Delete a Book")
        print("5. List all Members")
        print("6. Add a Member")
        print("7. Update a Member")
        print("8. Delete a Member")
        print("9. Enter Book Title name for verify book available")
        print("10. List assigned books to member")
        print("11. Assign a Book")
        print("12. Return a Book")
        print("13. Exit")

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        match choice:
            case 1:
                manager.list_books()
            case 2:
                title = input("Enter book title: ")
                author = input("Enter book author: ")
                quantity = int(input("Enter book quantity: "))
                manager.add_book(title, author, quantity)
            case 3:
                book_id = input("Enter book ID: ")
                title = input("Enter new title (leave blank to skip): ") or None
                author = input("Enter new author (leave blank to skip): ") or None
                quantity = input("Enter new quantity (leave blank to skip): ") or None
                manager.update_book(book_id, title, author, quantity)
            case 4:
                book_id = input("Enter book ID to delete: ")
                manager.delete_book(book_id)
            case 5:
                manager.list_members()
            case 6:
                name = input("Enter member name: ")
                contact = input("Enter member contact: ")
                manager.add_member(name, contact)
            case 7:
                member_id = input("Enter member ID: ")
                name = input("Enter new name (leave blank to skip): ") or None
                contact = input("Enter new contact (leave blank to skip): ") or None
                manager.update_member(member_id, name, contact)
            case 8:
                member_id = input("Enter member ID to delete: ")
                manager.delete_member(member_id)
            case 9:
                # Query to check book available or not?
                title = input("Enter book title: ")
                manager.check_book_available(title)
            case 10:
                manager.list_assigned_books_to_members()
            case 11:
                member_id = input("Enter member ID: ")
                book_id = input("Enter book ID: ")
                # Ask for the due date. If left blank, automatically set it.
                due_date_input = input("Enter due date (YYYY-MM-DD) or leave blank for automatic 14 days from now: ")
                
                # If the due date is provided, validate the format, otherwise leave it as None
                due_date = None
                if due_date_input:
                    try:
                        due_date = datetime.strptime(due_date_input, "%Y-%m-%d")
                    except ValueError:
                        print("Invalid date format. Due date will be automatically set to 14 days from today.")
                
                manager.assign_book(member_id, book_id, due_date)

            case 12:
                assignment_id = input("Enter assignment ID to mark as returned: ")
                manager.return_book(assignment_id)
            case 13:
                print("Exiting...")
                break
            case _:
                print("Invalid choice. Please try again.")