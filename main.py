import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='-')

cogs = ['quran', 'help', 'reciters']

for cog in cogs:
    bot.load_extension(cog)

bot.remove_command('help')


@bot.event
async def on_ready():
    print(f"Logged in on {len(bot.guilds)} servers.")
    presence = discord.Game("-qhelp")
    await bot.change_presence(activity=presence)


token = open("token.txt", "r").read()
bot.run(token.strip())
