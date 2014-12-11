class CommandDecodeException(Exception):
    def __init__(self, msg):
        self.msg = msg

class Registry:
    """ We use this class, though empty, to store class variable data
    against it so that we can access those same variables from anywhere
    without having to worry about awful import dependency issues.  Think
    of it as a poor man's windows registry. """
    pass