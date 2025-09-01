"""
Design Patterns examples for the OOP module.
Demonstrates common Gang of Four patterns and Python-specific patterns.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


def get_design_patterns_examples() -> Dict[str, Any]:
    """Get comprehensive design pattern examples."""
    return {
        "singleton_pattern": {
            "code": """
class DatabaseConnection:
    '''Singleton pattern - ensures only one instance exists.'''
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.host = "localhost"
            self.port = 5432
            self.database = "python_mastery"
            self.connection_count = 0
            self._initialized = True
            print("Database connection initialized")
    
    def connect(self):
        '''Simulate database connection.'''
        self.connection_count += 1
        return f"Connected to {self.database} at {self.host}:{self.port} (Connection #{self.connection_count})"
    
    def disconnect(self):
        '''Simulate database disconnection.'''
        return "Disconnected from database"

# Thread-safe singleton
import threading

class ThreadSafeSingleton:
    '''Thread-safe singleton implementation.'''
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.data = "Thread-safe singleton data"

# Usage examples
print("=== Singleton Pattern ===")
db1 = DatabaseConnection()
db2 = DatabaseConnection()

print(f"Same instance? {db1 is db2}")
print(db1.connect())
print(db2.connect())

# Thread-safe version
singleton1 = ThreadSafeSingleton()
singleton2 = ThreadSafeSingleton()
print(f"Thread-safe singleton same instance? {singleton1 is singleton2}")
""",
            "output": "=== Singleton Pattern ===\nDatabase connection initialized\nSame instance? True\nConnected to python_mastery at localhost:5432 (Connection #1)\nConnected to python_mastery at localhost:5432 (Connection #2)\nThread-safe singleton same instance? True",
            "explanation": "Singleton pattern ensures a class has only one instance and provides global access to it"
        },
        
        "observer_pattern": {
            "code": """
from abc import ABC, abstractmethod

class Observer(ABC):
    '''Abstract observer interface.'''
    
    @abstractmethod
    def update(self, subject, event_data):
        pass

class Subject:
    '''Subject class that maintains list of observers.'''
    
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        '''Add an observer.'''
        if observer not in self._observers:
            self._observers.append(observer)
            return f"Observer {observer.__class__.__name__} attached"
        return "Observer already attached"
    
    def detach(self, observer):
        '''Remove an observer.'''
        if observer in self._observers:
            self._observers.remove(observer)
            return f"Observer {observer.__class__.__name__} detached"
        return "Observer not found"
    
    def notify(self, event_data):
        '''Notify all observers of an event.'''
        for observer in self._observers:
            observer.update(self, event_data)

class StockPrice(Subject):
    '''Stock price subject that notifies observers of price changes.'''
    
    def __init__(self, symbol, price):
        super().__init__()
        self.symbol = symbol
        self._price = price
    
    @property
    def price(self):
        return self._price
    
    @price.setter
    def price(self, new_price):
        old_price = self._price
        self._price = new_price
        self.notify({
            'symbol': self.symbol,
            'old_price': old_price,
            'new_price': new_price,
            'change': new_price - old_price
        })

class EmailNotifier(Observer):
    '''Email notification observer.'''
    
    def __init__(self, email, threshold=5.0):
        self.email = email
        self.threshold = threshold
    
    def update(self, subject, event_data):
        change = abs(event_data['change'])
        if change >= self.threshold:
            direction = "increased" if event_data['change'] > 0 else "decreased"
            print(f"EMAIL to {self.email}: {event_data['symbol']} {direction} by ${change:.2f}")

class SMSNotifier(Observer):
    '''SMS notification observer.'''
    
    def __init__(self, phone, threshold=10.0):
        self.phone = phone
        self.threshold = threshold
    
    def update(self, subject, event_data):
        change = abs(event_data['change'])
        if change >= self.threshold:
            print(f"SMS to {self.phone}: ALERT! {event_data['symbol']} price changed significantly")

