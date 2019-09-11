class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def __copy__(self):
        r = AttributeDict()
        r.update(self)
        return r
