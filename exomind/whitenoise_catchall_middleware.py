from whitenoise.middleware import WhiteNoiseMiddleware


class WhiteNoiseCatchAllMiddleware(WhiteNoiseMiddleware):
    """Wrap WhiteNoiseMiddleware so we can use it to send respond to 404"""
    INSTANCES = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.INSTANCES.append(self)

    @classmethod
    def serve_file_by_path(cls, request, path):
        assert len(cls.INSTANCES) == 1
        instance = cls.INSTANCES[0]

        if instance.autorefresh:
            static_file = instance.find_file(path)
        else:
            static_file = instance.files.get(path)

        return instance.serve(static_file, request)