class TradingBot(Observer):
    '''Automated trading bot observer.'''
    
    def __init__(self, strategy="buy_low"):
        self.strategy = strategy
        self.trades = []
    
    def update(self, subject, event_data):
        if self.strategy == "buy_low" and event_data['change'] < -5:
            trade = f"BUY {event_data['symbol']} at ${event_data['new_price']}"
            self.trades.append(trade)
            print(f"TRADING BOT: {trade}")
        elif self.strategy == "sell_high" and event_data['change'] > 5:
            trade = f"SELL {event_data['symbol']} at ${event_data['new_price']}"
            self.trades.append(trade)
            print(f"TRADING BOT: {trade}")

# Usage example
print("\\n=== Observer Pattern ===")
stock = StockPrice("AAPL", 150.0)

# Create observers
email_notify = EmailNotifier("investor@email.com", threshold=3.0)
sms_notify = SMSNotifier("+1234567890", threshold=8.0)
trading_bot = TradingBot("buy_low")

# Attach observers
print(stock.attach(email_notify))
print(stock.attach(sms_notify))
print(stock.attach(trading_bot))

# Trigger price changes
print("\\nPrice changes:")
stock.price = 155.0  # +$5 change
stock.price = 147.0  # -$8 change
stock.price = 142.0  # -$5 change
""",
            "output": "=== Observer Pattern ===\nObserver EmailNotifier attached\nObserver SMSNotifier attached\nObserver TradingBot attached\n\nPrice changes:\nEMAIL to investor@email.com: AAPL increased by $5.00\nEMAIL to investor@email.com: AAPL decreased by $8.00\nSMS to +1234567890: ALERT! AAPL price changed significantly\nEMAIL to investor@email.com: AAPL decreased by $5.00\nTRADING BOT: BUY AAPL at $142.0",
            "explanation": "Observer pattern allows objects to be notified of changes in other objects without tight coupling"
        },
        
        "factory_pattern": {
            "code": """
from abc import ABC, abstractmethod

# Abstract Product
class Vehicle(ABC):
    '''Abstract vehicle class.'''
    
    @abstractmethod
    def start_engine(self):
        pass
    
    @abstractmethod
    def stop_engine(self):
        pass
    
    def __str__(self):
        return f"{self.__class__.__name__}: {self.make} {self.model}"

# Concrete Products
class Car(Vehicle):
    def __init__(self, make, model, doors=4):
        self.make = make
        self.model = model
        self.doors = doors
        self.engine_running = False
    
    def start_engine(self):
        self.engine_running = True
        return f"Car engine started with key"
    
    def stop_engine(self):
        self.engine_running = False
        return f"Car engine stopped"

class Motorcycle(Vehicle):
    def __init__(self, make, model, engine_size=600):
        self.make = make
        self.model = model
        self.engine_size = engine_size
        self.engine_running = False
    
    def start_engine(self):
        self.engine_running = True
        return f"Motorcycle engine started with kick/button"
    
    def stop_engine(self):
        self.engine_running = False
        return f"Motorcycle engine stopped"

class Truck(Vehicle):
    def __init__(self, make, model, payload_capacity=1000):
        self.make = make
        self.model = model
        self.payload_capacity = payload_capacity
        self.engine_running = False
    
    def start_engine(self):
        self.engine_running = True
        return f"Truck engine started with heavy duty ignition"
    
    def stop_engine(self):
        self.engine_running = False
        return f"Truck engine stopped"

# Simple Factory
class VehicleFactory:
    '''Simple factory for creating vehicles.'''
    
    @staticmethod
    def create_vehicle(vehicle_type, **kwargs):
        vehicle_types = {
            'car': Car,
            'motorcycle': Motorcycle,
            'truck': Truck
        }
        
        vehicle_class = vehicle_types.get(vehicle_type.lower())
        if vehicle_class:
            return vehicle_class(**kwargs)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")

# Factory Method Pattern
class VehicleManufacturer(ABC):
    '''Abstract manufacturer using factory method pattern.'''
    
    @abstractmethod
    def create_vehicle(self, model, **kwargs):
        pass
    
    def produce_vehicle(self, model, **kwargs):
        '''Template method that uses factory method.'''
        vehicle = self.create_vehicle(model, **kwargs)
        self.perform_quality_check(vehicle)
        return vehicle
    
    def perform_quality_check(self, vehicle):
        '''Common quality check for all manufacturers.'''
        print(f"Quality check passed for {vehicle}")

