class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BinaryTree:
    # Initialize the tree with an empty root
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            # If the tree is empty, create a new root node
            self.root = Node(value)
        else:
            # Call the recursive helper function to insert
            self._insert_recursively(self.root, value)

    def _insert_recursively(self, current, value):
        if value < current.value:
            # If the value is less than the current node's value, go left
            if current.left is None:
                current.left = Node(value)
            else:
                self._insert_recursively(current.left, value)
        elif value > current.value:
            # If the value is greater than the current node's value, go right
            if current.right is None:
                current.right = Node(value)
            else:
                self._insert_recursively(current.right, value)
        else:
            pass

    def inorderTraversal(self, root):
      result = [] # An empty list to store the traversal results
      if root:
         result = self.inorderTraversal(root.left) # Recursively traverse the left subtree
         result.append(root.value)
         result += self.inorderTraversal(root.right) # Recursively traverse the right subtree
      return result

