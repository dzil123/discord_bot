#!/usr/bin/env python3
import asyncio
from collections import namedtuple
from dataclasses import dataclass
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


@dataclass
class ReactionEntry:
    func: typing.Callable
    active: bool


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
        for emoji_entry in decorate.resolve(self):
            emoji = emoji_entry[1][0]
            func = emoji_entry[0]
            active = emoji_entry[2].get("active", True)

            self.emoji_hooks[emoji] = ReactionEntry(func, active)

    def event_check(self, reaction, user):
        return all(
            (
                reaction.message.id == self.message.id,
                reaction.emoji in self.emoji_hooks
                and self.emoji_hooks[reaction.emoji].active,
                user.id != self.ctx.bot.user.id,
                (not self.restrict_to_user or user.id == self.restrict_to_user.id),
            )
        )

    async def update_message(self):
        self.message = await self.message.channel.fetch_message(self.message.id)

    async def create_initial_reactions(self):
        for emoji, entry in self.emoji_hooks.items():
            if entry.active:
                await self.message.add_reaction(emoji)

    async def update_reactions(self):
        await self.update_message()

        if len(self.message.reactions) == 0:
            await self.delete_all_reactions()
            return

        emojis = [reaction.emoji for reaction in self.message.reactions]

        for emoji, entry in self.emoji_hooks.items():
            exists = emoji in emojis
            if exists and not entry.active:
                reaction = [
                    reaction
                    for reaction in self.message.reactions
                    if reaction.emoji == emoji
                ][0]
                await self.delete_reaction_all_users(reaction)
            if not exists and entry.active:
                await self.message.add_reaction(emoji)

    async def delete_user_reaction(self, reaction, user):
        await self.message.remove_reaction(reaction.emoji, user)

    async def delete_reaction_all_users(self, reaction):
        async for user in reaction.users():
            await reaction.remove(user)

    async def delete_all_reactions(self):
        await self.message.clear_reactions()

    async def wait_for_reaction(self):
        return await self.ctx.bot.wait_for(
            "reaction_add", timeout=self.timeout, check=self.event_check
        )

    async def do_iteration(self):  # return False if exit
        try:
            reaction, user = await self.wait_for_reaction()
            await self.update_message()
            # async with self.ctx.typing():
            entry = self.emoji_hooks[reaction.emoji]
            return await entry.func(reaction, user)
        except asyncio.TimeoutError:
            return False

    async def mainloop(self):
        # setup
        async with self.ctx.typing():
            self.message: discord.Message = await self.ctx.send("Loading...")
            await self.create_initial_reactions()
            await self.message.edit(content=None, embed=self.embed)

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
        super().__init__(ctx, embed, timeout=None)

    async def update(self):
        self.embed.description = str(self.num)
        await self.message.edit(embed=self.embed)

        self.emoji_hooks[EMOJI["smiley"]].active = self.num >= 12
        await self.update_reactions()

    @decorate(EMOJI["left"])
    async def subtract(self, reaction, user):
        await self.delete_user_reaction(reaction, user)
        self.num -= 1

        await self.update()

        return True

    @decorate(EMOJI["right"])
    async def add(self, reaction, user):
        await self.delete_user_reaction(reaction, user)
        self.num += 1

        await self.update()

        return True

    @decorate(EMOJI["x"])
    async def exit(self, reaction, user):
        return False

    @decorate(EMOJI["smiley"], active=False)
    async def smile(self, reaction, user):
        self.num = min(11, self.num)

        await self.update()

        return True


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
