"""
Custom data structures examples for the Data Structures module.
Covers linked lists, stacks, queues, and other fundamental structures.
"""

from typing import Dict, Any


class CustomExamples:
    """Custom data structures examples and demonstrations."""
    
    @staticmethod
    def get_linked_list_implementation() -> Dict[str, Any]:
        """Get linked list implementation examples."""
        return {
            "code": '''
class ListNode:
    """Node for singly linked list."""
    def __init__(self, data):
        self.data = data
        self.next = None
    
    def __str__(self):
        return str(self.data)

class LinkedList:
    """Simple singly linked list implementation."""
    
    def __init__(self):
        self.head = None
        self.size = 0
    
    def append(self, data):
        """Add element to the end of the list."""
        new_node = ListNode(data)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.size += 1
    
    def prepend(self, data):
        """Add element to the beginning of the list."""
        new_node = ListNode(data)
        new_node.next = self.head
        self.head = new_node
        self.size += 1
    
    def insert_at(self, index, data):
        """Insert element at specific index."""
        if index < 0 or index > self.size:
            raise IndexError("Index out of range")
        
        if index == 0:
            self.prepend(data)
            return
        
        new_node = ListNode(data)
        current = self.head
        for _ in range(index - 1):
            current = current.next
        
        new_node.next = current.next
        current.next = new_node
        self.size += 1
    
    def delete(self, data):
        """Delete first occurrence of data."""
        if not self.head:
            return False
        
        if self.head.data == data:
            self.head = self.head.next
            self.size -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                self.size -= 1
                return True
            current = current.next
        return False
    
    def find(self, data):
        """Find element in the list."""
        current = self.head
        index = 0
        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1
        return -1
    
    def reverse(self):
        """Reverse the linked list in place."""
        prev = None
        current = self.head
        
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        
        self.head = prev
    
    def get_middle(self):
        """Get middle element using two-pointer technique."""
        if not self.head:
            return None
        
        slow = fast = self.head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        
        return slow.data
    
    def detect_cycle(self):
        """Detect if there's a cycle in the list."""
        if not self.head:
            return False
        
        slow = fast = self.head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                return True
        
        return False
    
    def __len__(self):
        return self.size
    
    def __str__(self):
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        return ' -> '.join(elements) + ' -> None'
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def to_list(self):
        """Convert to Python list."""
        return list(self)

def demonstrate_linked_list():
    """Demonstrate linked list operations."""
    print("=== Linked List Demonstration ===")
    
    ll = LinkedList()
    print(f"Created empty list: {ll}")
    
    # Add elements
    for i in [1, 2, 3, 4, 5]:
        ll.append(i)
    print(f"After appending 1-5: {ll}")
    
    ll.prepend(0)
    print(f"After prepending 0: {ll}")
    
    ll.insert_at(3, 2.5)
    print(f"After inserting 2.5 at index 3: {ll}")
    
    # Search operations
    print(f"Find 3: index {ll.find(3)}")
    print(f"Find 10: index {ll.find(10)}")
    print(f"Middle element: {ll.get_middle()}")
    
    # Modify list
    ll.delete(2.5)
    print(f"After deleting 2.5: {ll}")
    
    # Reverse
    ll.reverse()
    print(f"After reversing: {ll}")
    
    # Convert to list
    print(f"As Python list: {ll.to_list()}")
    print(f"Length: {len(ll)}")
    
    # Iteration
    print(f"Iterate: {[x for x in ll]}")

if __name__ == "__main__":
    demonstrate_linked_list()
''',
            "explanation": "Custom linked list implementation demonstrates fundamental pointer-based data structure concepts and memory management"
        }
    
    @staticmethod
    def get_stack_and_queue() -> Dict[str, Any]:
        """Get stack and queue implementation examples."""
        return {
            "code": '''
class Stack:
    """Stack implementation using list."""
    
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """Add item to top of stack."""
        self.items.append(item)
    
    def pop(self):
        """Remove and return top item."""
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.pop()
    
    def peek(self):
        """Return top item without removing."""
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items[-1]
    
    def is_empty(self):
        """Check if stack is empty."""
        return len(self.items) == 0
    
    def size(self):
        """Return stack size."""
        return len(self.items)
    
    def __str__(self):
        return f"Stack({self.items})"

class Queue:
    """Queue implementation using deque for efficiency."""
    
    def __init__(self):
        from collections import deque
        self.items = deque()
    
    def enqueue(self, item):
        """Add item to rear of queue."""
        self.items.append(item)
    
    def dequeue(self):
        """Remove and return front item."""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items.popleft()
    
    def front(self):
        """Return front item without removing."""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items[0]
    
    def rear(self):
        """Return rear item without removing."""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items[-1]
    
    def is_empty(self):
        """Check if queue is empty."""
        return len(self.items) == 0
    
    def size(self):
        """Return queue size."""
        return len(self.items)
    
    def __str__(self):
        return f"Queue({list(self.items)})"

class CircularQueue:
    """Circular queue implementation with fixed capacity."""
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = [None] * capacity
        self.front = 0
        self.rear = -1
        self.count = 0
    
    def enqueue(self, item):
        """Add item to queue."""
        if self.is_full():
            raise OverflowError("Queue is full")
        
        self.rear = (self.rear + 1) % self.capacity
        self.items[self.rear] = item
        self.count += 1
    
    def dequeue(self):
        """Remove and return front item."""
        if self.is_empty():
            raise IndexError("Queue is empty")
        
        item = self.items[self.front]
        self.items[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item
    
    def is_empty(self):
        return self.count == 0
    
    def is_full(self):
        return self.count == self.capacity
    
    def size(self):
        return self.count
    
    def __str__(self):
        if self.is_empty():
            return "CircularQueue([])"
        
        result = []
        current = self.front
        for _ in range(self.count):
            result.append(self.items[current])
            current = (current + 1) % self.capacity
        
        return f"CircularQueue({result})"

def is_balanced_parentheses(expression):
    """Check if parentheses are balanced using stack."""
    stack = Stack()
    pairs = {'(': ')', '[': ']', '{': '}'}
    
    for char in expression:
        if char in pairs:  # Opening bracket
            stack.push(char)
        elif char in pairs.values():  # Closing bracket
            if stack.is_empty():
                return False
            if pairs[stack.pop()] != char:
                return False
    
    return stack.is_empty()

def evaluate_postfix(expression):
    """Evaluate postfix expression using stack."""
    stack = Stack()
    operators = {'+', '-', '*', '/', '**'}
    
    for token in expression.split():
        if token in operators:
            if stack.size() < 2:
                raise ValueError("Invalid postfix expression")
            
            b = stack.pop()
            a = stack.pop()
            
            if token == '+':
                result = a + b
            elif token == '-':
                result = a - b
            elif token == '*':
                result = a * b
            elif token == '/':
                result = a / b
            elif token == '**':
                result = a ** b
            
            stack.push(result)
        else:
            try:
                stack.push(float(token))
            except ValueError:
                raise ValueError(f"Invalid token: {token}")
    
    if stack.size() != 1:
        raise ValueError("Invalid postfix expression")
    
    return stack.pop()

def simulate_task_queue():
    """Simulate task processing with priority queue."""
    import heapq
    
    # Priority queue using heapq (min-heap)
    task_queue = []
    task_id = 0
    
    def add_task(priority, description):
        nonlocal task_id
        task_id += 1
        heapq.heappush(task_queue, (priority, task_id, description))
        return task_id
    
    def get_next_task():
        if task_queue:
            priority, tid, description = heapq.heappop(task_queue)
            return {'id': tid, 'priority': priority, 'description': description}
        return None
    
    # Add tasks with different priorities
    tasks = [
        (3, "Low priority task"),
        (1, "High priority task"),
        (2, "Medium priority task"),
        (1, "Another high priority task"),
        (2, "Another medium task")
    ]
    
    print("=== Task Queue Simulation ===")
    
    for priority, desc in tasks:
        tid = add_task(priority, desc)
        print(f"Added task {tid}: {desc} (priority {priority})")
    
    print("\\nProcessing tasks in priority order:")
    while task_queue:
        task = get_next_task()
        print(f"  Processing task {task['id']}: {task['description']} (priority {task['priority']})")

def demonstrate_stacks_and_queues():
    """Demonstrate stack and queue operations."""
    print("=== Stack Demonstration ===")
    stack = Stack()
    
    # Push elements
    for item in [1, 2, 3, 4, 5]:
        stack.push(item)
        print(f"Pushed {item}: {stack}")
    
    # Pop elements
    while not stack.is_empty():
        popped = stack.pop()
        print(f"Popped {popped}: {stack}")
    
    print("\\n=== Queue Demonstration ===")
    queue = Queue()
    
    # Enqueue elements
    for item in ['A', 'B', 'C', 'D']:
        queue.enqueue(item)
        print(f"Enqueued {item}: {queue}")
    
    # Dequeue elements
    while not queue.is_empty():
        dequeued = queue.dequeue()
        print(f"Dequeued {dequeued}: {queue}")
    
    print("\\n=== Circular Queue Demonstration ===")
    cq = CircularQueue(4)
    
    # Fill queue
    for item in [10, 20, 30, 40]:
        cq.enqueue(item)
        print(f"Enqueued {item}: {cq}")
    
    # Dequeue and enqueue to show circular behavior
    print(f"Dequeued: {cq.dequeue()}, Queue: {cq}")
    print(f"Dequeued: {cq.dequeue()}, Queue: {cq}")
    
    cq.enqueue(50)
    cq.enqueue(60)
    print(f"After adding 50, 60: {cq}")
    
    print("\\n=== Balanced Parentheses Check ===")
    expressions = [
        "((()))",
        "({[]})",
        "(()",
        "([)]",
        "{[()]}"
    ]
    
    for expr in expressions:
        result = is_balanced_parentheses(expr)
        print(f"'{expr}' is {'balanced' if result else 'not balanced'}")
    
    print("\\n=== Postfix Expression Evaluation ===")
    postfix_expressions = [
        "3 4 +",           # 3 + 4 = 7
        "3 4 + 2 *",       # (3 + 4) * 2 = 14
        "3 4 2 * +",       # 3 + (4 * 2) = 11
        "15 7 1 1 + - / 3 * 2 1 1 + + -"  # Complex expression
    ]
    
    for expr in postfix_expressions:
        try:
            result = evaluate_postfix(expr)
            print(f"'{expr}' = {result}")
        except Exception as e:
            print(f"'{expr}' -> Error: {e}")
    
    # Run task queue simulation
    simulate_task_queue()

if __name__ == "__main__":
    demonstrate_stacks_and_queues()
''',
            "explanation": "Stack (LIFO) and Queue (FIFO) are fundamental data structures with many practical applications in algorithm design and system programming"
        }