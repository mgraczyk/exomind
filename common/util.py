class lazy_property(object):
    """Defines a property whose value will be computed only once and as needed.

        This can only be used on instance methods.
    """

    def __init__(self, func):
        self._func = func

    def __get__(self, obj_self, cls):
        value = self._func(obj_self)
        setattr(obj_self, self._func.__name__, value)
        return value


class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

    def __copy__(self):
        r = AttributeDict()
        r.update(self)
        return r