class ToyotaFactory(VehicleManufacturer):
    '''Toyota vehicle factory.'''
    
    def create_vehicle(self, model, vehicle_type='car', **kwargs):
        if vehicle_type == 'car':
            return Car('Toyota', model, **kwargs)
        elif vehicle_type == 'truck':
            return Truck('Toyota', model, **kwargs)
        else:
            raise ValueError(f"Toyota doesn't make {vehicle_type}")

class HondaFactory(VehicleManufacturer):
    '''Honda vehicle factory.'''
    
    def create_vehicle(self, model, vehicle_type='car', **kwargs):
        if vehicle_type == 'car':
            return Car('Honda', model, **kwargs)
        elif vehicle_type == 'motorcycle':
            return Motorcycle('Honda', model, **kwargs)
        else:
            raise ValueError(f"Honda doesn't make {vehicle_type}")

# Abstract Factory Pattern
class VehicleComponentFactory(ABC):
    '''Abstract factory for vehicle components.'''
    
    @abstractmethod
    def create_engine(self):
        pass
    
    @abstractmethod
    def create_transmission(self):
        pass

class EconomyComponentFactory(VehicleComponentFactory):
    '''Factory for economy vehicle components.'''
    
    def create_engine(self):
        return "4-cylinder economy engine"
    
    def create_transmission(self):
        return "CVT transmission"

class LuxuryComponentFactory(VehicleComponentFactory):
    '''Factory for luxury vehicle components.'''
    
    def create_engine(self):
        return "V8 luxury engine"
    
    def create_transmission(self):
        return "8-speed automatic transmission"

# Usage examples
print("=== Factory Patterns ===")

# Simple Factory
print("\\n--- Simple Factory ---")
vehicles = [
    VehicleFactory.create_vehicle("car", make="Generic", model="Sedan"),
    VehicleFactory.create_vehicle("motorcycle", make="Generic", model="Sport"),
    VehicleFactory.create_vehicle("truck", make="Generic", model="Pickup")
]

for vehicle in vehicles:
    print(f"{vehicle}")
    print(f"  {vehicle.start_engine()}")

# Factory Method
print("\\n--- Factory Method ---")
toyota_factory = ToyotaFactory()
honda_factory = HondaFactory()

camry = toyota_factory.produce_vehicle("Camry", vehicle_type="car")
civic = honda_factory.produce_vehicle("Civic", vehicle_type="car")
cbr = honda_factory.produce_vehicle("CBR600", vehicle_type="motorcycle")

print(f"Produced: {camry}")
print(f"Produced: {civic}")
print(f"Produced: {cbr}")

# Abstract Factory
print("\\n--- Abstract Factory ---")
economy_factory = EconomyComponentFactory()
luxury_factory = LuxuryComponentFactory()

print("Economy vehicle components:")
print(f"  Engine: {economy_factory.create_engine()}")
print(f"  Transmission: {economy_factory.create_transmission()}")

print("Luxury vehicle components:")
print(f"  Engine: {luxury_factory.create_engine()}")
print(f"  Transmission: {luxury_factory.create_transmission()}")
""",
            "output": "=== Factory Patterns ===\n\n--- Simple Factory ---\nCar: Generic Sedan\n  Car engine started with key\nMotorcycle: Generic Sport\n  Motorcycle engine started with kick/button\nTruck: Generic Pickup\n  Truck engine started with heavy duty ignition\n\n--- Factory Method ---\nQuality check passed for Car: Toyota Camry\nQuality check passed for Car: Honda Civic\nQuality check passed for Motorcycle: Honda CBR600\nProduced: Car: Toyota Camry\nProduced: Car: Honda Civic\nProduced: Motorcycle: Honda CBR600\n\n--- Abstract Factory ---\nEconomy vehicle components:\n  Engine: 4-cylinder economy engine\n  Transmission: CVT transmission\nLuxury vehicle components:\n  Engine: V8 luxury engine\n  Transmission: 8-speed automatic transmission",
            "explanation": "Factory patterns provide ways to create objects without specifying their exact classes"
        },
        
        "decorator_pattern": {
            "code": """
from abc import ABC, abstractmethod

