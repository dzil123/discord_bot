#!/usr/bin/env python3
import asyncio
import discord
from discord.ext import commands
import typing

import decorators

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


class Pagination:
    register = decorators.RegisteringDecorator(params=True)

    def __init__(self, ctx: commands.Context):
        self.ctx = ctx

    @register(EMOJI["x"])
    def react_delete(self, reaction, user):
        pass

    @register(EMOJI["left"])
    def react_prev(self, reaction, user):
        pass

    @register(EMOJI["right"])
    def react_next(self, reaction, user):
        pass


@bot.add_listener
async def on_ready():
    print("ready")


@bot.command()
async def go(ctx: commands.Context, num: int):
    e = discord.Embed(
        title="hi", description="descript", color=discord.Color.dark_magenta()
    )
    message: discord.Message = await ctx.send("text", embed=e)
    await message.add_reaction(EMOJI[num])
    await asyncio.sleep(1)
    await message.clear_reactions()


@bot.command()
async def ge(ctx: commands.Context, s: str):
    message: discord.Message = await ctx.send("text")
    await message.add_reaction(s)


@bot.command()
async def gi(ctx: commands.Context, s: str):
    message: discord.Message = await ctx.send("text")
    await message.add_reaction(s + "\u20e3")


def main(token):
    bot.run(token)


if __name__ == "__main__":
    import secret_config

    main(secret_config.token)
