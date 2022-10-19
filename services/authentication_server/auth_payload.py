from datetime import datetime
import os
import datetime

class AuthPayload(dict):
    def __init__(self, id, client_id, is_admin):
        EXPIRESSECONDS = int(os.getenv('EXPIRESSECONDS'))

        self.id = id

        self.sub = client_id
        self.is_admin = is_admin

        self.exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=EXPIRESSECONDS)