from discord.ext.commands import Bot
import random
import string

charset = string.ascii_uppercase + string.digits


def random_string(length: int):
    return "".join(random.choice(charset) for x in range(length))


class CloseableBot(Bot):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.close_hooks = []

    def add_close_hook(self, hook):
        self.close_hooks.append(hook)

    def remove_close_hook(self, hook):
        try:
            self.close_hooks.remove(hook)
        except ValueError:
            print("ValueError on removing close hook:", hook)

    async def close(self):
        print("hook into close()")
        if self._closed:
            return

        for hook in self.close_hooks[:]:  # create copy of list
            print("closing", hook)
            await hook.__aexit__()

        await super().close()
