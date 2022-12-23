import heapq
import json
import pickle
from typing import Dict, List
from queue import PriorityQueue

import datetime
import sys
import logging
import uuid

import requests
import utils

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
        self.services_cache_map:Dict[str, Dict[str, Node]] = {}
        self.services_cache_list:Dict[str,DoublyLinkedList] = {}
        self.expiration_time_heap:Dict[str, PriorityQueue] = {}

        self.service_item_max_size = 1024 * 32
        self.per_service_memory_limit = self.service_item_max_size * 8

        self.replication_id = str(uuid.uuid1())
        self.secondary_id = str(uuid.uuid1())

        self.is_leader = False
        self.backlog = []
        self.replication_offset = 0
        self.secondary_backlog = []
        self.secondary_offset = 0
        self.events_queue = {}

    
    def on_become_leader(self):
        self.is_leader = True
        self.secondary_id = self.replication_id
        self.replication_id = str(uuid.uuid1())
        self.secondary_offset = self.replication_offset
        self.secondary_backlog = self.backlog #todo: copy? remove secondary?

        logger.info(f"Became leader, replication_id: {self.replication_id}, secondary_id: {self.secondary_id}")
        # self.replication_offset = 0 # do not reset offset
        # keep backlog

    def get_copy(self):
        expiration_time_heap = {}

        #todo: doublecheck
        for key, queue in self.expiration_time_heap.items():
            queue_items = queue.queue
            heapq.heapify(queue_items)
            expiration_time_heap[key] = queue_items
            print(f'key: {key}, value: {expiration_time_heap[key]}')

        data = [self.replication_id, self.replication_offset, self.backlog, self.services_cache_map, self.services_cache_list, expiration_time_heap, self.services]
        data_pickle = pickle.dumps(data)
        print('map:', self.services_cache_map.items())

        logger.info(f"inside get_copy, data_pickle: {data_pickle}")
        
        return data_pickle

    def update_state_from_copy(self, data_pickle):
        logger.info("Inside update_state_from_copy, data: {data}")

        data = pickle.loads(data_pickle)

        self.replication_id = data[0]
        self.replication_offset = data[1]
        self.backlog = data[2]
        self.services_cache_map = data[3]
        self.services_cache_list = data[4]

        expiration_time_heap = data[5]
        self.services = data[6]

        self.expiration_time_heap:Dict[str, PriorityQueue] = {}


        for key, queue in expiration_time_heap.items():
            pq = PriorityQueue()

            while len(queue) != 0:
                item = queue.heappop()
                pq.put(item)

            self.expiration_time_heap[key] = pq

        # print("state updated from copy: ", self.expiration_time_heap)
        # print(self.expiration_time_heap.items())
        # print('cache list:', self.services_cache_list.items())

        # for key, item in self.services_cache_list.items():
        #     print(item.print_list())

        # print('map:', self.services_cache_map.items())
        # print(self.services_cache_map['string'])
        # print(self.services_cache_map['string'].get('string/', None))


    def get_replication_id(self):
        return self.replication_id

    
    def get_secondary_id(self):
        return self.secondary_id

    def get_replication_offset(self):
        return self.replication_offset

    
    def get_secondary_offset(self):
        return self.secondary_offset


    def on_leader_updated(self, leader_host, leader_replication_id, leader_offset, leader_secondary_id, leader_secondary_offset):
        assert leader_offset >= leader_secondary_offset, 'offset mismatch'

        logger.info(f"Inside on leader update. rid: {self.replication_id}, offset: {self.replication_offset}, leader rid: {leader_replication_id},\
                        leader offset: {leader_offset}, leader sid: {leader_secondary_id}, leader soffset: {leader_offset}")

        if self.replication_id == leader_secondary_id:
            if self.replication_offset > leader_secondary_offset: #todo: check
                logger.info("Sync, requesting full copy, id match, offset mismatch")
                state_copy = requests.get(f'{leader_host}/full_copy')

                self.update_state_from_copy(state_copy.content)
                # undo... start from scratch
                pass
            else:
                logger.info(f"Sync, requesting events from {self.replication_offset + 1}")
                response = requests.get(f'{leader_host}/events?start={self.replication_offset+1}') #todo:assure success catch errors
                events = response.json()
                self.update(events) # update here also backlog
        else:
            logger.info("Sync, requesting full coppy, diff ids")
            state_copy = requests.get(f'{leader_host}/full_copy')
            self.update_state_from_copy(state_copy.content)

        # now the state is in sync

        self.is_leader = False
        self.replication_id = leader_replication_id
        self.secondary_id = leader_secondary_id
        # update offset


    def update(self, events):
        if len(events) == 0:
            return


        for event in events:
            event = Event(operation=event['operation'], service=event['service'], key=event['key'], value=event['value'],\
                            offset=event['offset'], expiration_time=event['expiration_time'])

            self.process_event(event)

    
    def process_event(self, event: Event):
        # duplicate event
        if event.offset <= self.replication_offset:
            return
            
        if event.offset > event.offset + 1:
            logger.info(f"queueing event, event_offset: {event.offset}, current offset: {self.replication_offset}")
            self.events_queue[event.offset] = event

            return


        if event.operation == 'add':
            self.add(event.service, event.key, event.expiration_time, event.value)
        elif event.operation == 'remove':
            self.remove_by_key(event.service, event.key)
        elif event.operation == 'update_expiration_time':
            self.update_expiration_time(event.service, event.key, event.expiration_time)
        else:
            raise Exception(f"Invalid event operation: {event.operation}")
        

    def remove_by_key(self, service_name, key):
        node:Node = self.services_cache_map[service_name].get(key, None)

        if node == None:
            raise Exception(f"Key={key} doesn't exist")
        
        self.services_cache_list[service_name].remove(node)

        self.replication_offset += 1

        event = {
            'operation': 'remove_by_key',
            'service': service_name,
            'key': key,
            'value': 'val',
            'expiration_time': None, #todo: correct
            'offset': self.replication_offset
        }
        self.add_event_to_backlog(event)
        logger.info(f"Item {key} (service: {service_name}) removed")

    
    def remove_expired_items(self,  service_name):
        if service_name not in self.expiration_time_heap:
            return
        
        expiration_time_heap = self.expiration_time_heap
        expiration_time_heap.acquire()

        now = datetime.datetime.utcnow()

        while not expiration_time_heap.empty() and expiration_time_heap.queue[0][0].expiration_time < now:
            item = expiration_time_heap.get() #dead lock ??? block=False
            self.services_cache_list[service_name].remove(item)
        
        self.expiration_time_heap.release()

    
    def update_expiration_time(self, service, key, expiration_time):
        cached_item_node = self.services_cache_map[service].get(key, None)
        cached_item_node.data.expiration_time = expiration_time
        self.services_cache_list[service].move_to_end(cached_item_node)

        self.replication_offset += 1

        event = {
            'operation': 'update_expiration_time',
            'service': service,
            'key': key,
            'value': cached_item_node.data.data,
            'expiration_time': expiration_time, 
            'offset': self.replication_offset
        }
        self.add_event_to_backlog(event)



    def add(self, service_name, path, expiration_time, data: str):
        if service_name not in self.services:
            self.services.append(service_name)
            self.services_cache_map[service_name]: Dict[str, Node] = {}
            self.services_cache_list[service_name] = DoublyLinkedList()
            self.expiration_time_heap[service_name] = PriorityQueue()
            
        cached_item_node = self.services_cache_map[service_name].get(path, None)

        if cached_item_node:
            self.update_expiration_time(service_name,path, expiration_time)

            return
    
        new_data_size = sys.getsizeof(data)
        # print("data size:", new_data_size, self.service_item_max_size)

        if new_data_size > self.service_item_max_size:
            raise Exception('Data exceeds max limit') 

        # print("list...")
        # print(f'service name: {service_name}')
        service_data_list: DoublyLinkedList = self.services_cache_list[service_name]

        # print("while...")
        while not service_data_list.empty() and service_data_list.data_size + new_data_size > self.per_service_memory_limit:
            self.replication_offset += 1
            event = {
                'operation': 'remove',
                'service': service_name,
                'key': path,
                'value': service_data_list.head.data.data,
                'expiration_time': service_data_list.head.data.expiration_time,#remove expiration time
                'offset': self.replication_offset
            }
            self.add_event_to_backlog(event)

            service_data_list.remove_start()

        # print("cached")
        cached_data_item = CachedDataItem(data, expiration_time)
        node = service_data_list.add(cached_data_item)
        self.services_cache_map[service_name][path] = node

        self.replication_offset += 1

        event = {
            'operation': 'add',
            'service': service_name,
            'key': path,
            'value': node.data.data,
            'expiration_time': node.data.expiration_time,
            'offset': self.replication_offset
        }
        self.add_event_to_backlog(event)


    def add_event_to_backlog(self, event):
        self.backlog.append(event)

        if self.is_leader:
            utils.fire_event(event)



    def get(self, service_name, path):
        if service_name not in self.services:
            return None

        cached_item_node = self.services_cache_map[service_name].get(path, None)

        if not cached_item_node or cached_item_node.data.expiration_time < datetime.datetime.utcnow():
            return None

        return cached_item_node.data.data


    def get_backlog(self):
        return self.backlog
        


__data_store = DataStore()

add = __data_store.add
get = __data_store.get
get_backlog = __data_store.get_backlog
process_event = __data_store.process_event
on_become_leader = __data_store.on_become_leader
on_leader_updated = __data_store.on_leader_updated
get_replication_id = __data_store.get_replication_id
get_secondary_id = __data_store.get_secondary_id
get_replication_offset = __data_store.get_replication_offset
get_secondary_offset = __data_store.get_secondary_offset
get_copy = __data_store.get_copy
update_state_from_copy = __data_store.update_state_from_copy

            
