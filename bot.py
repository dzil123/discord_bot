import asyncio
import discord
from discord.ext import commands


EMOJI = {"smiley": "\U0001f603", 10: "\U0001f51f"}

for x in range(10):
    EMOJI[x] = str(x) + "\u20e3"


bot = commands.Bot(command_prefix="!")


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
