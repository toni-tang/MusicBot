class Node:

    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:

    def __init__(self):
        self.front = self.rear = None
    
    def push(self, item):
        newNode = Node(item)

        if(self.front is None):
            self.front = self.rear = newNode
        else:
            self.rear.next = newNode
            self.rear = newNode

    def pop(self):
        if self.front is None:
            return
        else:
            self.front = self.front.next

    def peek(self):
        return self.front.data


