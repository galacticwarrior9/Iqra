import discord
import asyncio
import youtube_dl
import aiohttp
from discord.ext import commands
from fuzzywuzzy import process, fuzz

from reciters import everyayah_reciters, get_mp3quran_reciter

RECITATION_NOT_FOUND = "**Could not find a recitation for the surah by this reciter.** Try a different surah."
RECITER_NOT_FOUND = "**Couldn't find reciter!** Type `-reciters` for a list of available reciters."
SURAH_NOT_FOUND = "**Surah not found** Use the surah's name or number. Examples: \n\n`-qplay surah" \
                  " al-fatihah`\n\n`-qplay surah 1`"
PAGE_NOT_FOUND = "**Sorry, the page must be between 1 and 604.**"
DISCONNECTED = "**Successfully disconnected.**"
INVALID_VOLUME = "**The volume must be between 0 and 100.**"
INVALID_VERSE = "**Please provide a verse.** For example, 1:2 is Surah al-Fatiha, ayah 2."
NON_EXISTENT_VERSE = "**There are only {} verses in this surah.**"
ALREADY_PLAYING = "**Already playing**. To stop playing, type `-qstop`."
NOT_PLAYING = "The bot is not playing."

players = {}


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}


ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


async def get_surah_names():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://api.quran.com/api/v3/chapters') as r:
            data = await r.json()
        surahs = data['chapters']

    surah_names = {}
    for surah in surahs:
        surah_names[surah['name_simple'].lower()] = surah['id']

    return surah_names


