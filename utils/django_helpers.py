from utils.b64id import B64ID


class B64IDConverter:
  regex = '[-a-zA-Z0-9_]{22}'

  def to_python(self, v):
    return B64ID(v)

  def to_url(self, v):
    return str(v)
