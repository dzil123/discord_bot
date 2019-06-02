#!/usr/bin/env python3
import asyncio
import discord
from discord.ext import commands
import random
import string

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

    @decorate(EMOJI["smiley"], active=False)
    async def smile(self, reaction, user):
        self.num = min(11, self.num)

        await self.update()

    @decorate(EMOJI["right"])
    async def add(self, reaction, user):
        await self.delete_user_reaction(reaction, user)
        self.num += 1

        await self.update()

    @decorate(EMOJI["x"])
    async def exit(self, reaction, user):
        async with self.ctx.typing():
            print("x pressed")
            await self.delete_all_reactions()
            await self.update_reactions()


BOT_BOT_BOT_SERVER = None
BOT_CATEGORY = None


charset = string.ascii_uppercase + string.digits


async def send_in_new_channel(ctx):
    channel = None
    try:
        name = (
            ctx.author.display_name
            + " "
            + "".join(random.choice(charset) for _ in range(8))
        )
        overwrite = discord.PermissionOverwrite(read_messages=True)
        channel = await BOT_CATEGORY.create_text_channel(name=name)
        await channel.set_permissions(ctx.author, overwrite=overwrite)
        await channel.send("Hello, boy")
        await asyncio.sleep(300)
    finally:
        try:
            await channel.delete()
        except AttributeError:  # channel is None
            pass


@bot.command()
async def go(ctx):
    async with ctx.typing():
        await send_in_new_channel(ctx)


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
    bot.run(token)
    # Pagination(None)


if __name__ == "__main__":
    import secret_config

    main(secret_config.token)
