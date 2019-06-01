#!/usr/bin/env python3
import asyncio
import discord
from discord.ext import commands
import typing

from decorators import decorate

EMOJI = {
    "smiley": "\U0001f603",
    10: "\U0001f51f",
    "x": "\u274c",
    "left": "\u2b05",
    "right": "\u27a1",
}

for x in range(10):
    EMOJI[x] = str(x) + "\u20e3"


bot = commands.Bot(command_prefix="!")


class RespondToEmoji:
    def __init__(
        self,
        ctx: commands.Context,
        embed: discord.Embed,
        restrict_to_user=True,
        timeout=30,
    ):
        self.ctx = ctx
        self.embed = embed
        if restrict_to_user == True:
            restrict_to_user = ctx.author
        self.restrict_to_user = restrict_to_user
        self.emoji_hooks = {}
        self.timeout = timeout
        decorate.register(self, self.register_hook)
        print(self.emoji_hooks)

    def register_hook(self, func, emoji):
        self.emoji_hooks[emoji] = func

    def event_check(self, reaction, user):
        return all(
            (
                reaction.message.id == self.message.id,
                reaction.emoji in self.emoji_hooks,
                user.id != self.ctx.bot.user.id,
                (not self.restrict_to_user or user.id == self.restrict_to_user.id),
            )
        )

    async def create_initial_reactions(self):
        for emoji in self.emoji_hooks:
            await self.message.add_reaction(emoji)

    async def delete_user_reaction(self, reaction, user):
        await self.message.remove_reaction(reaction.emoji, user)

    async def wait_for_reaction(self):
        return await self.ctx.bot.wait_for(
            "reaction_add", timeout=self.timeout, check=self.event_check
        )

    async def do_iteration(self):  # return False if exit
        try:
            reaction, user = await self.wait_for_reaction()
            async with self.ctx.typing():
                func = self.emoji_hooks[reaction.emoji]
                return await func(reaction, user)
        except asyncio.TimeoutError:
            return False

    async def mainloop(self):
        # setup
        async with self.ctx.typing():
            self.message = await self.ctx.send(embed=self.embed)
            await self.create_initial_reactions()

        # loop
        while await self.do_iteration():
            pass

        # cleanup

        await self.message.clear_reactions()

    @classmethod
    async def create(cls, ctx: commands.Context, embed: discord.Embed, *args, **kargs):
        inst = cls(ctx, embed, *args, **kargs)
        await inst.mainloop()


class Counter(RespondToEmoji):
    def __init__(self, ctx: commands.Context):
        self.num = 10
        embed = discord.Embed(title="Counter", description=str(self.num))
        super().__init__(ctx, embed)

    @decorate(EMOJI["left"])
    async def subtract(self, reaction, user):
        await self.delete_user_reaction(reaction, user)
        self.num -= 1
        self.embed.description = str(self.num)
        await self.message.edit(embed=self.embed)

        return True

    @decorate(EMOJI["right"])
    async def add(self, reaction, user):
        await self.delete_user_reaction(reaction, user)
        self.num += 1
        self.embed.description = str(self.num)
        await self.message.edit(embed=self.embed)

        return True

    @decorate(EMOJI["x"])
    async def exit(self, reaction, user):
        return False


@bot.add_listener
async def on_ready():
    print("ready")


@bot.command()
async def count(ctx):
    async with ctx.typing():
        counter = Counter(ctx)
    await counter.mainloop()


def main(token):
    bot.run(token)
    # Pagination(None)


if __name__ == "__main__":
    import secret_config

    main(secret_config.token)
