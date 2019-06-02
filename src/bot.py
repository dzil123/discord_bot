#!/usr/bin/env python3
import asyncio
from collections import namedtuple
from dataclasses import dataclass
import discord
from discord.ext import commands
import typing

from decorators import decorate
from emoji import EMOJI, RespondToEmoji

bot = commands.Bot(command_prefix="!")


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
