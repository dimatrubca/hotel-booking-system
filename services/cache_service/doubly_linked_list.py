import logging
import sys

logger = logging.getLogger(__name__)

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.previous = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.data_size = 0


    def traverse(self, starting_point=None):
        if starting_point is None:
            starting_point = self.head

        node = starting_point

        while node is not None and (node.next != starting_point):
            yield node
            node = node.next
        
        yield node


    def add(self, data):
        node = Node(data)

        if self.head == None:
            self.head = self.tail = node
        else:
            node.previous = self.tail
            self.tail.next = node
            self.tail = node

        self.data_size += sys.getsizeof(data)

        return node
            
            
    def move_to_end(self, node: Node):
        if self.tail == node:
            return

        if self.head == node:
            self.head = node.next

        if node.previous:
            (node.previous).next = node.next

        if node.next:
            (node.next).previous = node.previous
            

        self.tail.next = node
        node.previous = self.tail
        node.next = None
        self.tail = node


    def remove(self, node):
        if self.head == node:
            self.head = node.next

        if self.tail == node:
            self.tail = node.previous

        if node.previous:
            (node.previous).next = node.next

        if node.next:
            (node.next).previous = node.previous

        del node

    def remove_start(self):
        if self.head == None:
            raise Exception("Empty list, cannot remove item")

        prev_head = self.head
        self.head = self.head.next
        self.head.previous = None
        
        del prev_head
        

    def print_list(self, starting_point=None):
        nodes = []

        for node in self.traverse(starting_point):
            nodes.append(str(node))

        print(' -> '.join(nodes))

    def empty(self):
        return self.head == None