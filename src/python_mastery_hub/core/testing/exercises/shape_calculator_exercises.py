"""
Shape Calculator Exercise for Test-Driven Development.

This exercise demonstrates TDD principles by building a shape calculator
from scratch using the Red-Green-Refactor cycle. Students will write
failing tests first, then implement minimal code to pass.
"""

import unittest
import math
from abc import ABC, abstractmethod
from typing import Union


# Base classes for the exercise - START WITH THESE
class Shape(ABC):
    """Abstract base class for all shapes."""
    
    @abstractmethod
    def area(self) -> float:
        """Calculate the area of the shape."""
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        """Calculate the perimeter of the shape."""
        pass
    
    def __str__(self) -> str:
        """String representation of the shape."""
        return f"{self.__class__.__name__}(area={self.area():.2f}, perimeter={self.perimeter():.2f})"


# Exercise Classes - IMPLEMENT THESE USING TDD
class Circle(Shape):
    """Circle shape implementation."""
    
    def __init__(self, radius: float):
        """Initialize circle with radius."""
        # TODO: Implement during TDD
        pass
    
    def area(self) -> float:
        """Calculate circle area."""
        # TODO: Implement during TDD
        pass
    
    def perimeter(self) -> float:
        """Calculate circle perimeter (circumference)."""
        # TODO: Implement during TDD
        pass


class Rectangle(Shape):
    """Rectangle shape implementation."""
    
    def __init__(self, width: float, height: float):
        """Initialize rectangle with width and height."""
        # TODO: Implement during TDD
        pass
    
    def area(self) -> float:
        """Calculate rectangle area."""
        # TODO: Implement during TDD
        pass
    
    def perimeter(self) -> float:
        """Calculate rectangle perimeter."""
        # TODO: Implement during TDD
        pass


class Square(Rectangle):
    """Square shape implementation (inherits from Rectangle)."""
    
    def __init__(self, side: float):
        """Initialize square with side length."""
        # TODO: Implement during TDD
        pass


class Triangle(Shape):
    """Triangle shape implementation."""
    
    def __init__(self, a: float, b: float, c: float):
        """Initialize triangle with three sides."""
        # TODO: Implement during TDD
        pass
    
    def area(self) -> float:
        """Calculate triangle area using Heron's formula."""
        # TODO: Implement during TDD
        pass
    
    def perimeter(self) -> float:
        """Calculate triangle perimeter."""
        # TODO: Implement during TDD
        pass


class ShapeCalculator:
    """Calculator for performing operations on shapes."""
    
    def __init__(self):
        """Initialize the calculator."""
        # TODO: Implement during TDD
        pass
    
    def total_area(self, shapes: list) -> float:
        """Calculate total area of multiple shapes."""
        # TODO: Implement during TDD
        pass
    
    def total_perimeter(self, shapes: list) -> float:
        """Calculate total perimeter of multiple shapes."""
        # TODO: Implement during TDD
        pass
    
    def largest_shape(self, shapes: list) -> Shape:
        """Find the shape with the largest area."""
        # TODO: Implement during TDD
        pass
    
    def smallest_shape(self, shapes: list) -> Shape:
        """Find the shape with the smallest area."""
        # TODO: Implement during TDD
        pass


# TDD Test Cases - Follow the Red-Green-Refactor cycle
class TestTDDCircle(unittest.TestCase):
    """TDD tests for Circle class."""
    
    def test_circle_creation_with_radius(self):
        """Test 1: Circle should be created with a radius."""
        # RED: Write failing test first
        circle = Circle(5)
        self.assertEqual(circle.radius, 5)
    
    def test_circle_area_calculation(self):
        """Test 2: Circle should calculate area correctly."""
        # RED: This will fail initially
        circle = Circle(3)
        expected_area = math.pi * 3 * 3
        self.assertAlmostEqual(circle.area(), expected_area, places=2)
    
    def test_circle_perimeter_calculation(self):
        """Test 3: Circle should calculate perimeter correctly."""
        # RED: This will fail initially
        circle = Circle(4)
        expected_perimeter = 2 * math.pi * 4
        self.assertAlmostEqual(circle.perimeter(), expected_perimeter, places=2)
    
    def test_circle_zero_radius(self):
        """Test 4: Circle with zero radius should have zero area and perimeter."""
        circle = Circle(0)
        self.assertEqual(circle.area(), 0)
        self.assertEqual(circle.perimeter(), 0)
    
    def test_circle_negative_radius_raises_error(self):
        """Test 5: Circle with negative radius should raise ValueError."""
        with self.assertRaises(ValueError):
            Circle(-1)
    
    def test_circle_string_representation(self):
        """Test 6: Circle should have meaningful string representation."""
        circle = Circle(2)
        result = str(circle)
        self.assertIn("Circle", result)
        self.assertIn("area", result)
        self.assertIn("perimeter", result)


