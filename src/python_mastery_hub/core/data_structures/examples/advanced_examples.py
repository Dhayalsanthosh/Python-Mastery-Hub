"""
Advanced collections examples for the Data Structures module.
Covers collections module specialized containers.
"""

from typing import Dict, Any


class AdvancedExamples:
    """Advanced collections examples and demonstrations."""
    
    @staticmethod
    def get_collections_module() -> Dict[str, Any]:
        """Get comprehensive collections module examples."""
        return {
            "code": '''
from collections import defaultdict, Counter, deque, namedtuple, OrderedDict
from collections import ChainMap

def demonstrate_defaultdict():
    """Demonstrate defaultdict usage patterns."""
    print("=== defaultdict Examples ===")
    
    # Group words by length
    dd = defaultdict(list)
    words = ['apple', 'banana', 'cherry', 'date', 'elderberry']
    
    for word in words:
        dd[len(word)].append(word)
    
    print("Words grouped by length:")
    for length, word_list in dd.items():
        print(f"  {length} letters: {word_list}")
    
    # Count character frequencies
    char_count = defaultdict(int)
    text = "hello world"
    
    for char in text:
        if char.isalpha():
            char_count[char] += 1
    
    print(f"Character frequencies: {dict(char_count)}")
    
    # Nested defaultdict for 2D structure
    nested_dd = defaultdict(lambda: defaultdict(int))
    
    # Simulate user activity tracking
    activities = [
        ('alice', 'login', 5),
        ('bob', 'login', 3),
        ('alice', 'logout', 2),
        ('charlie', 'login', 1)
    ]
    
    for user, activity, count in activities:
        nested_dd[user][activity] += count
    
    print("User activity tracking:")
    for user, actions in nested_dd.items():
        print(f"  {user}: {dict(actions)}")

def demonstrate_counter():
    """Demonstrate Counter usage patterns."""
    print("\\n=== Counter Examples ===")
    
    # Word frequency analysis
    text = "the quick brown fox jumps over the lazy dog the fox is quick"
    word_counter = Counter(text.split())
    
    print(f"Word frequencies: {word_counter}")
    print(f"Most common words: {word_counter.most_common(3)}")
    print(f"Least common words: {word_counter.most_common()[:-3-1:-1]}")
    
    # Character frequency analysis
    char_counter = Counter(text.replace(' ', ''))
    print(f"Character frequencies: {char_counter}")
    
    # Counter arithmetic
    counter1 = Counter(['a', 'b', 'c', 'a', 'b'])
    counter2 = Counter(['a', 'b', 'b', 'd'])
    
    print(f"Counter 1: {counter1}")
    print(f"Counter 2: {counter2}")
    print(f"Addition: {counter1 + counter2}")
    print(f"Subtraction: {counter1 - counter2}")
    print(f"Intersection: {counter1 & counter2}")
    print(f"Union: {counter1 | counter2}")
    
    # Finding missing elements
    expected = Counter(['a', 'b', 'c', 'd', 'e'])
    actual = Counter(['a', 'b', 'c'])
    missing = expected - actual
    print(f"Missing elements: {list(missing.elements())}")

def demonstrate_deque():
    """Demonstrate deque usage patterns."""
    print("\\n=== deque Examples ===")
    
    # Basic deque operations
    dq = deque([1, 2, 3, 4, 5])
    print(f"Original deque: {dq}")
    
    # Operations at both ends
    dq.appendleft(0)
    dq.append(6)
    print(f"After appends: {dq}")
    
    left_item = dq.popleft()
    right_item = dq.pop()
    print(f"Removed {left_item} (left) and {right_item} (right): {dq}")
    
    # Rotation
    dq.rotate(2)
    print(f"After rotate(2): {dq}")
    dq.rotate(-3)
    print(f"After rotate(-3): {dq}")
    
    # Limited size deque (circular buffer)
    circular = deque(maxlen=5)
    for i in range(8):
        circular.append(i)
        print(f"Added {i}: {circular}")
    
    # Sliding window example
    def sliding_window_avg(data, window_size):
        window = deque(maxlen=window_size)
        averages = []
        
        for value in data:
            window.append(value)
            if len(window) == window_size:
                averages.append(sum(window) / window_size)
        
        return averages
    
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    moving_avg = sliding_window_avg(data, 3)
    print(f"3-period moving average: {moving_avg}")

def demonstrate_namedtuple():
    """Demonstrate namedtuple usage patterns."""
    print("\\n=== namedtuple Examples ===")
    
    # Define namedtuple types
    Point = namedtuple('Point', ['x', 'y'])
    Student = namedtuple('Student', ['name', 'age', 'grade', 'gpa'])
    
    # Create instances
    p1 = Point(3, 4)
    p2 = Point(0, 0)
    
    student1 = Student('Alice', 20, 'A', 3.8)
    student2 = Student('Bob', 21, 'B+', 3.5)
    
    print(f"Points: {p1}, {p2}")
    print(f"Students: {student1}, {student2}")
    
    # Access fields
    print(f"Point p1 coordinates: x={p1.x}, y={p1.y}")
    print(f"Student 1 GPA: {student1.gpa}")
    
    # namedtuple methods
    print(f"Point fields: {p1._fields}")
    print(f"Student as dict: {student1._asdict()}")
    
    # Creating new instances with modifications
    student1_updated = student1._replace(gpa=4.0)
    print(f"Student 1 updated: {student1_updated}")
    
    # Using namedtuples in calculations
    def distance(point1, point2):
        return ((point1.x - point2.x)**2 + (point1.y - point2.y)**2)**0.5
    
    dist = distance(p1, p2)
    print(f"Distance between {p1} and {p2}: {dist:.2f}")
    
    # namedtuple with defaults (Python 3.7+)
    Employee = namedtuple('Employee', ['name', 'department', 'salary'], defaults=['Unknown', 50000])
    emp1 = Employee('John')
    emp2 = Employee('Jane', 'Engineering')
    print(f"Employees: {emp1}, {emp2}")

def demonstrate_ordereddict():
    """Demonstrate OrderedDict usage patterns."""
    print("\\n=== OrderedDict Examples ===")
    
    # Basic OrderedDict
    od = OrderedDict()
    od['third'] = 3
    od['first'] = 1
    od['second'] = 2
    
    print(f"OrderedDict: {od}")
    print(f"Keys in insertion order: {list(od.keys())}")
    
    # Moving items
    od.move_to_end('first')
    print(f"After move_to_end('first'): {od}")
    
    od.move_to_end('second', last=False)
    print(f"After move_to_end('second', last=False): {od}")
    
    # LRU Cache simulation
    class LRUCache:
        def __init__(self, capacity):
            self.capacity = capacity
            self.cache = OrderedDict()
        
        def get(self, key):
            if key in self.cache:
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
        
        def put(self, key, value):
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    lru = LRUCache(3)
    lru.put('a', 1)
    lru.put('b', 2)
    lru.put('c', 3)
    print(f"LRU after adding a,b,c: {list(lru.cache.items())}")
    
    lru.get('a')  # Access 'a'
    lru.put('d', 4)  # Should evict 'b'
    print(f"LRU after accessing 'a' and adding 'd': {list(lru.cache.items())}")

def demonstrate_chainmap():
    """Demonstrate ChainMap usage patterns."""
    print("\\n=== ChainMap Examples ===")
    
    # Configuration management
    defaults = {'theme': 'light', 'language': 'en', 'debug': False}
    user_config = {'theme': 'dark', 'debug': True}
    cli_args = {'debug': False, 'verbose': True}
    
    # Priority: cli_args > user_config > defaults
    config = ChainMap(cli_args, user_config, defaults)
    
    print(f"Combined config: {dict(config)}")
    print(f"Theme: {config['theme']}")  # From user_config
    print(f"Debug: {config['debug']}")  # From cli_args (highest priority)
    print(f"Language: {config['language']}")  # From defaults
    
    # Show the chain
    print(f"Configuration chain: {config.maps}")
    
    # Creating new child contexts
    temp_config = config.new_child({'temp_setting': 'value'})
    print(f"Temporary config: {dict(temp_config)}")
    
    # Environment variable simulation
    import os
    env_vars = {'PATH': '/usr/bin', 'HOME': '/home/user'}
    app_defaults = {'PATH': '/default/path', 'EDITOR': 'vim'}
    
    environment = ChainMap(env_vars, app_defaults)
    print(f"Environment PATH: {environment['PATH']}")
    print(f"Environment EDITOR: {environment['EDITOR']}")

# Run all demonstrations
if __name__ == "__main__":
    demonstrate_defaultdict()
    demonstrate_counter()
    demonstrate_deque()
    demonstrate_namedtuple()
    demonstrate_ordereddict()
    demonstrate_chainmap()
''',
            "explanation": "Advanced collections in the collections module provide specialized containers for specific use cases that extend Python's built-in types"
        }