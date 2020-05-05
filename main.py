import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='-')


@bot.event
async def on_ready():
    print(f"Logged in on {len(bot.guilds)} servers.")
    presence = discord.Game("-qhelp")
    await bot.change_presence(activity=presence)

    bot.remove_command('help')

    cogs = ['quran', 'help']

    for cog in cogs:
        bot.load_extension(cog)

token = open("token.txt", "r").read()
bot.run(token.strip())
