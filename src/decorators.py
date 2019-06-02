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


class MethodMarker(DictDiffKey):
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

    def resolve(self, obj):
        methods = []

        for key, item in self.data.items():
            func = getattr(obj, item[0].__name__)  # todo, use types.methodtype
            if self.get_id(func) != key:
                continue
            methods.append((func, item[1], item[2]))

        return methods


decorate = MethodMarker()
