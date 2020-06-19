class Error(Exception):
    pass

class ConnectionFailedError(Error):
    def __init__(self, msg):
        self.msg = msg