"""
LinkedList implementation exercise for the Data Structures module.
"""

from typing import Dict, Any


class LinkedListExercise:
    """LinkedList implementation exercise."""
    
    @staticmethod
    def get_exercise() -> Dict[str, Any]:
        """Get the LinkedList implementation exercise."""
        return {
            "title": "Doubly Linked List Implementation",
            "instructions": """
Implement a complete doubly linked list with comprehensive functionality.
This exercise will test your understanding of pointer-based data structures,
memory management, and algorithm implementation.
""",
            "objectives": [
                "Understand pointer-based data structures",
                "Implement node-based memory management",
                "Create efficient insertion and deletion algorithms",
                "Handle edge cases and boundary conditions",
                "Provide comprehensive testing and validation"
            ],
            "tasks": [
                {
                    "step": 1,
                    "title": "Create Node Class",
                    "description": "Implement DoublyLinkedListNode with proper structure",
                    "requirements": [
                        "Store data, next, and previous pointers",
                        "Implement __str__ method for debugging",
                        "Handle None values appropriately",
                        "Provide clear initialization"
                    ]
                },
                {
                    "step": 2,
                    "title": "Implement Basic Operations",
                    "description": "Create fundamental list operations",
                    "requirements": [
                        "append(data) - add to end",
                        "prepend(data) - add to beginning", 
                        "insert_at(index, data) - insert at position",
                        "delete(data) - remove first occurrence",
                        "find(data) - locate element"
                    ]
                },
                {
                    "step": 3,
                    "title": "Advanced Operations",
                    "description": "Implement sophisticated list manipulation",
                    "requirements": [
                        "reverse() - reverse the entire list",
                        "get_middle() - find middle element efficiently",
                        "remove_duplicates() - eliminate duplicate values",
                        "merge() - combine with another sorted list"
                    ]
                },
                {
                    "step": 4,
                    "title": "Iterator and Magic Methods",
                    "description": "Make the list Pythonic and usable",
                    "requirements": [
                        "__len__ - return size",
                        "__str__ - string representation",
                        "__iter__ - make iterable",
                        "__getitem__ - support indexing",
                        "__contains__ - support 'in' operator"
                    ]
                },
                {
                    "step": 5,
                    "title": "Error Handling and Testing",
                    "description": "Robust error handling and comprehensive tests",
                    "requirements": [
                        "Handle empty list operations",
                        "Validate index bounds",
                        "Provide meaningful error messages",
                        "Create comprehensive test suite"
                    ]
                }
            ],
            "starter_code": '''
class DoublyLinkedListNode:
    """Node for doubly linked list."""
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
    
    def __str__(self):
        return str(self.data)

class DoublyLinkedList:
    """Doubly linked list implementation."""
    
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def append(self, data):
        """Add element to the end of the list."""
        # TODO: Implement append operation
        pass
    
    def prepend(self, data):
        """Add element to the beginning of the list."""
        # TODO: Implement prepend operation
        pass
    
    def insert_at(self, index, data):
        """Insert element at specific index."""
        # TODO: Implement insertion at index
        pass
    
    def delete(self, data):
        """Delete first occurrence of data."""
        # TODO: Implement deletion
        pass
    
    def find(self, data):
        """Find element and return its index."""
        # TODO: Implement search
        pass
    
    def reverse(self):
        """Reverse the list in place."""
        # TODO: Implement reversal
        pass
    
    def get_middle(self):
        """Get middle element using two-pointer technique."""
        # TODO: Implement middle element finder
        pass
    
    def __len__(self):
        # TODO: Return size
        pass
    
    def __str__(self):
        # TODO: Return string representation
        pass
    
    def __iter__(self):
        # TODO: Make iterable
        pass

# Test your implementation
if __name__ == "__main__":
    dll = DoublyLinkedList()
    
    # Test basic operations
    for i in [1, 2, 3, 4, 5]:
        dll.append(i)
    
    print(f"List: {dll}")
    print(f"Length: {len(dll)}")
    print(f"Middle: {dll.get_middle()}")
    
    # Test more operations...
''',
            "hints": [
                "Keep track of both head and tail pointers for efficiency",
                "Update both next and prev pointers when modifying nodes",
                "Handle empty list and single-element cases carefully",
                "Use two-pointer technique for finding middle element",
                "Remember to update size counter for all operations"
            ],
            "solution": '''
class DoublyLinkedListNode:
    """Node for doubly linked list."""
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None
    
    def __str__(self):
        return str(self.data)

class DoublyLinkedList:
    """Complete doubly linked list implementation."""
    
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
    
    def append(self, data):
        """Add element to the end of the list."""
        new_node = DoublyLinkedListNode(data)
        
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        
        self.size += 1
    
    def prepend(self, data):
        """Add element to the beginning of the list."""
        new_node = DoublyLinkedListNode(data)
        
        if not self.head:
            self.head = self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        
        self.size += 1
    
    def insert_at(self, index, data):
        """Insert element at specific index."""
        if index < 0 or index > self.size:
            raise IndexError("Index out of range")
        
        if index == 0:
            self.prepend(data)
        elif index == self.size:
            self.append(data)
        else:
            new_node = DoublyLinkedListNode(data)
            current = self._get_node_at_index(index)
            
            new_node.next = current
            new_node.prev = current.prev
            current.prev.next = new_node
            current.prev = new_node
            
            self.size += 1
    
    def delete(self, data):
        """Delete first occurrence of data."""
        current = self.head
        
        while current:
            if current.data == data:
                self._remove_node(current)
                return True
            current = current.next
        
        return False
    
    def _remove_node(self, node):
        """Helper method to remove a specific node."""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        
        self.size -= 1
    
    def _get_node_at_index(self, index):
        """Helper method to get node at specific index."""
        if index < 0 or index >= self.size:
            raise IndexError("Index out of range")
        
        # Optimize by starting from head or tail
        if index < self.size // 2:
            current = self.head
            for _ in range(index):
                current = current.next
        else:
            current = self.tail
            for _ in range(self.size - 1 - index):
                current = current.prev
        
        return current
    
    def find(self, data):
        """Find element and return its index."""
        current = self.head
        index = 0
        
        while current:
            if current.data == data:
                return index
            current = current.next
            index += 1
        
        return -1
    
    def reverse(self):
        """Reverse the list in place."""
        current = self.head
        self.head, self.tail = self.tail, self.head
        
        while current:
            current.next, current.prev = current.prev, current.next
            current = current.prev  # Move to next node (was previous)
    
    def get_middle(self):
        """Get middle element using two-pointer technique."""
        if not self.head:
            return None
        
        slow = fast = self.head
        
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        
        return slow.data
    
    def remove_duplicates(self):
        """Remove duplicate values from the list."""
        if not self.head:
            return
        
        seen = set()
        current = self.head
        
        while current:
            if current.data in seen:
                next_node = current.next
                self._remove_node(current)
                current = next_node
            else:
                seen.add(current.data)
                current = current.next
    
    def merge(self, other_list):
        """Merge with another sorted doubly linked list."""
        if not isinstance(other_list, DoublyLinkedList):
            raise TypeError("Can only merge with another DoublyLinkedList")
        
        # Create new list for merged result
        merged = DoublyLinkedList()
        current1, current2 = self.head, other_list.head
        
        while current1 and current2:
            if current1.data <= current2.data:
                merged.append(current1.data)
                current1 = current1.next
            else:
                merged.append(current2.data)
                current2 = current2.next
        
        # Add remaining elements
        while current1:
            merged.append(current1.data)
            current1 = current1.next
        
        while current2:
            merged.append(current2.data)
            current2 = current2.next
        
        return merged
    
    def __len__(self):
        """Return the size of the list."""
        return self.size
    
    def __str__(self):
        """Return string representation."""
        if not self.head:
            return "DoublyLinkedList([])"
        
        elements = []
        current = self.head
        while current:
            elements.append(str(current.data))
            current = current.next
        
        return f"DoublyLinkedList([{' <-> '.join(elements)}])"
    
    def __iter__(self):
        """Make the list iterable."""
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def __getitem__(self, index):
        """Support indexing."""
        node = self._get_node_at_index(index)
        return node.data
    
    def __contains__(self, data):
        """Support 'in' operator."""
        return self.find(data) != -1

# Test function
def test_doubly_linked_list():
    """Test the doubly linked list implementation."""
    dll = DoublyLinkedList()
    
    # Test append
    for i in range(1, 6):
        dll.append(i)
    assert list(dll) == [1, 2, 3, 4, 5]
    
    # Test prepend
    dll.prepend(0)
    assert list(dll) == [0, 1, 2, 3, 4, 5]
    
    # Test find
    assert dll.find(3) == 3
    assert dll.find(10) == -1
    
    # Test delete
    assert dll.delete(3) == True
    assert list(dll) == [0, 1, 2, 4, 5]
    
    print("All LinkedList tests passed!")

if __name__ == "__main__":
    test_doubly_linked_list()
'''
        }


def get_exercise():
    """Get the LinkedList exercise."""
    return LinkedListExercise.get_exercise()