from typing import Dict, List
from queue import PriorityQueue

import datetime
import sys
import logging
import uuid

import requests

from doubly_linked_list import DoublyLinkedList, Node
from schemas import Event

logger = logging.getLogger(__name__)


class CachedDataItem:
    def __init__(self, data: str, expiration_time):
        self.data = data
        self.expiration_time = expiration_time


class DataStore:
    def __init__(self):
        self.services:List[str] = []
        self.services_cache_map:Dict[str, Node] = {}
        self.services_cache_list:DoublyLinkedList = {}
        self.expiration_time_heap:Dict[str, PriorityQueue] = {}

        self.service_item_max_size = 1024 * 32
        self.per_service_memory_limit = self.service_item_max_size * 8

        self.replication_id = str(uuid.uuid1())
        self.secondary_id = str(uuid.uuid1())

        self.is_leader = False
        self.backlog = []
        self.offset = 0
        self.secondary_backlog = []
        self.secondary_offset = 0
        self.events_queue = {}

    
    def on_become_leader(self):
        self.is_leader = True
        self.secondary_id = self.replication_id
        self.replication_id = str(uuid.uuid1())
        self.secondary_offset = self.offset
        self.secondary_backlog = self.backlog #todo: copy? remove secondary?
        # self.offset = 0 # do not reset offset
        # keep backlog


    def on_leader_updated(self, leader_replication_id, leader_offset, leader_secondary_id, leader_secondary_offset):
        assert leader_offset >= leader_secondary_offset, 'offset mismatch'

        if self.replication_id == leader_secondary_id:
            if self.offset > leader_secondary_offset:
                state_copy = requests.get(f'/full_state')

                self.update_state_from_copy(state_copy)
                # undo... start from scratch
                pass
            else:
                response = requests.get(f'/events?start={self.offset+1}') #todo:assure success catch errors
                events = response.json()
                self.update_state(events) # update here also backlog

        # now the state is in sync

        self.is_leader = False
        self.replication_id = leader_replication_id
        self.secondary_id = leader_secondary_id
        # update offset


    def update(self, events):
        if len(events) == 0:
            return

        for event in events:
            if event['operation'] == 'add':
                service = event['service']
                key = event['key']
                value = event['value']
                offset = event['offset'] #todo: check offset match
                expiration_time = event['expiration_time']

                self.add(service, key, expiration_time, value)

            elif event['operation'] == 'remove':
                service = event['service']
                key = event['key']

                self.remove_by_key(service, key)

    
    def process_event(self, event: Event):
        # duplicate event
        if event.offset <= event.offset:
            return
            
        if event.offset > event.offset + 1:
            self.events_queue[event.offset] = event


        if event.operation == 'add':
            self.add(event.service, event.key, event.expiration_time, event.value)
        elif event.operation == 'remove':
            self.remove_by_key(event.service, event.key)
        else:
            raise Exception(f"Invalid event operation: {event.operation}")


    def remove_by_key(self, service_domain, key):
        node:Node = self.services_cache_map[service_domain].get(key, None)

        if node == None:
            raise Exception(f"Key={key} doesn't exist")
        
        self.services_cache_list[service_domain].remove(node)

        logger.info(f"Item {key} (service: {service_domain}) removed")

    
    def update_state_from_copy(self):
        raise NotImplementedError()

    
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
            self.offset += 1
            event = {
                'operation': 'remove',
                'service': service_domain,
                'key': path,
                'value': service_data_list.head.data.data,
                'expiration_time': service_data_list.head.data.expiration_time,
                'offset': self.offset
            }
            self.add_event_to_backlog(event)

            service_data_list.remove_start()

        print("cached")
        cached_data_item = CachedDataItem(data, expiration_time)
        node = service_data_list.add(cached_data_item)
        self.services_cache_map[service_domain][path] = node

        self.offset += 1

        event = {
            'operation': 'add',
            'service': service_domain,
            'key': path,
            'value': node.data.data,
            'offset': self.offset
        }
        self.add_event_to_backlog(event)


    def add_event_to_backlog(self, event):
        self.backlog.append(event)

        fire_event(event)



    def get(self, service_domain, path):
        if service_domain not in self.services:
            return None

        cached_item_node = self.services_cache_map[service_domain].get(path, None)

        if not cached_item_node or cached_item_node.data.expiration_time < datetime.datetime.utcnow():
            return None

        return cached_item_node.data.data


    def get_backlog(self):
        return self.backlog
        


__data_store = DataStore()

add = __data_store.add
get = __data_store.get
get_backlog = __data_store.get_backlog

    