class TestTDDRectangle(unittest.TestCase):
    """TDD tests for Rectangle class."""
    
    def test_rectangle_creation_with_dimensions(self):
        """Test 7: Rectangle should be created with width and height."""
        rectangle = Rectangle(5, 3)
        self.assertEqual(rectangle.width, 5)
        self.assertEqual(rectangle.height, 3)
    
    def test_rectangle_area_calculation(self):
        """Test 8: Rectangle should calculate area correctly."""
        rectangle = Rectangle(4, 6)
        self.assertEqual(rectangle.area(), 24)
    
    def test_rectangle_perimeter_calculation(self):
        """Test 9: Rectangle should calculate perimeter correctly."""
        rectangle = Rectangle(3, 5)
        self.assertEqual(rectangle.perimeter(), 16)
    
    def test_rectangle_zero_dimensions(self):
        """Test 10: Rectangle with zero dimensions should have zero area."""
        rectangle = Rectangle(0, 5)
        self.assertEqual(rectangle.area(), 0)
        
        rectangle = Rectangle(3, 0)
        self.assertEqual(rectangle.area(), 0)
    
    def test_rectangle_negative_dimensions_raise_error(self):
        """Test 11: Rectangle with negative dimensions should raise ValueError."""
        with self.assertRaises(ValueError):
            Rectangle(-1, 5)
        
        with self.assertRaises(ValueError):
            Rectangle(5, -1)


class TestTDDSquare(unittest.TestCase):
    """TDD tests for Square class."""
    
    def test_square_creation_with_side(self):
        """Test 12: Square should be created with a side length."""
        square = Square(4)
        self.assertEqual(square.side, 4)
        # Square should inherit width and height from Rectangle
        self.assertEqual(square.width, 4)
        self.assertEqual(square.height, 4)
    
    def test_square_area_calculation(self):
        """Test 13: Square should calculate area correctly."""
        square = Square(5)
        self.assertEqual(square.area(), 25)
    
    def test_square_perimeter_calculation(self):
        """Test 14: Square should calculate perimeter correctly."""
        square = Square(3)
        self.assertEqual(square.perimeter(), 12)
    
    def test_square_is_rectangle(self):
        """Test 15: Square should be an instance of Rectangle."""
        square = Square(2)
        self.assertIsInstance(square, Rectangle)
        self.assertIsInstance(square, Shape)


class TestTDDTriangle(unittest.TestCase):
    """TDD tests for Triangle class."""
    
    def test_triangle_creation_with_sides(self):
        """Test 16: Triangle should be created with three sides."""
        triangle = Triangle(3, 4, 5)
        self.assertEqual(triangle.a, 3)
        self.assertEqual(triangle.b, 4)
        self.assertEqual(triangle.c, 5)
    
    def test_triangle_area_calculation_right_triangle(self):
        """Test 17: Triangle should calculate area correctly for right triangle."""
        # 3-4-5 right triangle has area of 6
        triangle = Triangle(3, 4, 5)
        self.assertAlmostEqual(triangle.area(), 6, places=2)
    
    def test_triangle_perimeter_calculation(self):
        """Test 18: Triangle should calculate perimeter correctly."""
        triangle = Triangle(3, 4, 5)
        self.assertEqual(triangle.perimeter(), 12)
    
    def test_triangle_invalid_sides_raise_error(self):
        """Test 19: Triangle with invalid sides should raise ValueError."""
        # Triangle inequality: sum of any two sides must be greater than the third
        with self.assertRaises(ValueError):
            Triangle(1, 2, 5)  # 1 + 2 < 5
        
        with self.assertRaises(ValueError):
            Triangle(0, 4, 5)  # Zero side length
        
        with self.assertRaises(ValueError):
            Triangle(-1, 4, 5)  # Negative side length
    
    def test_triangle_equilateral(self):
        """Test 20: Equilateral triangle calculations."""
        triangle = Triangle(6, 6, 6)
        self.assertEqual(triangle.perimeter(), 18)
        # Area of equilateral triangle with side 6: (√3/4) * 6²
        expected_area = (math.sqrt(3) / 4) * 36
        self.assertAlmostEqual(triangle.area(), expected_area, places=2)


