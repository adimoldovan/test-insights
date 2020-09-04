class Result:
    def __init__(self, status, uuid, start, stop, trace):
        self.status = status
        self.uuid = uuid
        self.start = start
        self.stop = stop
        self.trace = trace

    def __str__(self):
        return str(self.__dict__)
