class Node:

    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:

    def __init__(self):
        self.front = self.rear = None
        self.size = 0
    
    def push(self, item):
        newNode = Node(item)

        if self.front is None:
            self.front = self.rear = newNode
            self.size = 1
        else:
            self.rear.next = newNode
            self.rear = newNode
            self.size += 1

    def pop(self):
        if self.front is None or self.size == 0:
            return
        else:
            temp = self.front
            self.front = self.front.next
            self.size -= 1
        return temp.data 

    def peek(self):
        return self.front.data