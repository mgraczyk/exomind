from os import urandom
from uuid import UUID
from base64 import urlsafe_b64encode, urlsafe_b64decode


class B64ID(UUID):
    def __init__(self, arg0=None, **kwargs):
        if isinstance(arg0, UUID):
            super().__init__(int=arg0.int)
        elif isinstance(arg0, str) and len(arg0) == 22:
            super().__init__(bytes=urlsafe_b64decode(arg0 + '=='))
        else:
            super().__init__(arg0, **kwargs)

    def __str__(self):
        b = self.int.to_bytes(16, 'big')
        return urlsafe_b64encode(b)[:22].decode()

    def as_uuid(self):
        return UUID(int=self.int)

    def as_uuid_str(self):
        return super().__str__()


def b64id4():
    return B64ID(bytes=urandom(16), version=4)
