

class Use:
    def __init__(self, call, *args, **kwargs):
        self.call = call
        self.args = args
        self.kwargs = kwargs

    def to_value(self):
        return self.call(*self.args, **self.kwargs)
    pass


class Required:
    pass


class Ignored:
    pass
