"""
Binary Search Tree implementation exercise for the Data Structures module.
"""

from typing import Dict, Any


class BSTExercise:
    """Binary Search Tree implementation exercise."""
    
    @staticmethod
    def get_exercise() -> Dict[str, Any]:
        """Get the BST implementation exercise."""
        return {
            "title": "Binary Search Tree Implementation",
            "instructions": """
Implement a comprehensive Binary Search Tree with insertion, deletion, traversals,
and advanced operations. This exercise tests your understanding of tree structures,
recursive algorithms, and balanced tree properties.
""",
            "objectives": [
                "Understand tree data structures and recursive algorithms",
                "Implement efficient search, insertion, and deletion operations",
                "Master different tree traversal methods",
                "Handle tree balancing and optimization",
                "Create comprehensive tree analysis tools"
            ],
            "tasks": [
                {
                    "step": 1,
                    "title": "Create TreeNode Class",
                    "description": "Implement basic tree node structure",
                    "requirements": [
                        "Store data, left, and right child references",
                        "Implement comparison methods for ordering",
                        "Provide clear string representation",
                        "Handle None values appropriately"
                    ]
                },
                {
                    "step": 2,
                    "title": "Basic Tree Operations",
                    "description": "Implement fundamental BST operations",
                    "requirements": [
                        "insert(data) - add element maintaining BST property",
                        "search(data) - find element in tree",
                        "delete(data) - remove element handling all cases",
                        "find_min() and find_max() - locate extreme values"
                    ]
                },
                {
                    "step": 3,
                    "title": "Tree Traversals",
                    "description": "Implement all standard traversal methods",
                    "requirements": [
                        "inorder_traversal() - left, root, right",
                        "preorder_traversal() - root, left, right",
                        "postorder_traversal() - left, right, root",
                        "level_order_traversal() - breadth-first"
                    ]
                },
                {
                    "step": 4,
                    "title": "Tree Analysis",
                    "description": "Implement tree measurement and analysis",
                    "requirements": [
                        "height() - calculate tree height",
                        "size() - count total nodes",
                        "is_balanced() - check balance property",
                        "validate_bst() - verify BST property"
                    ]
                },
                {
                    "step": 5,
                    "title": "Advanced Operations",
                    "description": "Implement sophisticated tree operations",
                    "requirements": [
                        "find_lca() - lowest common ancestor",
                        "path_to_node() - find path from root to node",
                        "serialize() and deserialize() - tree persistence",
                        "create_balanced_bst() - build balanced tree from sorted array"
                    ]
                }
            ],
            "starter_code": '''
class TreeNode:
    """Node for binary search tree."""
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
    
    def __str__(self):
        return str(self.data)

class BinarySearchTree:
    """Binary Search Tree implementation."""
    
    def __init__(self):
        self.root = None
    
    def insert(self, data):
        """Insert data into the BST."""
        # TODO: Implement insertion
        pass
    
    def search(self, data):
        """Search for data in the BST."""
        # TODO: Implement search
        pass
    
    def delete(self, data):
        """Delete data from the BST."""
        # TODO: Implement deletion (hardest part!)
        pass
    
    def inorder_traversal(self):
        """Return inorder traversal of the tree."""
        # TODO: Implement inorder traversal
        pass
    
    def height(self):
        """Calculate height of the tree."""
        # TODO: Implement height calculation
        pass
    
    def is_balanced(self):
        """Check if tree is balanced."""
        # TODO: Implement balance checking
        pass

# Test your implementation
if __name__ == "__main__":
    bst = BinarySearchTree()
    values = [50, 30, 20, 40, 70, 60, 80]
    
    for val in values:
        bst.insert(val)
    
    print(f"Inorder: {bst.inorder_traversal()}")
    print(f"Height: {bst.height()}")
    print(f"Balanced: {bst.is_balanced()}")
''',
            "hints": [
                "Use recursive approaches for most tree operations",
                "Handle three cases for deletion: no children, one child, two children",
                "For deletion with two children, replace with inorder successor",
                "Use helper methods to separate public interface from implementation",
                "Consider using a queue for level-order traversal"
            ],
            "solution": '''
from collections import deque

class TreeNode:
    """Node for binary search tree."""
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
    
    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return f"TreeNode({self.data})"

class BinarySearchTree:
    """Comprehensive Binary Search Tree implementation."""
    
    def __init__(self, values=None):
        self.root = None
        if values:
            for value in values:
                self.insert(value)
    
    def insert(self, data):
        """Insert data into the BST."""
        self.root = self._insert_recursive(self.root, data)
    
    def _insert_recursive(self, node, data):
        """Helper method for recursive insertion."""
        if node is None:
            return TreeNode(data)
        
        if data < node.data:
            node.left = self._insert_recursive(node.left, data)
        elif data > node.data:
            node.right = self._insert_recursive(node.right, data)
        # Ignore duplicates
        
        return node
    
    def search(self, data):
        """Search for data in the BST."""
        return self._search_recursive(self.root, data)
    
    def _search_recursive(self, node, data):
        """Helper method for recursive search."""
        if node is None or node.data == data:
            return node
        
        if data < node.data:
            return self._search_recursive(node.left, data)
        return self._search_recursive(node.right, data)
    
    def delete(self, data):
        """Delete data from the BST."""
        self.root = self._delete_recursive(self.root, data)
    
    def _delete_recursive(self, node, data):
        """Helper method for recursive deletion."""
        if node is None:
            return node
        
        if data < node.data:
            node.left = self._delete_recursive(node.left, data)
        elif data > node.data:
            node.right = self._delete_recursive(node.right, data)
        else:
            # Node to be deleted found
            
            # Case 1: No children (leaf node)
            if node.left is None and node.right is None:
                return None
            
            # Case 2: One child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            
            # Case 3: Two children
            # Find inorder successor (smallest in right subtree)
            successor = self._find_min_node(node.right)
            node.data = successor.data
            node.right = self._delete_recursive(node.right, successor.data)
        
        return node
    
    def _find_min_node(self, node):
        """Find node with minimum value in subtree."""
        while node.left:
            node = node.left
        return node
    
    def find_min(self):
        """Find minimum value in the tree."""
        if self.root is None:
            return None
        return self._find_min_node(self.root).data
    
    def find_max(self):
        """Find maximum value in the tree."""
        if self.root is None:
            return None
        
        node = self.root
        while node.right:
            node = node.right
        return node.data
    
    def inorder_traversal(self):
        """Return inorder traversal (sorted order)."""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node, result):
        """Helper for inorder traversal."""
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.data)
            self._inorder_recursive(node.right, result)
    
    def preorder_traversal(self):
        """Return preorder traversal."""
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node, result):
        """Helper for preorder traversal."""
        if node:
            result.append(node.data)
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)
    
    def postorder_traversal(self):
        """Return postorder traversal."""
        result = []
        self._postorder_recursive(self.root, result)
        return result
    
    def _postorder_recursive(self, node, result):
        """Helper for postorder traversal."""
        if node:
            self._postorder_recursive(node.left, result)
            self._postorder_recursive(node.right, result)
            result.append(node.data)
    
    def level_order_traversal(self):
        """Return level order (breadth-first) traversal."""
        if not self.root:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            result.append(node.data)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        return result
    
    def height(self):
        """Calculate height of the tree."""
        return self._height_recursive(self.root)
    
    def _height_recursive(self, node):
        """Helper for height calculation."""
        if node is None:
            return -1
        
        left_height = self._height_recursive(node.left)
        right_height = self._height_recursive(node.right)
        
        return 1 + max(left_height, right_height)
    
    def size(self):
        """Count total number of nodes."""
        return self._size_recursive(self.root)
    
    def _size_recursive(self, node):
        """Helper for size calculation."""
        if node is None:
            return 0
        return 1 + self._size_recursive(node.left) + self._size_recursive(node.right)
    
    def is_balanced(self):
        """Check if tree is balanced (height difference <= 1)."""
        def check_balance(node):
            if node is None:
                return True, -1
            
            left_balanced, left_height = check_balance(node.left)
            if not left_balanced:
                return False, 0
            
            right_balanced, right_height = check_balance(node.right)
            if not right_balanced:
                return False, 0
            
            balanced = abs(left_height - right_height) <= 1
            height = 1 + max(left_height, right_height)
            
            return balanced, height
        
        is_balanced, _ = check_balance(self.root)
        return is_balanced
    
    def validate_bst(self):
        """Validate that tree maintains BST property."""
        def validate_recursive(node, min_val, max_val):
            if node is None:
                return True
            
            if node.data <= min_val or node.data >= max_val:
                return False
            
            return (validate_recursive(node.left, min_val, node.data) and
                   validate_recursive(node.right, node.data, max_val))
        
        return validate_recursive(self.root, float('-inf'), float('inf'))
    
    def find_lca(self, val1, val2):
        """Find lowest common ancestor of two values."""
        def lca_recursive(node, v1, v2):
            if node is None:
                return None
            
            # If both values are smaller, LCA is in left subtree
            if v1 < node.data and v2 < node.data:
                return lca_recursive(node.left, v1, v2)
            
            # If both values are larger, LCA is in right subtree
            if v1 > node.data and v2 > node.data:
                return lca_recursive(node.right, v1, v2)
            
            # Current node is the LCA
            return node
        
        lca_node = lca_recursive(self.root, val1, val2)
        return lca_node.data if lca_node else None
    
    def __str__(self):
        """String representation of the tree."""
        if not self.root:
            return "BinarySearchTree(empty)"
        
        return f"BinarySearchTree(inorder: {self.inorder_traversal()})"

# Test function
def test_binary_search_tree():
    """Test the BST implementation."""
    bst = BinarySearchTree()
    values = [50, 30, 20, 40, 70, 60, 80]
    
    for val in values:
        bst.insert(val)
    
    # Test search
    assert bst.search(50) is not None
    assert bst.search(100) is None
    
    # Test traversals
    assert bst.inorder_traversal() == [20, 30, 40, 50, 60, 70, 80]
    assert bst.preorder_traversal() == [50, 30, 20, 40, 70, 60, 80]
    
    # Test tree properties
    assert bst.height() == 2
    assert bst.size() == 7
    assert bst.find_min() == 20
    assert bst.find_max() == 80
    
    # Test validation
    assert bst.validate_bst() == True
    
    # Test LCA
    assert bst.find_lca(20, 40) == 30
    assert bst.find_lca(60, 80) == 70
    
    print("All BST tests passed!")

if __name__ == "__main__":
    test_binary_search_tree()
'''
        }


def get_exercise():
    """Get the BST exercise."""
    return BSTExercise.get_exercise()