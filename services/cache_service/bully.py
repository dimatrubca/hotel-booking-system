
from config import settings


class Bully:
    def __init__(self, id, ):
        self.id = id
        self.election = False
        self.coordinator = None
        self.heart_beating_leader = False
        self.replication_id = None
        self.secondary_replication_id = None
        self.last_leader_change_timestamp = None

bully = Bully(id=settings.SERVICE_ID)