async def get_surah_id_from_name(surah_name):
    surah_names = await get_surah_names()
    surah_id = surah_names[surah_name]
    return surah_id


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Quran(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.info_url = 'http://api.quran.com:3000/api/v3/chapters/{}'
        self.reciter_info_url = 'http://mp3quran.net/api/_english.php'
        self.makkah_url = 'http://66.226.10.51:8000/SaudiTVArabic?dl=1'
        self.quranradio_url = 'http://live.mp3quran.net:8006/stream?type=http&nocache=29554'
        self.page_url = 'https://everyayah.com/data/{}/PageMp3s/Page{}.mp3'
        self.ayah_url = 'https://everyayah.com/data/{}/{}.mp3'
        self.mushaf_url = 'https://www.searchtruth.org/quran/images1/{}.jpg'

    def make_ayah_url(self, surah, ayah, reciter):
        url_surah = str(surah).zfill(3)
        url_ayah = str(ayah).zfill(3)

        try: url_reciter = everyayah_reciters[reciter]
        except KeyError: return None

        url_ref = f'{url_surah}{url_ayah}'
        url = self.ayah_url.format(url_reciter, url_ref)

        return url

    def make_page_url(self, page, reciter):
        try: url_reciter = everyayah_reciters[reciter]
        except KeyError: return None

        url_page = str(page).zfill(3)
        url = self.page_url.format(url_reciter, url_page)

        return url, url_page

    async def get_surah_info(self, surah):
        async with self.session.get(self.info_url.format(surah)) as r:
            data = await r.json()
            name = data['chapter']['name_simple']
            arabic_name = data['chapter']['name_arabic']

        return name, arabic_name

    @staticmethod
    def get_qplay_file(url, surah):
        file_name = str(surah).zfill(3) + '.mp3'
        file_url = f'{url}/{file_name}'
        return file_url

    async def get_verse_count(self, surah):
        async with self.session.get(self.info_url.format(surah)) as r:
            data = await r.json()
            verses_count = data['chapter']['verses_count']
            verses_count = int(verses_count)
        return verses_count

    def make_embed(self, title, description, footer, colour, image=None):
        em = discord.Embed(title=title, colour=colour, description=description)
        em.set_footer(text=footer)
        if image is not None:
            em.set_image(url=image)
        return em

    @commands.group()
    async def qplay(self, ctx):
        if ctx.invoked_subcommand is None:
            return await ctx.send('**Invalid arguments**. For help, type `-qhelp qplay`.')

    @qplay.command()
    async def surah(self, ctx, surah, *, reciter: str = 'Mishary Alafasi'):

        if ctx.voice_client.is_playing():
            return await ctx.send(ALREADY_PLAYING)

        try:
            surah = int(surah)

        except ValueError:
            try:
                surah = await get_surah_id_from_name(surah.lower())
            # We try to suggest a correction if an invalid surah name string is given.
            except KeyError:
                surah_names = await get_surah_names()
                result = process.extract(surah, surah_names.keys(), scorer=fuzz.partial_ratio, limit=1)
                if result is not None:
                    await ctx.send(f'Could not find {surah}, so the closest match - *{result[0][0]}* - will be used.')
                    surah = await get_surah_id_from_name(result[0][0].lower())
                else:
                    return await ctx.send(SURAH_NOT_FOUND)

        reciter = await get_mp3quran_reciter(reciter.lower())

        if reciter is None:
            return await ctx.send(RECITER_NOT_FOUND)

        if not 0 < surah <= 114:
            return await ctx.send(SURAH_NOT_FOUND)

        file_url = self.get_qplay_file(reciter.server, surah)

        try:
            player = await YTDLSource.from_url(file_url, loop=self.bot.loop, stream=True)
        except:
            return await ctx.send(RECITATION_NOT_FOUND)

        players[ctx.guild.id] = player

        try:
            ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect()
                                                                                           , self.bot.loop))
        except discord.errors.ClientException as e:
            return print(e)

        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}).\nReciter: **{reciter.name}**.' \
                      f'\nRiwayah: {reciter.riwayah}'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400)
        await ctx.send(embed=em)

    @qplay.command()
    async def ayah(self, ctx, ref: str, *, reciter: str = 'mishary al-afasy'):

        if ctx.voice_client.is_playing():
            return await ctx.send(ALREADY_PLAYING)

        try:
            surah, ayah = ref.split(':')
            surah = int(surah)
            ayah = int(ayah)

        except:
            return await ctx.send("Invalid arguments. Commands: `-qplay ayah <surah>:<ayah> <reciter>`."
                                  "\n\nExample: `-qplay ayah 2:255 abdul rahman al-sudais`.")

        reciter = reciter.lower()

        if reciter not in everyayah_reciters:
            return await ctx.send(RECITER_NOT_FOUND)

        if not 0 < surah <= 114:
            return await ctx.send(SURAH_NOT_FOUND)

        verse_count = await self.get_verse_count(surah)
        if ayah > verse_count:
            return await ctx.send(NON_EXISTENT_VERSE.format(verse_count))

        url = self.make_ayah_url(surah, ayah, reciter)
        try: player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            return await ctx.send(RECITATION_NOT_FOUND)

        players[ctx.guild.id] = player
        try:
            ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect()
                                                                                           , self.bot.loop))
        except discord.errors.ClientException as e:
            return print(e)

        reciter = reciter.replace('-', ' - ').title().replace(' - ', '-')
        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}), Ayah {ayah}. ' \
                      f'\nReciter: **{reciter}**.'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
                             f'https://everyayah.com/data/QuranText_jpg/{surah}_{ayah}.jpg')
        await ctx.send(embed=em)

    @qplay.command()
    async def page(self, ctx, page: int, *, reciter: str = 'mishary al-afasy'):

        if ctx.voice_client.is_playing():
            return await ctx.send(ALREADY_PLAYING)

        try:
            page = int(page)
        except:
            return await ctx.send("Invalid arguments. Commands: `-qpage <page>:<ayah> <reciter>`."
                                  "\n\nExample: `-qayah 604 abdul rahman al-sudais`.")

        reciter = reciter.lower()
        readable_reciter = reciter.replace('-', ' - ').title().replace(' - ', '-')

        if reciter not in everyayah_reciters:
            return await ctx.send(RECITER_NOT_FOUND)

        if not 0 < page <= 604:
            return await ctx.send(PAGE_NOT_FOUND)

        url, url_page = self.make_page_url(page, reciter)

        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            return await ctx.send(RECITATION_NOT_FOUND)

        players[ctx.guild.id] = player
        try:
            ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect()
                                                                                           , self.bot.loop))
        except discord.errors.ClientException as e:
            print(e)
            return

        description = f'Playing **Page {page}.**\nReciter: **{readable_reciter}**.'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
                             f'https://www.searchtruth.org/quran/images2/large/page-{url_page}.jpeg')
        await ctx.send(embed=em)

    @commands.command()
    async def qstop(self, ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None:
            await voice_client.disconnect()
            await ctx.send(DISCONNECTED)
        else:
            await ctx.send(NOT_PLAYING)

    @commands.command()
    async def qlive(self, ctx, *, link: str = 'makkah'):

        if ctx.voice_client.is_playing():
            return await ctx.send(ALREADY_PLAYING)

        link = link.lower()

        if link == 'quran radio':
            player = await YTDLSource.from_url(self.quranradio_url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player)
            await ctx.send("Now playing **mp3quran.net radio** (الإذاعة العامة - اذاعة متنوعة لمختلف القراء).")

        elif link == 'makkah':
            player = await YTDLSource.from_url(self.makkah_url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player)
            await ctx.send("Now playing **Makkah Live** (قناة القرآن الكريم- بث مباشر).")

    @commands.command(name="qvolume")
    async def qvolume(self, ctx, volume: int):
        if not 0 <= volume <= 100:
            return await ctx.send(INVALID_VOLUME)
        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to **{volume}%**.")

    @qplay.before_invoke
    @qlive.before_invoke
    async def join_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")

    # Leave empty voice channels to conserve bandwidth.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is None:
            if len(before.channel.members) == 1 and self.bot.user in before.channel.members:
                voice_client = discord.utils.get(self.bot.voice_clients, guild=before.channel.guild)
                if voice_client is not None:
                    await voice_client.disconnect()


def setup(bot):
    bot.add_cog(Quran(bot))
