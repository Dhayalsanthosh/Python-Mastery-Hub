"""
Library System exercise for the OOP module.
Build a comprehensive library management system using classes and objects.
"""

from typing import Dict, Any


def get_library_exercise() -> Dict[str, Any]:
    """Get the Library System exercise."""
    return {
        "title": "Library Management System",
        "difficulty": "medium",
        "estimated_time": "1-2 hours",
        "instructions": """
Create a comprehensive library management system that demonstrates fundamental 
OOP concepts including classes, objects, methods, and basic inheritance.

Your system should handle books, authors, patrons, and library operations
like checking out books, returning books, and searching the catalog.
""",
        "learning_objectives": [
            "Practice class design and object creation",
            "Implement methods for object behavior",
            "Use composition to build complex systems",
            "Handle object relationships and associations",
            "Apply encapsulation principles"
        ],
        "tasks": [
            {
                "step": 1,
                "title": "Create Author Class",
                "description": "Design an Author class to represent book authors",
                "requirements": [
                    "Store author name, birth year, and nationality",
                    "Implement __str__ method for readable output",
                    "Add method to calculate author's age",
                    "Include validation for birth year"
                ]
            },
            {
                "step": 2,
                "title": "Create Book Class", 
                "description": "Design a Book class with author association",
                "requirements": [
                    "Store title, author (Author object), ISBN, publication year",
                    "Track availability status (checked out or available)",
                    "Implement __str__ and __repr__ methods",
                    "Add methods to check out and return the book"
                ]
            },
            {
                "step": 3,
                "title": "Create Patron Class",
                "description": "Design a Patron class for library users", 
                "requirements": [
                    "Store patron name, ID, contact information",
                    "Track list of currently checked out books",
                    "Implement methods to check out and return books",
                    "Add borrowing limit enforcement"
                ]
            },
            {
                "step": 4,
                "title": "Create Library Class",
                "description": "Design the main Library class to manage everything",
                "requirements": [
                    "Maintain catalogs of books, authors, and patrons",
                    "Implement book search by title, author, or ISBN",
                    "Handle book checkout and return transactions",
                    "Generate reports on library inventory and usage"
                ]
            },
            {
                "step": 5,
                "title": "Add Advanced Features",
                "description": "Extend the system with additional functionality",
                "requirements": [
                    "Add book reservation system",
                    "Implement overdue book tracking",
                    "Create different patron types (Student, Faculty, Public)",
                    "Add fine calculation for overdue books"
                ]
            }
        ],
        "starter_code": '''
from datetime import datetime, timedelta
from typing import List, Optional

class Author:
    """Represents a book author."""
    
    def __init__(self, name: str, birth_year: int, nationality: str = "Unknown"):
        # TODO: Implement initialization with validation
        pass
    
    def get_age(self) -> int:
        """Calculate and return author's current age."""
        # TODO: Implement age calculation
        pass
    
    def __str__(self) -> str:
        # TODO: Return readable string representation
        pass

class Book:
    """Represents a book in the library."""
    
    def __init__(self, title: str, author: Author, isbn: str, publication_year: int):
        # TODO: Implement initialization
        pass
    
    def check_out(self) -> bool:
        """Mark book as checked out."""
        # TODO: Implement checkout logic
        pass
    
    def return_book(self) -> bool:
        """Mark book as returned/available."""
        # TODO: Implement return logic
        pass
    
    def __str__(self) -> str:
        # TODO: Return readable string representation
        pass

class Patron:
    """Represents a library patron."""
    
    def __init__(self, name: str, patron_id: str, email: str):
        # TODO: Implement initialization
        pass
    
    def can_check_out(self) -> bool:
        """Check if patron can check out more books."""
        # TODO: Implement borrowing limit check
        pass
    
    def check_out_book(self, book: Book) -> bool:
        """Check out a book to this patron."""
        # TODO: Implement checkout logic
        pass
    
    def return_book(self, book: Book) -> bool:
        """Return a book from this patron."""
        # TODO: Implement return logic
        pass

class Library:
    """Main library management system."""
    
    def __init__(self, name: str):
        # TODO: Implement initialization
        pass
    
    def add_book(self, book: Book) -> str:
        """Add a book to the library catalog."""
        # TODO: Implement book addition
        pass
    
    def add_patron(self, patron: Patron) -> str:
        """Register a new patron."""
        # TODO: Implement patron registration
        pass
    
    def search_books(self, query: str) -> List[Book]:
        """Search for books by title, author, or ISBN."""
        # TODO: Implement search functionality
        pass
    
    def check_out_book(self, isbn: str, patron_id: str) -> str:
        """Handle book checkout transaction."""
        # TODO: Implement checkout transaction
        pass
    
    def return_book(self, isbn: str, patron_id: str) -> str:
        """Handle book return transaction."""
        # TODO: Implement return transaction
        pass

# Test your implementation
if __name__ == "__main__":
    # Create library
    library = Library("City Public Library")
    
    # Create authors
    orwell = Author("George Orwell", 1903, "British")
    tolkien = Author("J.R.R. Tolkien", 1892, "British")
    
    # Create books
    book1 = Book("1984", orwell, "978-0-452-28423-4", 1949)
    book2 = Book("The Hobbit", tolkien, "978-0-547-92822-7", 1937)
    
    # Add books to library
    print(library.add_book(book1))
    print(library.add_book(book2))
    
    # Create and register patron
    alice = Patron("Alice Johnson", "P001", "alice@email.com")
    print(library.add_patron(alice))
    
    # Test checkout/return
    print(library.check_out_book("978-0-452-28423-4", "P001"))
    print(library.return_book("978-0-452-28423-4", "P001"))
''',
        "hints": [
            "Use composition - Book contains Author, Library contains Books and Patrons",
            "Consider using dictionaries for fast lookups (ISBN -> Book, ID -> Patron)",
            "Implement proper validation in constructors",
            "Use datetime for tracking checkout dates and due dates",
            "Think about edge cases - what if book is already checked out?",
            "Consider using enums for status values (AVAILABLE, CHECKED_OUT)",
            "Make sure to update both Book and Patron when checking out/returning"
        ],
        "solution": '''
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum

class BookStatus(Enum):
    """Enumeration for book status."""
    AVAILABLE = "available"
    CHECKED_OUT = "checked_out"
    RESERVED = "reserved"

class PatronType(Enum):
    """Enumeration for patron types."""
    STUDENT = "student"
    FACULTY = "faculty"
    PUBLIC = "public"

class Author:
    """Represents a book author."""
    
    def __init__(self, name: str, birth_year: int, nationality: str = "Unknown"):
        if not name or not name.strip():
            raise ValueError("Author name cannot be empty")
        if birth_year < 0 or birth_year > datetime.now().year:
            raise ValueError("Invalid birth year")
        
        self.name = name.strip()
        self.birth_year = birth_year
        self.nationality = nationality
    
    def get_age(self) -> int:
        """Calculate and return author's current age."""
        current_year = datetime.now().year
        return current_year - self.birth_year
    
    def __str__(self) -> str:
        return f"{self.name} ({self.birth_year}, {self.nationality})"
    
    def __repr__(self) -> str:
        return f"Author('{self.name}', {self.birth_year}, '{self.nationality}')"

class Book:
    """Represents a book in the library."""
    
    def __init__(self, title: str, author: Author, isbn: str, publication_year: int):
        if not title or not title.strip():
            raise ValueError("Book title cannot be empty")
        if not isinstance(author, Author):
            raise ValueError("Author must be an Author object")
        if not isbn or len(isbn.replace("-", "").replace(" ", "")) < 10:
            raise ValueError("Invalid ISBN")
        if publication_year < 0 or publication_year > datetime.now().year:
            raise ValueError("Invalid publication year")
        
        self.title = title.strip()
        self.author = author
        self.isbn = isbn
        self.publication_year = publication_year
        self.status = BookStatus.AVAILABLE
        self.checked_out_to = None
        self.due_date = None
        self.checkout_date = None
    
    def check_out(self, patron_id: str, due_date: datetime = None) -> bool:
        """Mark book as checked out."""
        if self.status != BookStatus.AVAILABLE:
            return False
        
        self.status = BookStatus.CHECKED_OUT
        self.checked_out_to = patron_id
        self.checkout_date = datetime.now()
        self.due_date = due_date or (datetime.now() + timedelta(days=14))
        return True
    
    def return_book(self) -> bool:
        """Mark book as returned/available."""
        if self.status != BookStatus.CHECKED_OUT:
            return False
        
        self.status = BookStatus.AVAILABLE
        self.checked_out_to = None
        self.due_date = None
        self.checkout_date = None
        return True
    
    def is_overdue(self) -> bool:
        """Check if book is overdue."""
        if self.status != BookStatus.CHECKED_OUT or not self.due_date:
            return False
        return datetime.now() > self.due_date
    
    def days_overdue(self) -> int:
        """Calculate days overdue (0 if not overdue)."""
        if not self.is_overdue():
            return 0
        return (datetime.now() - self.due_date).days
    
    def __str__(self) -> str:
        status_info = f" ({self.status.value})"
        if self.status == BookStatus.CHECKED_OUT:
            status_info += f" - Due: {self.due_date.strftime('%Y-%m-%d')}"
        return f"'{self.title}' by {self.author.name} [{self.isbn}]{status_info}"
    
    def __repr__(self) -> str:
        return f"Book('{self.title}', {self.author!r}, '{self.isbn}', {self.publication_year})"

class Patron:
    """Represents a library patron."""
    
    def __init__(self, name: str, patron_id: str, email: str, patron_type: PatronType = PatronType.PUBLIC):
        if not name or not name.strip():
            raise ValueError("Patron name cannot be empty")
        if not patron_id or not patron_id.strip():
            raise ValueError("Patron ID cannot be empty")
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        
        self.name = name.strip()
        self.patron_id = patron_id.strip()
        self.email = email.strip().lower()
        self.patron_type = patron_type
        self.checked_out_books: List[str] = []  # List of ISBNs
        self.registration_date = datetime.now()
        self.total_fines = 0.0
        
        # Set borrowing limits based on patron type
        self.borrowing_limits = {
            PatronType.STUDENT: 5,
            PatronType.FACULTY: 10,
            PatronType.PUBLIC: 3
        }
    
    def can_check_out(self) -> bool:
        """Check if patron can check out more books."""
        max_books = self.borrowing_limits[self.patron_type]
        return len(self.checked_out_books) < max_books and self.total_fines < 10.0
    
    def check_out_book(self, isbn: str) -> bool:
        """Check out a book to this patron."""
        if not self.can_check_out():
            return False
        
        if isbn not in self.checked_out_books:
            self.checked_out_books.append(isbn)
            return True
        return False
    
    def return_book(self, isbn: str) -> bool:
        """Return a book from this patron."""
        if isbn in self.checked_out_books:
            self.checked_out_books.remove(isbn)
            return True
        return False
    
    def add_fine(self, amount: float) -> None:
        """Add fine to patron's account."""
        self.total_fines += amount
    
    def pay_fine(self, amount: float) -> float:
        """Pay fine and return remaining balance."""
        self.total_fines = max(0, self.total_fines - amount)
        return self.total_fines
    
    def __str__(self) -> str:
        return f"Patron: {self.name} (ID: {self.patron_id}, Type: {self.patron_type.value})"

class Library:
    """Main library management system."""
    
    def __init__(self, name: str):
        self.name = name
        self.books: Dict[str, Book] = {}  # ISBN -> Book
        self.patrons: Dict[str, Patron] = {}  # Patron ID -> Patron
        self.authors: Dict[str, Author] = {}  # Author name -> Author
        self.transaction_log: List[Dict] = []
    
    def add_book(self, book: Book) -> str:
        """Add a book to the library catalog."""
        if book.isbn in self.books:
            return f"Book with ISBN {book.isbn} already exists"
        
        self.books[book.isbn] = book
        
        # Add author to authors catalog
        if book.author.name not in self.authors:
            self.authors[book.author.name] = book.author
        
        self._log_transaction("ADD_BOOK", book.isbn, details=f"Added '{book.title}'")
        return f"Successfully added '{book.title}' to library catalog"
    
    def add_patron(self, patron: Patron) -> str:
        """Register a new patron."""
        if patron.patron_id in self.patrons:
            return f"Patron with ID {patron.patron_id} already exists"
        
        self.patrons[patron.patron_id] = patron
        self._log_transaction("ADD_PATRON", patron.patron_id, details=f"Registered {patron.name}")
        return f"Successfully registered patron: {patron.name}"
    
    def search_books(self, query: str) -> List[Book]:
        """Search for books by title, author, or ISBN."""
        query = query.lower().strip()
        results = []
        
        for book in self.books.values():
            if (query in book.title.lower() or 
                query in book.author.name.lower() or 
                query in book.isbn.lower()):
                results.append(book)
        
        return results
    
    def check_out_book(self, isbn: str, patron_id: str) -> str:
        """Handle book checkout transaction."""
        # Validate book exists
        if isbn not in self.books:
            return f"Book with ISBN {isbn} not found"
        
        # Validate patron exists
        if patron_id not in self.patrons:
            return f"Patron with ID {patron_id} not found"
        
        book = self.books[isbn]
        patron = self.patrons[patron_id]
        
        # Check if book is available
        if book.status != BookStatus.AVAILABLE:
            return f"Book '{book.title}' is not available for checkout"
        
        # Check if patron can check out more books
        if not patron.can_check_out():
            return f"Patron {patron.name} cannot check out more books (limit reached or has fines)"
        
        # Perform checkout
        due_date = datetime.now() + timedelta(days=14)  # 2 week loan
        if book.check_out(patron_id, due_date) and patron.check_out_book(isbn):
            self._log_transaction("CHECKOUT", isbn, patron_id, 
                                f"'{book.title}' checked out to {patron.name}")
            return f"Successfully checked out '{book.title}' to {patron.name}. Due: {due_date.strftime('%Y-%m-%d')}"
        
        return "Checkout failed"
    
    def return_book(self, isbn: str, patron_id: str) -> str:
        """Handle book return transaction."""
        # Validate book exists
        if isbn not in self.books:
            return f"Book with ISBN {isbn} not found"
        
        # Validate patron exists
        if patron_id not in self.patrons:
            return f"Patron with ID {patron_id} not found"
        
        book = self.books[isbn]
        patron = self.patrons[patron_id]
        
        # Check if book is checked out to this patron
        if book.checked_out_to != patron_id:
            return f"Book '{book.title}' is not checked out to {patron.name}"
        
        # Calculate fines for overdue books
        fine_message = ""
        if book.is_overdue():
            days_overdue = book.days_overdue()
            fine_amount = days_overdue * 0.50  # $0.50 per day
            patron.add_fine(fine_amount)
            fine_message = f" (Fine: ${fine_amount:.2f} for {days_overdue} days overdue)"
        
        # Perform return
        if book.return_book() and patron.return_book(isbn):
            self._log_transaction("RETURN", isbn, patron_id, 
                                f"'{book.title}' returned by {patron.name}")
            return f"Successfully returned '{book.title}'{fine_message}"
        
        return "Return failed"
    
    def get_overdue_books(self) -> List[Book]:
        """Get list of all overdue books."""
        return [book for book in self.books.values() if book.is_overdue()]
    
    def get_patron_books(self, patron_id: str) -> List[Book]:
        """Get list of books checked out by a patron."""
        if patron_id not in self.patrons:
            return []
        
        patron = self.patrons[patron_id]
        return [self.books[isbn] for isbn in patron.checked_out_books if isbn in self.books]
    
    def generate_inventory_report(self) -> str:
        """Generate library inventory report."""
        total_books = len(self.books)
        available_books = len([b for b in self.books.values() if b.status == BookStatus.AVAILABLE])
        checked_out_books = len([b for b in self.books.values() if b.status == BookStatus.CHECKED_OUT])
        overdue_books = len(self.get_overdue_books())
        
        report = f"""
=== {self.name} Inventory Report ===
Total Books: {total_books}
Available: {available_books}
Checked Out: {checked_out_books}
Overdue: {overdue_books}
Total Patrons: {len(self.patrons)}
Total Authors: {len(self.authors)}

Recent Transactions: {len(self.transaction_log)}
"""
        return report
    
    def _log_transaction(self, action: str, isbn: str, patron_id: str = None, details: str = ""):
        """Log a transaction for audit purposes."""
        transaction = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'isbn': isbn,
            'patron_id': patron_id,
            'details': details
        }
        self.transaction_log.append(transaction)
    
    def __str__(self) -> str:
        return f"Library: {self.name} ({len(self.books)} books, {len(self.patrons)} patrons)"

# Comprehensive test and demonstration
def demonstrate_library_system():
    """Demonstrate the complete library system functionality."""
    print("=== Library Management System Demo ===\\n")
    
    # Create library
    library = Library("City Public Library")
    print(f"Created: {library}")
    
    # Create authors
    orwell = Author("George Orwell", 1903, "British")
    tolkien = Author("J.R.R. Tolkien", 1892, "British")
    rowling = Author("J.K. Rowling", 1965, "British")
    
    print(f"\\nAuthors created:")
    print(f"  {orwell} (Age: {orwell.get_age()})")
    print(f"  {tolkien} (Age: {tolkien.get_age()})")
    print(f"  {rowling} (Age: {rowling.get_age()})")
    
    # Create books
    books = [
        Book("1984", orwell, "978-0-452-28423-4", 1949),
        Book("Animal Farm", orwell, "978-0-452-28424-1", 1945),
        Book("The Hobbit", tolkien, "978-0-547-92822-7", 1937),
        Book("The Lord of the Rings", tolkien, "978-0-544-00341-5", 1954),
        Book("Harry Potter and the Philosopher's Stone", rowling, "978-0-7475-3269-9", 1997)
    ]
    
    print(f"\\nAdding books to library:")
    for book in books:
        print(f"  {library.add_book(book)}")
    
    # Create patrons with different types
    patrons = [
        Patron("Alice Johnson", "P001", "alice@email.com", PatronType.STUDENT),
        Patron("Bob Smith", "P002", "bob@email.com", PatronType.FACULTY),
        Patron("Carol Brown", "P003", "carol@email.com", PatronType.PUBLIC)
    ]
    
    print(f"\\nRegistering patrons:")
    for patron in patrons:
        print(f"  {library.add_patron(patron)}")
    
    # Test book search
    print(f"\\nSearching for books:")
    search_results = library.search_books("orwell")
    print(f"  Search 'orwell': {len(search_results)} results")
    for book in search_results:
        print(f"    - {book}")
    
    # Test checkout/return workflow
    print(f"\\nTesting checkout/return:")
    print(f"  {library.check_out_book('978-0-452-28423-4', 'P001')}")
    print(f"  {library.check_out_book('978-0-547-92822-7', 'P001')}")
    
    # Show patron's checked out books
    alice_books = library.get_patron_books('P001')
    print(f"  Alice's books: {[book.title for book in alice_books]}")
    
    # Test return
    print(f"  {library.return_book('978-0-452-28423-4', 'P001')}")
    
    # Generate and display report
    print(library.generate_inventory_report())
    
    print("=== Demo Complete ===")

if __name__ == "__main__":
    demonstrate_library_system()
'''
    }