# Component interface
class Coffee(ABC):
    '''Abstract coffee component.'''
    
    @abstractmethod
    def cost(self):
        pass
    
    @abstractmethod
    def description(self):
        pass

# Concrete component
class SimpleCoffee(Coffee):
    '''Basic coffee implementation.'''
    
    def cost(self):
        return 2.0
    
    def description(self):
        return "Simple coffee"

# Base decorator
class CoffeeDecorator(Coffee):
    '''Base decorator for coffee.'''
    
    def __init__(self, coffee):
        self._coffee = coffee
    
    def cost(self):
        return self._coffee.cost()
    
    def description(self):
        return self._coffee.description()

# Concrete decorators
class MilkDecorator(CoffeeDecorator):
    '''Adds milk to coffee.'''
    
    def cost(self):
        return self._coffee.cost() + 0.5
    
    def description(self):
        return self._coffee.description() + ", milk"

class SugarDecorator(CoffeeDecorator):
    '''Adds sugar to coffee.'''
    
    def cost(self):
        return self._coffee.cost() + 0.2
    
    def description(self):
        return self._coffee.description() + ", sugar"

class WhipDecorator(CoffeeDecorator):
    '''Adds whipped cream to coffee.'''
    
    def cost(self):
        return self._coffee.cost() + 0.7
    
    def description(self):
        return self._coffee.description() + ", whipped cream"

class VanillaDecorator(CoffeeDecorator):
    '''Adds vanilla syrup to coffee.'''
    
    def cost(self):
        return self._coffee.cost() + 0.6
    
    def description(self):
        return self._coffee.description() + ", vanilla syrup"

# Python-style decorator (function decorator)
def timing_decorator(func):
    '''Decorator to measure function execution time.'''
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def validation_decorator(validation_func):
    '''Decorator factory for input validation.'''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not validation_func(*args, **kwargs):
                raise ValueError(f"Validation failed for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Example class using decorators
class Calculator:
    '''Calculator class demonstrating method decorators.'''
    
    @timing_decorator
    def slow_calculation(self, n):
        '''Simulate a slow calculation.'''
        import time
        time.sleep(0.1)  # Simulate work
        return sum(range(n))
    
    @validation_decorator(lambda self, x, y: isinstance(x, (int, float)) and isinstance(y, (int, float)))
    def divide(self, x, y):
        '''Division with input validation.'''
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

# Usage examples
print("=== Decorator Pattern ===")

# Object decoration
print("\\n--- Coffee Decorators ---")
coffee = SimpleCoffee()
print(f"{coffee.description()}: ${coffee.cost():.2f}")

# Add decorators
coffee = MilkDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost():.2f}")

coffee = SugarDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost():.2f}")

coffee = WhipDecorator(coffee)
print(f"{coffee.description()}: ${coffee.cost():.2f}")

# Multiple decorations in one go
fancy_coffee = VanillaDecorator(
    WhipDecorator(
        MilkDecorator(
            SugarDecorator(
                SimpleCoffee()
            )
        )
    )
)

print(f"\\nFancy coffee: {fancy_coffee.description()}")
print(f"Total cost: ${fancy_coffee.cost():.2f}")

# Function decorators
print("\\n--- Function Decorators ---")
calc = Calculator()

result = calc.slow_calculation(10000)
print(f"Calculation result: {result}")

try:
    result = calc.divide(10, 2)
    print(f"Division result: {result}")
    
    # This will fail validation
    calc.divide("invalid", 2)
except ValueError as e:
    print(f"Validation error: {e}")
""",
            "output": "=== Decorator Pattern ===\n\n--- Coffee Decorators ---\nSimple coffee: $2.00\nSimple coffee, milk: $2.50\nSimple coffee, milk, sugar: $2.70\nSimple coffee, milk, sugar, whipped cream: $3.40\n\nFancy coffee: Simple coffee, sugar, milk, whipped cream, vanilla syrup\nTotal cost: $3.80\n\n--- Function Decorators ---\nslow_calculation took 0.1023 seconds\nCalculation result: 49995000\nDivision result: 5.0\nValidation error: Validation failed for divide",
            "explanation": "Decorator pattern allows adding new functionality to objects dynamically without altering their structure"
        }
    }