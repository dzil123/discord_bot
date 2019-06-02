#!/usr/bin/env python3
import asyncio
import contextlib
import discord
from discord.ext import commands
import logging

from decorators import decorate
from emoji import Emoji, MessageStack
from util import random_string

bot = commands.Bot(command_prefix="!")


class Counter(MessageStack):
    def __init__(self, ctx: commands.Context):
        self.num = 10
        embed = discord.Embed(title="Counter", description=str(self.num))
        super().__init__(ctx, embed, timeout=None)

    async def update(self):
        self.embed.description = str(self.num)
        # await self.message.edit(embed=self.embed)

        self.emoji_hooks[Emoji.smiley].active = self.num >= 12
        # await self.update_reactions()
        await self.ctx.send(embed=self.embed)

    @decorate(Emoji.left)
    async def subtract(self, reaction, user):
        await self.delete_user_reaction(reaction, user)
        self.num -= 1

        await self.update()

    @decorate(Emoji.smiley, active=False)
    async def smile(self, reaction, user):
        self.num = min(11, self.num)

        await self.update()

    @decorate(Emoji.right)
    async def add(self, reaction, user):
        await self.delete_user_reaction(reaction, user)
        self.num += 1

        await self.update()

    @decorate(Emoji.x)
    async def exit(self, reaction, user):
        # async with self.ctx.typing():
        #     print("x pressed")
        #     await self.delete_all_reactions()
        #     await self.update_reactions()

        return True

    @decorate(Emoji.rewind)
    async def rewind(self, reaction, user):
        await self.pop_message()


BOT_BOT_BOT_SERVER: discord.Guild = None
BOT_CATEGORY: discord.CategoryChannel = None


@contextlib.asynccontextmanager
async def send_in_new_channel(author: discord.Member):
    channel: discord.TextChannel = None
    try:
        name = author.display_name + " " + random_string(8)
        channel = await BOT_CATEGORY.create_text_channel(name=name)
        await channel.set_permissions(author, read_messages=True)

        yield channel
    finally:
        try:
            await channel.delete()
        except AttributeError:  # channel is None
            pass


@bot.command()
async def go(ctx):
    async with send_in_new_channel(ctx.author) as channel:
        await channel.send("Greetings " + ctx.author.mention + "!")

        num = 5
        msg: discord.Message = await channel.send(
            content=f"Game will begin in {num}..."
        )
        for x in range(num, -1, -1):
            await asyncio.sleep(1)
            await msg.edit(content=f"Game will begin in {x}...")

        ctx.send = channel.send
        counter = Counter(ctx)
        await counter.mainloop()
        await ctx.send("Thank you for playing!")
        await asyncio.sleep(5)


@bot.add_listener
async def on_ready():
    print("ready")
    global BOT_BOT_BOT_SERVER, BOT_CATEGORY
    BOT_BOT_BOT_SERVER = bot.get_guild(583530359782637579)
    BOT_CATEGORY = BOT_BOT_BOT_SERVER.get_channel(584636614203146250)


@bot.command()
async def count(ctx):
    async with ctx.typing():
        counter = Counter(ctx)
    await counter.mainloop()


@bot.command()
async def embed(ctx):
    """A simple command which showcases the use of embeds.
    Have a play around and visit the Visualizer."""

    embed = discord.Embed(
        title="Example Embed",
        description="Showcasing the use of Embeds...\nSee the visualizer for more info.",
        colour=0x98FB98,
    )
    embed.set_author(
        name="MysterialPy",
        url="https://gist.github.com/MysterialPy/public",
        icon_url="http://i.imgur.com/ko5A30P.png",
    )
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/84319995256905728/252292324967710721/embed.png"
    )

    embed.add_field(
        name="Embed Visualizer",
        value="[Click Here!](https://leovoel.github.io/embed-visualizer/)",
    )
    embed.add_field(name="Command Invoker", value=ctx.author.mention)
    embed.set_footer(
        text="Made in Python with discord.py@rewrite",
        icon_url="http://i.imgur.com/5BFecvA.png",
    )

    await ctx.send(
        content="**A simple Embed for discord.py@rewrite in cogs.**", embed=embed
    )


def main(token):
    logging.basicConfig(level=logging.INFO)
    bot.run(token)
    # Pagination(None)


if __name__ == "__main__":
    import secret_config

    main(secret_config.token)
