class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    # Initialize the tree with an empty root
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        if self.root is None:
            # If the tree is empty, create a new root node
            self.root = Node(key, value)
        else:
            # Call the recursive helper function to insert
            self._insert_recursively(self.root, key, value)

    def _insert_recursively(self, current, key, value):
        if key < current.key:
            # If the value is less than the current node's value, go left
            if current.left is None:
                current.left = Node(key, value)
            else:
                self._insert_recursively(current.left, key, value)
        elif key > current.key:
            # If the value is greater than the current node's value, go right
            if current.right is None:
                current.right = Node(key, value)
            else:
                self._insert_recursively(current.right, key, value)
        else:
            # Update the value if it already exists
            current.value = value
    
    def search(self, key):
        return self._search(self.root, key)
    
    def _search(self, current, key):
        if current is None:
            return None
        if current.key == key:
            return current.value
        elif key < current.key:
            return self._search(current.left, key)
        else:
            return self._search(current.right, key)