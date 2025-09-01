"""
Advanced unittest exercise for the Testing module.
Build a comprehensive test suite for a book library system.
"""

from typing import Dict, Any


def get_unittest_exercise() -> Dict[str, Any]:
    """Get the advanced unittest exercise."""
    return {
        "title": "Advanced Unit Testing - Library Management System",
        "difficulty": "medium",
        "estimated_time": "2-3 hours",
        "instructions": """
Build a comprehensive test suite for a book library management system using unittest.
This exercise will help you master advanced unittest features including fixtures,
custom assertions, test organization, and error handling.

You'll create tests for a multi-class system with complex interactions, demonstrating
real-world testing scenarios and best practices.
""",
        "learning_objectives": [
            "Master unittest fixtures and test organization",
            "Practice comprehensive test coverage strategies",
            "Learn to test complex object interactions",
            "Implement custom assertion methods",
            "Handle edge cases and error conditions effectively"
        ],
        "tasks": [
            {
                "step": 1,
                "title": "Create Book and Author Classes",
                "description": "Implement basic Book and Author model classes",
                "requirements": [
                    "Author class with name, birth_year, nationality",
                    "Book class with title, author, isbn, publication_year, copies",
                    "Proper validation for all inputs",
                    "String representations for debugging"
                ]
            },
            {
                "step": 2,
                "title": "Build Library Management System",
                "description": "Implement Library class with book management",
                "requirements": [
                    "Add books to library collection",
                    "Check out and return books",
                    "Search books by title, author, or ISBN",
                    "Track available copies"
                ]
            },
            {
                "step": 3,
                "title": "Implement Member System", 
                "description": "Add library member functionality",
                "requirements": [
                    "Member registration and management",
                    "Checkout history tracking",
                    "Fine calculation for overdue books",
                    "Member status (active/suspended)"
                ]
            },
            {
                "step": 4,
                "title": "Create Comprehensive Test Suite",
                "description": "Write thorough tests for all functionality",
                "requirements": [
                    "Test all positive and negative scenarios",
                    "Use setUp and tearDown appropriately",
                    "Implement parameterized tests with subTest",
                    "Test edge cases and boundary conditions"
                ]
            },
            {
                "step": 5,
                "title": "Add Advanced Testing Features",
                "description": "Implement advanced unittest features",
                "requirements": [
                    "Custom assertion methods",
                    "Test suite organization",
                    "Mock external dependencies if needed",
                    "Performance and stress testing"
                ]
            }
        ],
        "starter_code": '''
import unittest
from datetime import datetime, timedelta
from typing import List, Optional

class Author:
    """Author class for library system."""
    
    def __init__(self, name: str, birth_year: int, nationality: str = "Unknown"):
        # TODO: Implement with validation
        pass
    
    def __str__(self):
        # TODO: Implement string representation
        pass

class Book:
    """Book class for library system."""
    
    def __init__(self, title: str, author: Author, isbn: str, 
                 publication_year: int, total_copies: int = 1):
        # TODO: Implement with validation
        pass
    
    def __str__(self):
        # TODO: Implement string representation
        pass

class Member:
    """Library member class."""
    
    def __init__(self, member_id: str, name: str, email: str):
        # TODO: Implement with validation
        pass

class Library:
    """Main library management class."""
    
    def __init__(self, name: str):
        # TODO: Initialize library
        pass
    
    def add_book(self, book: Book) -> str:
        """Add a book to the library."""
        # TODO: Implement
        pass
    
    def register_member(self, member: Member) -> str:
        """Register a new member."""
        # TODO: Implement
        pass
    
    def checkout_book(self, member_id: str, isbn: str) -> str:
        """Check out a book to a member."""
        # TODO: Implement
        pass
    
    def return_book(self, member_id: str, isbn: str) -> str:
        """Return a book from a member."""
        # TODO: Implement
        pass

class TestLibrarySystem(unittest.TestCase):
    """Comprehensive test suite for library system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # TODO: Create test data
        pass
    
    def test_author_creation(self):
        """Test author creation with valid data."""
        # TODO: Implement test
        pass
    
    def test_book_creation(self):
        """Test book creation with valid data."""
        # TODO: Implement test
        pass
    
    def test_library_operations(self):
        """Test basic library operations."""
        # TODO: Implement test
        pass
    
    # TODO: Add more comprehensive tests

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
        "hints": [
            "Use setUp to create consistent test data across tests",
            "Validate input parameters in constructors",
            "Use subTest for testing multiple similar cases",
            "Test both successful operations and error conditions",
            "Consider using class-level setUp for expensive operations",
            "Create helper methods to reduce test code duplication",
            "Test edge cases like empty strings, negative numbers",
            "Use appropriate assertion methods for better error messages"
        ],
        "solution": '''
import unittest
from datetime import datetime, timedelta
from typing import List, Optional, Dict

class Author:
    """Author class for library system."""
    
    def __init__(self, name: str, birth_year: int, nationality: str = "Unknown"):
        if not name or not name.strip():
            raise ValueError("Author name cannot be empty")
        if birth_year < 0 or birth_year > datetime.now().year:
            raise ValueError("Invalid birth year")
        
        self.name = name.strip()
        self.birth_year = birth_year
        self.nationality = nationality.strip() if nationality else "Unknown"
    
    def __str__(self):
        return f"{self.name} ({self.birth_year}, {self.nationality})"
    
    def __eq__(self, other):
        if not isinstance(other, Author):
            return False
        return (self.name == other.name and 
                self.birth_year == other.birth_year and
                self.nationality == other.nationality)

class Book:
    """Book class for library system."""
    
    def __init__(self, title: str, author: Author, isbn: str, 
                 publication_year: int, total_copies: int = 1):
        if not title or not title.strip():
            raise ValueError("Book title cannot be empty")
        if not isinstance(author, Author):
            raise TypeError("Author must be an Author instance")
        if not isbn or not self._validate_isbn(isbn):
            raise ValueError("Invalid ISBN format")
        if publication_year < 0 or publication_year > datetime.now().year:
            raise ValueError("Invalid publication year")
        if total_copies < 1:
            raise ValueError("Total copies must be at least 1")
        
        self.title = title.strip()
        self.author = author
        self.isbn = isbn
        self.publication_year = publication_year
        self.total_copies = total_copies
        self.available_copies = total_copies
    
    def _validate_isbn(self, isbn: str) -> bool:
        """Validate ISBN format (simplified)."""
        isbn_clean = isbn.replace("-", "").replace(" ", "")
        return len(isbn_clean) in [10, 13] and isbn_clean.isdigit()
    
    def checkout(self) -> bool:
        """Check out a copy of this book."""
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False
    
    def return_copy(self) -> bool:
        """Return a copy of this book."""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False
    
    def is_available(self) -> bool:
        """Check if book is available for checkout."""
        return self.available_copies > 0
    
    def __str__(self):
        return f"'{self.title}' by {self.author.name} (ISBN: {self.isbn})"

class Member:
    """Library member class."""
    
    def __init__(self, member_id: str, name: str, email: str):
        if not member_id or not member_id.strip():
            raise ValueError("Member ID cannot be empty")
        if not name or not name.strip():
            raise ValueError("Member name cannot be empty")
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        
        self.member_id = member_id.strip()
        self.name = name.strip()
        self.email = email.strip()
        self.join_date = datetime.now()
        self.is_active = True
        self.checked_out_books = {}  # ISBN -> checkout_date
        self.checkout_history = []
    
    def __str__(self):
        return f"Member {self.member_id}: {self.name} ({self.email})"

class CheckoutRecord:
    """Record of a book checkout."""
    
    def __init__(self, member_id: str, isbn: str, checkout_date: datetime = None):
        self.member_id = member_id
        self.isbn = isbn
        self.checkout_date = checkout_date or datetime.now()
        self.due_date = self.checkout_date + timedelta(days=14)  # 2 week loan
        self.return_date = None
    
    def is_overdue(self) -> bool:
        """Check if book is overdue."""
        if self.return_date:
            return False  # Already returned
        return datetime.now() > self.due_date
    
    def days_overdue(self) -> int:
        """Get number of days overdue."""
        if not self.is_overdue():
            return 0
        return (datetime.now() - self.due_date).days
    
    def calculate_fine(self, daily_rate: float = 0.50) -> float:
        """Calculate fine for overdue book."""
        return max(0, self.days_overdue() * daily_rate)

class Library:
    """Main library management class."""
    
    def __init__(self, name: str):
        if not name or not name.strip():
            raise ValueError("Library name cannot be empty")
        
        self.name = name.strip()
        self.books = {}  # ISBN -> Book
        self.members = {}  # member_id -> Member
        self.checkout_records = []  # List of CheckoutRecord
        self.daily_fine_rate = 0.50
    
    def add_book(self, book: Book) -> str:
        """Add a book to the library."""
        if book.isbn in self.books:
            # Book already exists, add to copies
            existing_book = self.books[book.isbn]
            existing_book.total_copies += book.total_copies
            existing_book.available_copies += book.total_copies
            return f"Added {book.total_copies} more copies of '{book.title}'"
        else:
            self.books[book.isbn] = book
            return f"Added new book '{book.title}' to library"
    
    def register_member(self, member: Member) -> str:
        """Register a new member."""
        if member.member_id in self.members:
            raise ValueError(f"Member ID {member.member_id} already exists")
        
        self.members[member.member_id] = member
        return f"Registered member {member.name}"
    
    def checkout_book(self, member_id: str, isbn: str) -> str:
        """Check out a book to a member."""
        # Validate member
        if member_id not in self.members:
            raise ValueError(f"Member {member_id} not found")
        
        member = self.members[member_id]
        if not member.is_active:
            raise ValueError(f"Member {member_id} is not active")
        
        # Validate book
        if isbn not in self.books:
            raise ValueError(f"Book with ISBN {isbn} not found")
        
        book = self.books[isbn]
        if not book.is_available():
            raise ValueError(f"Book '{book.title}' is not available")
        
        # Check if member already has this book
        if isbn in member.checked_out_books:
            raise ValueError(f"Member already has '{book.title}' checked out")
        
        # Perform checkout
        if book.checkout():
            checkout_date = datetime.now()
            member.checked_out_books[isbn] = checkout_date
            
            record = CheckoutRecord(member_id, isbn, checkout_date)
            self.checkout_records.append(record)
            member.checkout_history.append(record)
            
            return f"Checked out '{book.title}' to {member.name}"
        else:
            raise RuntimeError("Failed to checkout book")
    
    def return_book(self, member_id: str, isbn: str) -> str:
        """Return a book from a member."""
        # Validate member
        if member_id not in self.members:
            raise ValueError(f"Member {member_id} not found")
        
        member = self.members[member_id]
        
        # Check if member has this book
        if isbn not in member.checked_out_books:
            raise ValueError(f"Member does not have book with ISBN {isbn}")
        
        # Validate book exists
        if isbn not in self.books:
            raise ValueError(f"Book with ISBN {isbn} not found")
        
        book = self.books[isbn]
        
        # Find checkout record
        checkout_record = None
        for record in self.checkout_records:
            if (record.member_id == member_id and 
                record.isbn == isbn and 
                record.return_date is None):
                checkout_record = record
                break
        
        if not checkout_record:
            raise RuntimeError("Checkout record not found")
        
        # Perform return
        if book.return_copy():
            checkout_record.return_date = datetime.now()
            del member.checked_out_books[isbn]
            
            # Calculate fine if overdue
            fine = checkout_record.calculate_fine(self.daily_fine_rate)
            fine_msg = f" (Fine: ${fine:.2f})" if fine > 0 else ""
            
            return f"Returned '{book.title}' from {member.name}{fine_msg}"
        else:
            raise RuntimeError("Failed to return book")
    
    def search_books_by_title(self, title: str) -> List[Book]:
        """Search books by title (case-insensitive partial match)."""
        title_lower = title.lower()
        return [book for book in self.books.values() 
                if title_lower in book.title.lower()]
    
    def search_books_by_author(self, author_name: str) -> List[Book]:
        """Search books by author name (case-insensitive partial match)."""
        author_lower = author_name.lower()
        return [book for book in self.books.values() 
                if author_lower in book.author.name.lower()]
    
    def get_overdue_books(self) -> List[CheckoutRecord]:
        """Get all overdue checkout records."""
        return [record for record in self.checkout_records 
                if record.return_date is None and record.is_overdue()]
    
    def get_member_fines(self, member_id: str) -> float:
        """Calculate total fines for a member."""
        total_fines = 0
        for record in self.checkout_records:
            if (record.member_id == member_id and 
                record.return_date is None and 
                record.is_overdue()):
                total_fines += record.calculate_fine(self.daily_fine_rate)
        return total_fines

class TestLibrarySystem(unittest.TestCase):
    """Comprehensive test suite for library system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test authors
        self.author1 = Author("George Orwell", 1903, "British")
        self.author2 = Author("Jane Austen", 1775, "British")
        self.author3 = Author("Mark Twain", 1835, "American")
        
        # Create test books
        self.book1 = Book("1984", self.author1, "978-0-452-28423-4", 1949, 3)
        self.book2 = Book("Animal Farm", self.author1, "978-0-452-28424-1", 1945, 2)
        self.book3 = Book("Pride and Prejudice", self.author2, "978-0-14-143951-8", 1813, 1)
        
        # Create test members
        self.member1 = Member("M001", "Alice Johnson", "alice@email.com")
        self.member2 = Member("M002", "Bob Smith", "bob@email.com")
        
        # Create test library
        self.library = Library("Test Library")
        
        # Add books and members to library
        self.library.add_book(self.book1)
        self.library.add_book(self.book2)
        self.library.add_book(self.book3)
        self.library.register_member(self.member1)
        self.library.register_member(self.member2)
    
    def test_author_creation_valid(self):
        """Test author creation with valid data."""
        author = Author("Test Author", 1950, "Canadian")
        self.assertEqual(author.name, "Test Author")
        self.assertEqual(author.birth_year, 1950)
        self.assertEqual(author.nationality, "Canadian")
    
    def test_author_creation_validation(self):
        """Test author creation validation."""
        # Empty name
        with self.assertRaises(ValueError):
            Author("", 1950)
        
        # Invalid birth year
        with self.assertRaises(ValueError):
            Author("Test", -100)
        
        with self.assertRaises(ValueError):
            Author("Test", 2050)  # Future year
    
    def test_book_creation_valid(self):
        """Test book creation with valid data."""
        book = Book("Test Book", self.author1, "978-1-234-56789-0", 2020, 5)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, self.author1)
        self.assertEqual(book.isbn, "978-1-234-56789-0")
        self.assertEqual(book.publication_year, 2020)
        self.assertEqual(book.total_copies, 5)
        self.assertEqual(book.available_copies, 5)
    
    def test_book_creation_validation(self):
        """Test book creation validation."""
        # Empty title
        with self.assertRaises(ValueError):
            Book("", self.author1, "978-1-234-56789-0", 2020)
        
        # Invalid author type
        with self.assertRaises(TypeError):
            Book("Test", "Not an author", "978-1-234-56789-0", 2020)
        
        # Invalid ISBN
        with self.assertRaises(ValueError):
            Book("Test", self.author1, "invalid-isbn", 2020)
        
        # Invalid copies
        with self.assertRaises(ValueError):
            Book("Test", self.author1, "978-1-234-56789-0", 2020, 0)
    
    def test_member_creation_valid(self):
        """Test member creation with valid data."""
        member = Member("M999", "Test Member", "test@email.com")
        self.assertEqual(member.member_id, "M999")
        self.assertEqual(member.name, "Test Member")
        self.assertEqual(member.email, "test@email.com")
        self.assertTrue(member.is_active)
    
    def test_member_creation_validation(self):
        """Test member creation validation."""
        # Empty member ID
        with self.assertRaises(ValueError):
            Member("", "Test", "test@email.com")
        
        # Invalid email
        with self.assertRaises(ValueError):
            Member("M999", "Test", "invalid-email")
    
    def test_library_add_book(self):
        """Test adding books to library."""
        new_book = Book("New Book", self.author3, "978-1-111-11111-1", 2023)
        result = self.library.add_book(new_book)
        
        self.assertIn("Added new book", result)
        self.assertIn(new_book.isbn, self.library.books)
    
    def test_library_add_duplicate_book(self):
        """Test adding duplicate book increases copies."""
        duplicate_book = Book("1984", self.author1, "978-0-452-28423-4", 1949, 2)
        original_copies = self.library.books["978-0-452-28423-4"].total_copies
        
        result = self.library.add_book(duplicate_book)
        
        self.assertIn("more copies", result)
        new_total = self.library.books["978-0-452-28423-4"].total_copies
        self.assertEqual(new_total, original_copies + 2)
    
    def test_checkout_book_success(self):
        """Test successful book checkout."""
        isbn = "978-0-452-28423-4"
        original_available = self.library.books[isbn].available_copies
        
        result = self.library.checkout_book("M001", isbn)
        
        self.assertIn("Checked out", result)
        self.assertIn("Alice Johnson", result)
        
        # Check book availability decreased
        new_available = self.library.books[isbn].available_copies
        self.assertEqual(new_available, original_available - 1)
        
        # Check member has book
        self.assertIn(isbn, self.member1.checked_out_books)
    
    def test_checkout_book_validation(self):
        """Test checkout validation."""
        # Invalid member
        with self.assertRaises(ValueError):
            self.library.checkout_book("INVALID", "978-0-452-28423-4")
        
        # Invalid book
        with self.assertRaises(ValueError):
            self.library.checkout_book("M001", "invalid-isbn")
        
        # Check out all copies then try again
        isbn = "978-0-14-143951-8"  # Only 1 copy
        self.library.checkout_book("M001", isbn)
        
        with self.assertRaises(ValueError):
            self.library.checkout_book("M002", isbn)
    
    def test_return_book_success(self):
        """Test successful book return."""
        isbn = "978-0-452-28423-4"
        
        # First checkout
        self.library.checkout_book("M001", isbn)
        original_available = self.library.books[isbn].available_copies
        
        # Then return
        result = self.library.return_book("M001", isbn)
        
        self.assertIn("Returned", result)
        
        # Check book availability increased
        new_available = self.library.books[isbn].available_copies
        self.assertEqual(new_available, original_available + 1)
        
        # Check member no longer has book
        self.assertNotIn(isbn, self.member1.checked_out_books)
    
    def test_search_functionality(self):
        """Test book search functionality."""
        # Search by title
        results = self.library.search_books_by_title("1984")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "1984")
        
        # Partial title search
        results = self.library.search_books_by_title("Animal")
        self.assertEqual(len(results), 1)
        
        # Search by author
        results = self.library.search_books_by_author("Orwell")
        self.assertEqual(len(results), 2)  # 1984 and Animal Farm
    
    def test_overdue_books_and_fines(self):
        """Test overdue book detection and fine calculation."""
        isbn = "978-0-452-28423-4"
        
        # Checkout book
        self.library.checkout_book("M001", isbn)
        
        # Manually set checkout date to make it overdue
        checkout_record = self.library.checkout_records[-1]
        checkout_record.checkout_date = datetime.now() - timedelta(days=20)
        checkout_record.due_date = checkout_record.checkout_date + timedelta(days=14)
        
        # Check overdue detection
        overdue_books = self.library.get_overdue_books()
        self.assertEqual(len(overdue_books), 1)
        self.assertTrue(overdue_books[0].is_overdue())
        
        # Check fine calculation
        fines = self.library.get_member_fines("M001")
        expected_fine = 6 * 0.50  # 6 days overdue * $0.50
        self.assertEqual(fines, expected_fine)
    
    def test_parameterized_isbn_validation(self):
        """Test ISBN validation with multiple formats using subTest."""
        valid_isbns = [
            "978-0-452-28423-4",
            "9780452284234",
            "0-452-28423-1",
            "0452284231"
        ]
        
        invalid_isbns = [
            "123",
            "abc-def-ghi",
            "978-0-452-28423-45",  # Too long
            ""
        ]
        
        # Test valid ISBNs
        for isbn in valid_isbns:
            with self.subTest(isbn=isbn):
                try:
                    book = Book("Test", self.author1, isbn, 2020)
                    self.assertEqual(book.isbn, isbn)
                except ValueError:
                    self.fail(f"Valid ISBN {isbn} was rejected")
        
        # Test invalid ISBNs
        for isbn in invalid_isbns:
            with self.subTest(isbn=isbn):
                with self.assertRaises(ValueError):
                    Book("Test", self.author1, isbn, 2020)
    
    def test_complex_library_workflow(self):
        """Test complex workflow with multiple operations."""
        # Multiple checkouts
        self.library.checkout_book("M001", "978-0-452-28423-4")
        self.library.checkout_book("M001", "978-0-452-28424-1")
        self.library.checkout_book("M002", "978-0-14-143951-8")
        
        # Verify state
        self.assertEqual(len(self.member1.checked_out_books), 2)
        self.assertEqual(len(self.member2.checked_out_books), 1)
        
        # Return one book
        self.library.return_book("M001", "978-0-452-28423-4")
        self.assertEqual(len(self.member1.checked_out_books), 1)
        
        # Another member can now checkout the returned book
        result = self.library.checkout_book("M002", "978-0-452-28423-4")
        self.assertIn("Checked out", result)

# Custom test runner with additional features
class LibraryTestRunner:
    """Custom test runner for library system tests."""
    
    @staticmethod
    def run_all_tests():
        """Run all tests with detailed reporting."""
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestLibrarySystem)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print(f"\n{'='*50}")
        print(f"Library System Test Results:")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {(result.testsRun - len(result.failures) - len(result.errors))/result.testsRun*100:.1f}%")
        print(f"{'='*50}")
        
        return result

if __name__ == '__main__':
    # Run with custom runner
    LibraryTestRunner.run_all_tests()
'''
    }