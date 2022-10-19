
class AuthResponse(dict):
    def __init__(self, token, expires_in, is_admin):
        self.token = token
        self.expires_in = expires_in