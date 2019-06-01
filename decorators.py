import collections
import functools


def default_get_id(func):
    def _getattr(attr):
        return getattr(func, attr, None)

    return _getattr("__module__"), _getattr("__qualname__")


class DictDiffKey(collections.UserDict):
    @staticmethod
    def get_id(key):
        # Override me
        return key

    def __getitem__(self, key):
        return self.data[self.get_id(key)]

    def __setitem__(self, key, item):
        self.data[self.get_id(key)] = item

    def __delitem__(self, key):
        del self.data[self.get_id(key)]

    def __contains__(self, key):
        return self.get_id(key) in self.data


class RegisteringDecorator(DictDiffKey):
    def __init__(self, get_id=default_get_id, params=True):
        super().__init__()
        self.get_id = get_id
        self.params = params

    def __call__(self, *args, second_call=False, **kargs):
        if self.params and not second_call:
            return functools.partial(self, *args, **kargs, second_call=True)
        func = args[-1]
        self[func] = (func, args[:-1], kargs)

        return func  # So it's actually a null decorator

    def register(self, obj, hook):
        valid_names = set(dir(obj))
        for key, item in self.data.items():
            print(key, item)
            if item[0].__name__ not in valid_names:
                continue
            func = getattr(obj, item[0].__name__)
            if self.get_id(func) != key:
                continue
            # You want to call hook with the bound method, which is func
            # Not item[0], which is the class function
            hook(getattr(obj, item[0].__name__), *item[1], **item[2])

        """
        for name in dir(obj):
            func = getattr(obj, name)
            if func in self:
                item = self[func]
                # You want to call hook with the bound method, which is func
                # Not item[0], which is the class function
                hook(func, *item[1], **item[2])
        """


decorate = RegisteringDecorator()
