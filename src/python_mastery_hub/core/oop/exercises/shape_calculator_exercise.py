"""
Shape Calculator exercise for the OOP module.
Create a polymorphic shape system with area and perimeter calculations.
"""

from typing import Dict, Any


def get_shape_calculator_exercise() -> Dict[str, Any]:
    """Get the Shape Calculator exercise."""
    return {
        "title": "Polymorphic Shape Calculator",
        "difficulty": "hard",
        "estimated_time": "2-2.5 hours",
        "instructions": """
Create a comprehensive shape calculation system that demonstrates polymorphism
through abstract base classes and method overriding. Your system should handle
different geometric shapes with consistent interfaces while providing
shape-specific implementations.

This exercise focuses on abstract classes, polymorphism, operator overloading,
and building flexible, extensible object hierarchies.
""",
        "learning_objectives": [
            "Apply abstract base classes to define interfaces",
            "Implement polymorphic methods for different shapes",
            "Use operator overloading for natural shape comparisons",
            "Practice inheritance with mathematical calculations",
            "Build extensible systems with consistent APIs"
        ],
        "tasks": [
            {
                "step": 1,
                "title": "Create Abstract Shape Base Class",
                "description": "Design abstract Shape class with common interface",
                "requirements": [
                    "Use ABC to create abstract base class",
                    "Define abstract methods: area() and perimeter()",
                    "Add concrete methods for common functionality",
                    "Implement comparison operators based on area"
                ]
            },
            {
                "step": 2,
                "title": "Implement Concrete Shape Classes",
                "description": "Create Rectangle, Circle, and Triangle classes",
                "requirements": [
                    "Each class inherits from Shape base class",
                    "Implement area() and perimeter() for each shape",
                    "Add shape-specific validation in constructors",
                    "Include string representations for debugging"
                ]
            },
            {
                "step": 3,
                "title": "Add Shape Calculator Class",
                "description": "Create calculator to work with shapes polymorphically",
                "requirements": [
                    "Accept any shape type through polymorphism",
                    "Calculate total area and perimeter of shape collections",
                    "Find largest/smallest shapes by different criteria",
                    "Generate shape statistics and reports"
                ]
            },
            {
                "step": 4,
                "title": "Implement Operator Overloading",
                "description": "Add natural comparison operations between shapes",
                "requirements": [
                    "Implement <, >, ==, != based on area comparison",
                    "Add + operator to combine shape areas",
                    "Create * operator for scaling shapes",
                    "Support len() for shape perimeter"
                ]
            },
            {
                "step": 5,
                "title": "Add Advanced Features",
                "description": "Extend with sophisticated shape operations",
                "requirements": [
                    "Create composite shapes (multiple shapes as one)",
                    "Add shape transformation methods (scale, rotate)",
                    "Implement shape factory for creating shapes from parameters",
                    "Add shape validation and error handling"
                ]
            }
        ],
        "starter_code": '''
from abc import ABC, abstractmethod
import math
from typing import List, Union, Dict, Any

class Shape(ABC):
    """Abstract base class for all geometric shapes."""
    
    def __init__(self, name: str):
        # TODO: Initialize with validation
        pass
    
    @abstractmethod
    def area(self) -> float:
        """Calculate and return the area of the shape."""
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        """Calculate and return the perimeter of the shape."""
        pass
    
    def __lt__(self, other) -> bool:
        """Compare shapes by area."""
        # TODO: Implement less than comparison
        pass
    
    def __eq__(self, other) -> bool:
        """Check if shapes have equal area."""
        # TODO: Implement equality comparison
        pass
    
    def __str__(self) -> str:
        # TODO: Return readable string representation
        pass

class Rectangle(Shape):
    """Rectangle shape implementation."""
    
    def __init__(self, width: float, height: float):
        # TODO: Implement initialization with validation
        pass
    
    def area(self) -> float:
        # TODO: Calculate rectangle area
        pass
    
    def perimeter(self) -> float:
        # TODO: Calculate rectangle perimeter
        pass

class Circle(Shape):
    """Circle shape implementation."""
    
    def __init__(self, radius: float):
        # TODO: Implement initialization with validation
        pass
    
    def area(self) -> float:
        # TODO: Calculate circle area
        pass
    
    def perimeter(self) -> float:
        # TODO: Calculate circle perimeter (circumference)
        pass

class Triangle(Shape):
    """Triangle shape implementation."""
    
    def __init__(self, side_a: float, side_b: float, side_c: float):
        # TODO: Implement initialization with validation
        pass
    
    def area(self) -> float:
        # TODO: Calculate triangle area using Heron's formula
        pass
    
    def perimeter(self) -> float:
        # TODO: Calculate triangle perimeter
        pass

class ShapeCalculator:
    """Calculator for performing operations on collections of shapes."""
    
    def __init__(self):
        # TODO: Initialize calculator
        pass
    
    def add_shape(self, shape: Shape) -> str:
        """Add a shape to the calculator."""
        # TODO: Implement shape addition
        pass
    
    def total_area(self) -> float:
        """Calculate total area of all shapes."""
        # TODO: Use polymorphism to calculate total area
        pass
    
    def largest_shape(self) -> Shape:
        """Find the shape with the largest area."""
        # TODO: Implement shape comparison
        pass
    
    def shapes_by_area(self) -> List[Shape]:
        """Return shapes sorted by area (largest first)."""
        # TODO: Implement sorting
        pass

# Test your implementation
if __name__ == "__main__":
    # Create shapes
    rectangle = Rectangle(5, 3)
    circle = Circle(2)
    triangle = Triangle(3, 4, 5)
    
    # Create calculator
    calc = ShapeCalculator()
    calc.add_shape(rectangle)
    calc.add_shape(circle)
    calc.add_shape(triangle)
    
    # Test polymorphic operations
    print(f"Total area: {calc.total_area():.2f}")
    largest = calc.largest_shape()
    print(f"Largest shape: {largest}")
    
    # Test comparisons
    print(f"Rectangle > Circle: {rectangle > circle}")
    print(f"Shapes by area: {[str(s) for s in calc.shapes_by_area()]}")
''',
        "hints": [
            "Use math.pi for circle calculations",
            "Heron's formula: area = sqrt(s * (s-a) * (s-b) * (s-c)) where s = perimeter/2",
            "Validate triangle inequality: sum of any two sides > third side",
            "Use isinstance() to check shape types in comparisons",
            "Consider floating-point precision when comparing areas",
            "Abstract methods must be implemented in all concrete classes",
            "Use super().__init__() to call parent constructor"
        ],
        "solution": '''
from abc import ABC, abstractmethod
import math
from typing import List, Union, Dict, Any, Optional

class Shape(ABC):
    """Abstract base class for all geometric shapes."""
    
    def __init__(self, name: str):
        if not name or not name.strip():
            raise ValueError("Shape name cannot be empty")
        self.name = name.strip()
    
    @abstractmethod
    def area(self) -> float:
        """Calculate and return the area of the shape."""
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        """Calculate and return the perimeter of the shape."""
        pass
    
    def __lt__(self, other) -> bool:
        """Compare shapes by area."""
        if not isinstance(other, Shape):
            return NotImplemented
        return self.area() < other.area()
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, Shape):
            return NotImplemented
        return self.area() <= other.area()
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, Shape):
            return NotImplemented
        return self.area() > other.area()
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, Shape):
            return NotImplemented
        return self.area() >= other.area()
    
    def __eq__(self, other) -> bool:
        """Check if shapes have equal area."""
        if not isinstance(other, Shape):
            return False
        return abs(self.area() - other.area()) < 1e-9  # Account for floating point precision
    
    def __ne__(self, other) -> bool:
        """Check if shapes have different areas."""
        return not self.__eq__(other)
    
    def __add__(self, other) -> float:
        """Add areas of two shapes."""
        if isinstance(other, Shape):
            return self.area() + other.area()
        elif isinstance(other, (int, float)):
            return self.area() + other
        return NotImplemented
    
    def __radd__(self, other) -> float:
        """Reverse addition."""
        return self.__add__(other)
    
    def __mul__(self, factor) -> 'Shape':
        """Scale shape by a factor."""
        if isinstance(factor, (int, float)) and factor > 0:
            return self.scale(factor)
        return NotImplemented
    
    def __rmul__(self, factor) -> 'Shape':
        """Reverse multiplication."""
        return self.__mul__(factor)
    
    def __len__(self) -> int:
        """Return perimeter as integer."""
        return int(self.perimeter())
    
    def scale(self, factor: float) -> 'Shape':
        """Create a scaled version of the shape."""
        # This is overridden in concrete classes
        raise NotImplementedError("Scale method must be implemented by subclasses")
    
    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive shape information."""
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'area': round(self.area(), 4),
            'perimeter': round(self.perimeter(), 4),
            'area_to_perimeter_ratio': round(self.area() / self.perimeter(), 4) if self.perimeter() > 0 else 0
        }
    
    def __str__(self) -> str:
        return f"{self.name}: Area = {self.area():.2f}, Perimeter = {self.perimeter():.2f}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

class Rectangle(Shape):
    """Rectangle shape implementation."""
    
    def __init__(self, width: float, height: float, name: str = "Rectangle"):
        super().__init__(name)
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self.width = width
        self.height = height
    
    def area(self) -> float:
        """Calculate rectangle area."""
        return self.width * self.height
    
    def perimeter(self) -> float:
        """Calculate rectangle perimeter."""
        return 2 * (self.width + self.height)
    
    def scale(self, factor: float) -> 'Rectangle':
        """Create a scaled rectangle."""
        return Rectangle(self.width * factor, self.height * factor, f"Scaled {self.name}")
    
    def is_square(self) -> bool:
        """Check if rectangle is a square."""
        return abs(self.width - self.height) < 1e-9
    
    def diagonal(self) -> float:
        """Calculate diagonal length."""
        return math.sqrt(self.width**2 + self.height**2)
    
    def __repr__(self) -> str:
        return f"Rectangle(width={self.width}, height={self.height})"

class Circle(Shape):
    """Circle shape implementation."""
    
    def __init__(self, radius: float, name: str = "Circle"):
        super().__init__(name)
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.radius = radius
    
    def area(self) -> float:
        """Calculate circle area."""
        return math.pi * self.radius ** 2
    
    def perimeter(self) -> float:
        """Calculate circle perimeter (circumference)."""
        return 2 * math.pi * self.radius
    
    def scale(self, factor: float) -> 'Circle':
        """Create a scaled circle."""
        return Circle(self.radius * factor, f"Scaled {self.name}")
    
    def diameter(self) -> float:
        """Get circle diameter."""
        return 2 * self.radius
    
    def __repr__(self) -> str:
        return f"Circle(radius={self.radius})"

class Triangle(Shape):
    """Triangle shape implementation."""
    
    def __init__(self, side_a: float, side_b: float, side_c: float, name: str = "Triangle"):
        super().__init__(name)
        if side_a <= 0 or side_b <= 0 or side_c <= 0:
            raise ValueError("All sides must be positive")
        
        # Check triangle inequality
        if (side_a + side_b <= side_c or 
            side_a + side_c <= side_b or 
            side_b + side_c <= side_a):
            raise ValueError("Triangle inequality violated: sum of any two sides must be greater than the third")
        
        self.side_a = side_a
        self.side_b = side_b
        self.side_c = side_c
    
    def area(self) -> float:
        """Calculate triangle area using Heron's formula."""
        s = self.perimeter() / 2  # Semi-perimeter
        return math.sqrt(s * (s - self.side_a) * (s - self.side_b) * (s - self.side_c))
    
    def perimeter(self) -> float:
        """Calculate triangle perimeter."""
        return self.side_a + self.side_b + self.side_c
    
    def scale(self, factor: float) -> 'Triangle':
        """Create a scaled triangle."""
        return Triangle(
            self.side_a * factor, 
            self.side_b * factor, 
            self.side_c * factor, 
            f"Scaled {self.name}"
        )
    
    def is_equilateral(self) -> bool:
        """Check if triangle is equilateral."""
        return (abs(self.side_a - self.side_b) < 1e-9 and 
                abs(self.side_b - self.side_c) < 1e-9)
    
    def is_isosceles(self) -> bool:
        """Check if triangle is isosceles."""
        return (abs(self.side_a - self.side_b) < 1e-9 or
                abs(self.side_b - self.side_c) < 1e-9 or
                abs(self.side_a - self.side_c) < 1e-9)
    
    def is_right_triangle(self) -> bool:
        """Check if triangle is a right triangle."""
        sides = sorted([self.side_a, self.side_b, self.side_c])
        return abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-9
    
    def triangle_type(self) -> str:
        """Get descriptive triangle type."""
        if self.is_equilateral():
            return "Equilateral"
        elif self.is_isosceles():
            return "Isosceles"
        elif self.is_right_triangle():
            return "Right"
        else:
            return "Scalene"
    
    def __repr__(self) -> str:
        return f"Triangle(sides=({self.side_a}, {self.side_b}, {self.side_c}))"

class CompositeShape(Shape):
    """Composite shape containing multiple shapes."""
    
    def __init__(self, shapes: List[Shape], name: str = "Composite Shape"):
        super().__init__(name)
        if not shapes:
            raise ValueError("Composite shape must contain at least one shape")
        self.shapes = shapes[:]  # Create copy
    
    def area(self) -> float:
        """Calculate total area of all component shapes."""
        return sum(shape.area() for shape in self.shapes)
    
    def perimeter(self) -> float:
        """Calculate total perimeter of all component shapes."""
        return sum(shape.perimeter() for shape in self.shapes)
    
    def scale(self, factor: float) -> 'CompositeShape':
        """Create a scaled composite shape."""
        scaled_shapes = [shape.scale(factor) for shape in self.shapes]
        return CompositeShape(scaled_shapes, f"Scaled {self.name}")
    
    def add_shape(self, shape: Shape) -> None:
        """Add a shape to the composite."""
        self.shapes.append(shape)
    
    def remove_shape(self, index: int) -> Shape:
        """Remove and return a shape by index."""
        if 0 <= index < len(self.shapes):
            return self.shapes.pop(index)
        raise IndexError("Shape index out of range")
    
    def get_component_info(self) -> List[Dict[str, Any]]:
        """Get information about all component shapes."""
        return [shape.get_info() for shape in self.shapes]
    
    def __len__(self) -> int:
        """Return number of component shapes."""
        return len(self.shapes)
    
    def __repr__(self) -> str:
        return f"CompositeShape(shapes={len(self.shapes)})"

class ShapeCalculator:
    """Calculator for performing operations on collections of shapes."""
    
    def __init__(self):
        self.shapes: List[Shape] = []
        self.calculation_history: List[Dict[str, Any]] = []
    
    def add_shape(self, shape: Shape) -> str:
        """Add a shape to the calculator."""
        if not isinstance(shape, Shape):
            raise TypeError("Object must be a Shape instance")
        
        self.shapes.append(shape)
        self._log_operation("ADD_SHAPE", {"shape": str(shape)})
        return f"Added {shape.name} to calculator"
    
    def remove_shape(self, index: int) -> str:
        """Remove a shape by index."""
        if 0 <= index < len(self.shapes):
            removed_shape = self.shapes.pop(index)
            self._log_operation("REMOVE_SHAPE", {"shape": str(removed_shape)})
            return f"Removed {removed_shape.name} from calculator"
        raise IndexError("Shape index out of range")
    
    def clear_shapes(self) -> str:
        """Remove all shapes."""
        count = len(self.shapes)
        self.shapes.clear()
        self._log_operation("CLEAR_SHAPES", {"count": count})
        return f"Removed {count} shapes from calculator"
    
    def total_area(self) -> float:
        """Calculate total area of all shapes."""
        total = sum(shape.area() for shape in self.shapes)
        self._log_operation("TOTAL_AREA", {"result": total})
        return total
    
    def total_perimeter(self) -> float:
        """Calculate total perimeter of all shapes."""
        total = sum(shape.perimeter() for shape in self.shapes)
        self._log_operation("TOTAL_PERIMETER", {"result": total})
        return total
    
    def average_area(self) -> float:
        """Calculate average area of all shapes."""
        if not self.shapes:
            return 0.0
        return self.total_area() / len(self.shapes)
    
    def largest_shape(self) -> Optional[Shape]:
        """Find the shape with the largest area."""
        if not self.shapes:
            return None
        return max(self.shapes, key=lambda shape: shape.area())
    
    def smallest_shape(self) -> Optional[Shape]:
        """Find the shape with the smallest area."""
        if not self.shapes:
            return None
        return min(self.shapes, key=lambda shape: shape.area())
    
    def shapes_by_area(self, reverse: bool = True) -> List[Shape]:
        """Return shapes sorted by area."""
        return sorted(self.shapes, key=lambda shape: shape.area(), reverse=reverse)
    
    def shapes_by_perimeter(self, reverse: bool = True) -> List[Shape]:
        """Return shapes sorted by perimeter."""
        return sorted(self.shapes, key=lambda shape: shape.perimeter(), reverse=reverse)
    
    def filter_shapes_by_type(self, shape_type: type) -> List[Shape]:
        """Filter shapes by type."""
        return [shape for shape in self.shapes if isinstance(shape, shape_type)]
    
    def filter_shapes_by_area_range(self, min_area: float, max_area: float) -> List[Shape]:
        """Filter shapes by area range."""
        return [shape for shape in self.shapes 
                if min_area <= shape.area() <= max_area]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about all shapes."""
        if not self.shapes:
            return {"message": "No shapes in calculator"}
        
        areas = [shape.area() for shape in self.shapes]
        perimeters = [shape.perimeter() for shape in self.shapes]
        
        # Count by type
        type_counts = {}
        for shape in self.shapes:
            shape_type = shape.__class__.__name__
            type_counts[shape_type] = type_counts.get(shape_type, 0) + 1
        
        return {
            'total_shapes': len(self.shapes),
            'total_area': sum(areas),
            'total_perimeter': sum(perimeters),
            'average_area': sum(areas) / len(areas),
            'average_perimeter': sum(perimeters) / len(perimeters),
            'largest_area': max(areas),
            'smallest_area': min(areas),
            'area_range': max(areas) - min(areas),
            'shape_types': type_counts,
            'calculations_performed': len(self.calculation_history)
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive text report."""
        if not self.shapes:
            return "No shapes to analyze."
        
        stats = self.get_statistics()
        
        report = f"""
=== Shape Calculator Report ===
Total Shapes: {stats['total_shapes']}
Total Area: {stats['total_area']:.2f}
Total Perimeter: {stats['total_perimeter']:.2f}
Average Area: {stats['average_area']:.2f}
Average Perimeter: {stats['average_perimeter']:.2f}

Area Statistics:
  Largest: {stats['largest_area']:.2f}
  Smallest: {stats['smallest_area']:.2f}
  Range: {stats['area_range']:.2f}

Shape Types:"""
        
        for shape_type, count in stats['shape_types'].items():
            report += f"\\n  {shape_type}: {count}"
        
        report += f"\\n\\nCalculations Performed: {stats['calculations_performed']}"
        
        return report
    
    def _log_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """Log an operation for history tracking."""
        log_entry = {
            'operation': operation,
            'timestamp': str(len(self.calculation_history)),  # Simple counter
            'details': details
        }
        self.calculation_history.append(log_entry)
    
    def __len__(self) -> int:
        """Return number of shapes in calculator."""
        return len(self.shapes)
    
    def __str__(self) -> str:
        return f"ShapeCalculator({len(self.shapes)} shapes, total area: {self.total_area():.2f})"

class ShapeFactory:
    """Factory for creating shapes from parameters."""
    
    @staticmethod
    def create_shape(shape_type: str, **kwargs) -> Shape:
        """Create a shape of the specified type."""
        shape_type = shape_type.lower()
        
        if shape_type == "rectangle":
            return Rectangle(kwargs.get('width', 1), kwargs.get('height', 1), 
                           kwargs.get('name', 'Rectangle'))
        elif shape_type == "circle":
            return Circle(kwargs.get('radius', 1), kwargs.get('name', 'Circle'))
        elif shape_type == "triangle":
            return Triangle(kwargs.get('side_a', 1), kwargs.get('side_b', 1), 
                          kwargs.get('side_c', 1), kwargs.get('name', 'Triangle'))
        elif shape_type == "square":
            side = kwargs.get('side', 1)
            return Rectangle(side, side, kwargs.get('name', 'Square'))
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")
    
    @staticmethod
    def create_regular_polygon_approximation(sides: int, side_length: float) -> CompositeShape:
        """Create a regular polygon approximation using triangles."""
        if sides < 3:
            raise ValueError("Polygon must have at least 3 sides")
        
        # This is a simplified approximation
        triangles = []
        for i in range(sides):
            # Create triangular segments (simplified)
            triangles.append(Triangle(side_length, side_length, side_length * 0.8))
        
        return CompositeShape(triangles, f"{sides}-sided Polygon")

# Comprehensive demonstration
def demonstrate_shape_calculator():
    """Demonstrate the complete shape calculator system."""
    print("=== Polymorphic Shape Calculator Demo ===\\n")
    
    # Create various shapes
    shapes = [
        Rectangle(5, 3, "Small Rectangle"),
        Circle(2, "Small Circle"),
        Triangle(3, 4, 5, "Right Triangle"),
        Rectangle(4, 4, "Square"),
        Circle(3, "Medium Circle"),
        Triangle(6, 6, 6, "Equilateral Triangle")
    ]
    
    print("Created shapes:")
    for shape in shapes:
        print(f"  {shape}")
        print(f"    Type: {shape.triangle_type() if isinstance(shape, Triangle) else shape.__class__.__name__}")
        if isinstance(shape, Rectangle):
            print(f"    Is Square: {shape.is_square()}")
            print(f"    Diagonal: {shape.diagonal():.2f}")
    
    # Create calculator and add shapes
    calc = ShapeCalculator()
    print(f"\\nAdding shapes to calculator:")
    for shape in shapes:
        print(f"  {calc.add_shape(shape)}")
    
    # Test polymorphic operations
    print(f"\\n=== Polymorphic Operations ===")
    print(f"Total area: {calc.total_area():.2f}")
    print(f"Total perimeter: {calc.total_perimeter():.2f}")
    print(f"Average area: {calc.average_area():.2f}")
    
    largest = calc.largest_shape()
    smallest = calc.smallest_shape()
    print(f"Largest shape: {largest.name} (area: {largest.area():.2f})")
    print(f"Smallest shape: {smallest.name} (area: {smallest.area():.2f})")
    
    # Test operator overloading
    print(f"\\n=== Operator Overloading ===")
    rect = shapes[0]
    circle = shapes[1]
    print(f"Rectangle > Circle: {rect > circle}")
    print(f"Rectangle == Circle: {rect == circle}")
    print(f"Combined area: {rect + circle:.2f}")
    print(f"Rectangle length (perimeter): {len(rect)}")
    
    # Test scaling
    print(f"\\n=== Shape Scaling ===")
    scaled_rect = rect.scale(2.0)
    print(f"Original rectangle: {rect}")
    print(f"Scaled rectangle (2x): {scaled_rect}")
    
    # Create composite shape
    print(f"\\n=== Composite Shapes ===")
    composite = CompositeShape([rect, circle], "Rectangle + Circle")
    print(f"Composite shape: {composite}")
    print(f"Component count: {len(composite)}")
    
    # Filter operations
    print(f"\\n=== Filtering Operations ===")
    rectangles = calc.filter_shapes_by_type(Rectangle)
    circles = calc.filter_shapes_by_type(Circle)
    triangles = calc.filter_shapes_by_type(Triangle)
    
    print(f"Rectangles: {len(rectangles)}")
    print(f"Circles: {len(circles)}")
    print(f"Triangles: {len(triangles)}")
    
    large_shapes = calc.filter_shapes_by_area_range(20, 100)
    print(f"Large shapes (area 20-100): {len(large_shapes)}")
    
    # Sorting
    print(f"\\n=== Sorting Operations ===")
    by_area = calc.shapes_by_area()
    print("Shapes by area (largest first):")
    for i, shape in enumerate(by_area[:3]):
        print(f"  {i+1}. {shape.name}: {shape.area():.2f}")
    
    # Generate comprehensive report
    print(calc.generate_report())
    
    # Test shape factory
    print(f"\\n=== Shape Factory ===")
    factory_shapes = [
        ShapeFactory.create_shape("rectangle", width=6, height=4),
        ShapeFactory.create_shape("circle", radius=2.5),
        ShapeFactory.create_shape("square", side=3),
    ]
    
    for shape in factory_shapes:
        print(f"Factory created: {shape}")
    
    print("\\n=== Demo Complete ===")

if __name__ == "__main__":
    demonstrate_shape_calculator()
'''
    }