class TestTDDShapeCalculator(unittest.TestCase):
    """TDD tests for ShapeCalculator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = ShapeCalculator()
        self.circle = Circle(2)
        self.rectangle = Rectangle(3, 4)
        self.square = Square(2)
        self.triangle = Triangle(3, 4, 5)
    
    def test_calculator_creation(self):
        """Test 21: Calculator should be created successfully."""
        calculator = ShapeCalculator()
        self.assertIsInstance(calculator, ShapeCalculator)
    
    def test_total_area_single_shape(self):
        """Test 22: Calculator should sum area of single shape."""
        shapes = [self.circle]
        total = self.calculator.total_area(shapes)
        self.assertAlmostEqual(total, self.circle.area(), places=2)
    
    def test_total_area_multiple_shapes(self):
        """Test 23: Calculator should sum areas of multiple shapes."""
        shapes = [self.circle, self.rectangle, self.square]
        expected_total = self.circle.area() + self.rectangle.area() + self.square.area()
        total = self.calculator.total_area(shapes)
        self.assertAlmostEqual(total, expected_total, places=2)
    
    def test_total_area_empty_list(self):
        """Test 24: Calculator should return 0 for empty list."""
        total = self.calculator.total_area([])
        self.assertEqual(total, 0)
    
    def test_total_perimeter_multiple_shapes(self):
        """Test 25: Calculator should sum perimeters of multiple shapes."""
        shapes = [self.rectangle, self.square]
        expected_total = self.rectangle.perimeter() + self.square.perimeter()
        total = self.calculator.total_perimeter(shapes)
        self.assertAlmostEqual(total, expected_total, places=2)
    
    def test_largest_shape_by_area(self):
        """Test 26: Calculator should find shape with largest area."""
        shapes = [self.circle, self.rectangle, self.square, self.triangle]
        largest = self.calculator.largest_shape(shapes)
        
        # Find the actual largest by comparing areas
        max_area = max(shape.area() for shape in shapes)
        self.assertAlmostEqual(largest.area(), max_area, places=2)
    
    def test_smallest_shape_by_area(self):
        """Test 27: Calculator should find shape with smallest area."""
        shapes = [self.circle, self.rectangle, self.square, self.triangle]
        smallest = self.calculator.smallest_shape(shapes)
        
        # Find the actual smallest by comparing areas
        min_area = min(shape.area() for shape in shapes)
        self.assertAlmostEqual(smallest.area(), min_area, places=2)
    
    def test_calculator_with_single_shape(self):
        """Test 28: Calculator methods should work with single shape."""
        shapes = [self.circle]
        
        largest = self.calculator.largest_shape(shapes)
        smallest = self.calculator.smallest_shape(shapes)
        
        self.assertEqual(largest, self.circle)
        self.assertEqual(smallest, self.circle)
    
    def test_calculator_empty_list_raises_error(self):
        """Test 29: Calculator should raise error for empty list in min/max operations."""
        with self.assertRaises(ValueError):
            self.calculator.largest_shape([])
        
        with self.assertRaises(ValueError):
            self.calculator.smallest_shape([])


# TDD Implementation Examples (Reference Solutions)
class CircleSolution(Shape):
    """Complete Circle implementation for reference."""
    
    def __init__(self, radius: float):
        if radius < 0:
            raise ValueError("Radius cannot be negative")
        self.radius = radius
    
    def area(self) -> float:
        return math.pi * self.radius ** 2
    
    def perimeter(self) -> float:
        return 2 * math.pi * self.radius


class RectangleSolution(Shape):
    """Complete Rectangle implementation for reference."""
    
    def __init__(self, width: float, height: float):
        if width < 0 or height < 0:
            raise ValueError("Dimensions cannot be negative")
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class SquareSolution(RectangleSolution):
    """Complete Square implementation for reference."""
    
    def __init__(self, side: float):
        super().__init__(side, side)
        self.side = side


class TriangleSolution(Shape):
    """Complete Triangle implementation for reference."""
    
    def __init__(self, a: float, b: float, c: float):
        if a <= 0 or b <= 0 or c <= 0:
            raise ValueError("Side lengths must be positive")
        
        # Check triangle inequality
        if a + b <= c or a + c <= b or b + c <= a:
            raise ValueError("Invalid triangle: triangle inequality violated")
        
        self.a = a
        self.b = b
        self.c = c
    
    def area(self) -> float:
        # Heron's formula
        s = self.perimeter() / 2
        return math.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
    
    def perimeter(self) -> float:
        return self.a + self.b + self.c


class ShapeCalculatorSolution:
    """Complete ShapeCalculator implementation for reference."""
    
    def total_area(self, shapes: list) -> float:
        return sum(shape.area() for shape in shapes)
    
    def total_perimeter(self, shapes: list) -> float:
        return sum(shape.perimeter() for shape in shapes)
    
    def largest_shape(self, shapes: list) -> Shape:
        if not shapes:
            raise ValueError("Cannot find largest shape in empty list")
        return max(shapes, key=lambda shape: shape.area())
    
    def smallest_shape(self, shapes: list) -> Shape:
        if not shapes:
            raise ValueError("Cannot find smallest shape in empty list")
        return min(shapes, key=lambda shape: shape.area())


def run_tdd_demonstration():
    """Demonstrate the TDD process step by step."""
    print("TDD Shape Calculator Exercise")
    print("=" * 50)
    print("Follow these steps:")
    print("1. RED: Write a failing test")
    print("2. GREEN: Write minimal code to pass the test")
    print("3. REFACTOR: Improve the code while keeping tests passing")
    print("4. Repeat for each new feature")
    print("\nStart with the Circle class and work through each test case.")
    print("=" * 50)
    
    # Run initial tests (will fail until implemented)
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTDDCircle))
    suite.addTest(unittest.makeSuite(TestTDDRectangle))
    suite.addTest(unittest.makeSuite(TestTDDSquare))
    suite.addTest(unittest.makeSuite(TestTDDTriangle))
    suite.addTest(unittest.makeSuite(TestTDDShapeCalculator))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    run_tdd_demonstration()