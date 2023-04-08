import json


class Resource(dict):
    def __init__(self, filePath=None, /, **kwargs):
        self.file = filePath
        self.autoSubmit = True
        if self.file:
            self.read(self.file)
        if kwargs:
            super().__init__(**kwargs)

    def attach(self, file):
        self.file = file

    def read(self, file=None):
        if not file:
            file = self.file
        with open(file, encoding="utf8") as f:
            super().__init__(json.load(f))

    def submit(self, file=None):
        file = file or self.file
        if not file:
            return
        with open(file, mode='w', encoding="utf8") as f:
            f.write(repr(self))

    def submittable(func):
        def wrapper(self, *args):
            res = func(self, *args)
            if self.autoSubmit:
                self.submit()
            return res
        return wrapper

    def toggleAutoSubmit(self):
        self.autoSubmit = not self.autoSubmit

    @submittable
    def clear(self):
        return super().clear()

    @submittable
    def __setitem__(self, k, v):
        return super().__setitem__(k, v)

    def __str__(self):
        return json.dumps(self)

    def __repr__(self):
        return json.dumps(self, indent=4)
