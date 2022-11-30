import datetime
import sys
import logging
from typing import Dict, List
from queue import PriorityQueue

from doubly_linked_list import DoublyLinkedList, Node

logger = logging.getLogger(__name__)


class CachedDataItem:
    def __init__(self, data: str, expiration_time):
        self.data = data
        self.expiration_time = expiration_time


class DataStore:
    def __init__(self):
        self.services:List[str] = []
        self.services_cache_map:Dict[str, CachedDataItem] = {}
        self.services_cache_list:DoublyLinkedList = {}
        self.expiration_time_heap:Dict[str, PriorityQueue] = {}

        self.service_item_max_size = 1024 * 32
        self.per_service_memory_limit = self.service_item_max_size * 8

    
    def remove_expired_items(self,  service_domain):
        if service_domain not in self.expiration_time_heap:
            return
        
        expiration_time_heap = self.expiration_time_heap
        expiration_time_heap.acquire()

        now = datetime.datetime.utcnow()

        while not expiration_time_heap.empty() and expiration_time_heap.queue[0][0].expiration_time < now:
            item = expiration_time_heap.get() #dead lock ??? block=False
            self.services_cache_list[service_domain].remove(item)
        
        self.expiration_time_heap.release()

    


    def add(self, service_domain, path, expiration_time, data: str):
        if service_domain not in self.services:
            self.services.append(service_domain)
            self.services_cache_map[service_domain]: Dict[str, Node] = {}
            self.services_cache_list[service_domain] = DoublyLinkedList()
            self.expiration_time_heap[service_domain] = PriorityQueue()
            
        cached_item_node = self.services_cache_map[service_domain].get(path, None)

        if cached_item_node:
            cached_item_node.data.expiration_time = expiration_time
            self.services_cache_list[service_domain].move_to_end(cached_item_node)
            
            return
    
        new_data_size = sys.getsizeof(data)
        print("data size:", new_data_size, self.service_item_max_size)

        if new_data_size > self.service_item_max_size:
            raise Exception('Data exceeds max limit') 

        print("list...")
        print(f'domain: {service_domain}')
        service_data_list: DoublyLinkedList = self.services_cache_list[service_domain]

        print("while...")
        while not service_data_list.empty() and service_data_list.data_size + new_data_size > self.per_service_memory_limit:
            service_data_list.remove_start()

        print("cached")
        cached_data_item = CachedDataItem(data, expiration_time)
        node = service_data_list.add(cached_data_item)
        self.services_cache_map[service_domain][path] = node


    def get(self, service_domain, path):
        if service_domain not in self.services:
            return None

        cached_item_node = self.services_cache_map[service_domain].get(path, None)

        if not cached_item_node or cached_item_node.data.expiration_time < datetime.datetime.utcnow():
            return None

        return cached_item_node.data.data
        


__data_store = DataStore()

add = __data_store.add
get = __data_store.get

    


