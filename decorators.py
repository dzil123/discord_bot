import collections
import functools


def default_get_id(func):
    def _getattr(attr):
        return getattr(func, attr, None)

    return _getattr("__module__"), _getattr("__qualname__")


# def registering_decorator(original_decorator=lambda f: f, get_id=default_get_id):
#     registry = {}

#     def decorator(func: typing.Callable):
#         registry[get_id(func)] = func
#         return original_decorator(func)

#     decorator.dict = registry
#     decorator.exists = lambda func: get_id(func) in decorator
#     return decorator


class OldRegisteringDecorator:
    def __init__(self, original_decorator=None, get_id=default_get_id):
        self.original_decorator = original_decorator
        self.get_id = get_id
        self.registry = {}

    def __call__(self, func):
        print("Calling RDecorator\t", func)
        ID = self.get_id(func)
        self.registry[ID] = func

        if self.original_decorator:
            return self.original_decorator(func)

        return func

    def __getitem__(self, key):
        return self.registry[self.get_id(key)]

    def __contains__(self, key):
        print("Running contains", key, "\t", self.get_id(key))
        return self.get_id(key) in self.registry


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
    def __init__(self, get_id=default_get_id, params=False):
        super().__init__()
        self.get_id = get_id
        self.params = params

    def __call__(self, *args, second_call=False, **kargs):
        if self.params and not second_call:
            return functools.partial(self, *args, **kargs, second_call=True)
        func = args[-1]
        self[func] = (func, args[:-1], kargs)

        return func  # So it's actually a null decorator


class Decorator:
    decorate = OldRegisteringDecorator()

    def __new__(cls):
        print("__new__")
        inst = super().__new__(cls)

        for key in dir(inst):
            value = getattr(inst, key)
            print("\nChecking", key, "\t", value)
            if cls._is_valid(value):
                print("Valid")
                setattr(inst, key, inst.impl_decorate(value))

        return inst

    @classmethod
    def _is_valid(cls, value):  # value should be a bound method
        return ("__func__" in dir(value)) and (value in cls.decorate)

    def impl_decorate(self, func):
        print("Implement me!")
