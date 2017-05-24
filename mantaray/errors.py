class MantarayError(Exception):
    pass


class MantarayNotImplemented(MantarayError):
    def __init__(self, obj):
        super().__init__("Support of `{0}` is not yet implemented".format(obj))
