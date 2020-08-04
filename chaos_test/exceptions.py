class UnreachableActException(Exception):
    def __init__(self, message, act):
        super(UnreachableActException, self).__init__(message)

class FailedAct(Exception):
    def __init__(self, message, act):
        super(FailedAct, self).__init__(message)