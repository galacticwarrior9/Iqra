import discord
from discord.ext import commands

intents = discord.Intents(guilds=True, voice_states=True, messages=True, reactions=True)
bot = commands.Bot(command_prefix='-', intents=intents)

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
