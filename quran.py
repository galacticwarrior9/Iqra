import discord
import asyncio
import youtube_dl
import aiohttp
from discord.ext import commands
from fuzzywuzzy import process

RECITATION_NOT_FOUND = "**Could not find a recitation for the surah by this reciter.** Try a different surah."
RECITER_NOT_FOUND = "**Couldn't find reciter!** Type `-reciters` for a list of available reciters."
SURAH_NOT_FOUND = "**Sorry, that is not a valid surah.**"
PAGE_NOT_FOUND = "**Sorry, the page must be between 1 and 604.**"
DISCONNECTED = "**Successfully disconnected.**"
INVALID_VOLUME = "**The volume must be between 0 and 100.**"
INVALID_VERSE = "**Please provide a verse.** For example, 1:2 is Surah al-Fatiha, ayah 2."
NON_EXISTENT_VERSE = "**There are only {} verses in this surah.**"

mp3quran_reciters = {
    'abdelbari al-toubayti': 0,
    'abdulaziz al-ahmad': 1,
    'abdulaziz al-asiri': 2,
    'abdulaziz al-zahrani': 3,
    'abdulbari muhammad': 4,
    'abdulbasit abdulsamad': 6,
    'abdulhadi kanakeri': 10,
    'abdullah al-juhany': 12,
    'abdullah al-kandari': 13,
    'abdullah al-khalaf': 14,
    'abdullah al-matroud': 15,
    'abdullah basfar': 18,
    'abdullah khayat': 20,
    'abdullah qaulan': 21,
    'abdul muhsin al-qasim': 23,
    'abdul muhsin al-harthy': 25,
    'abdul muhsin al-obaikan': 26,
    'abdul rahman al-majed': 27,
    'abdul rahman alusi': 28,
    'abdul rahman al-sudais': 29,
    'abdul rashid sufi': 30,
    'abdul wadud haneef': 33,
    'abu bakr al-shatri': 185,
    'addokali muhammad al-alim': 35,
    'adel al-kalbani': 36,
    'adel rayan': 37,
    'ahmad al-ajmy': 39,
    'ahmad al-hawashi': 40,
    'ahmad khader al-tarabulsi': 42,
    'ahmad nauina': 43,
    'ahmad saber': 44,
    'ahmad al-suwailem': 46,
    'ahmad al-amer': 48,
    'akram al-alaqmi': 50,
    'al-qaria yaseen': 51,
    'al-ashri omran': 52,
    'alfateh alzubair': 53,
    'ali al-hudhaify': 56,
    'ali hajjaj al-souissi': 58,
    'ali jaber': 76,
    'aloyoon al-koshi': 60,
    'alzain muhammad ahmad': 61,
    'badr al-turki': 62,
    'bandar baleela': 63,
    'emad hafez': 65,
    'fares abbad': 68,
    'hani al-rifai': 71,
    'hatem farid': 72,
    'ibrahim al-akhdar': 77,
    'ibrahim al-jibreen': 79,
    'ibrahim al-dossary': 80,
    'ibrahim al-jormy': 82,
    'idris akbar': 83,
    'jamaan alosaimi': 85,
    'jamal shaker abdullah': 87,
    'khalid al-qahtani': 88,
    'khalid abdulkafi': 89,
    'khalid al-jileel': 90,
    'khalid al-mohana': 94,
    'khalifa al-tunaiji': 96,
    'maher al-muaiqly': 99,
    'maher shakhashero': 100,
    'mahmoud al-rifai': 101,
    'mahmoud al-sheimy': 102,
    'mahmoud ali al-banna': 103,
    'mahmoud khalil al-hussary': 107,
    'mishary al-afasy': 113,
    'moeedh al-harthi': 114,
    'muhammad abdulkarem': 116,
    'muhammad al-abdullah': 117,
    'muhammad al-airawy': 119,
    'muhammad al-tablawi': 120,
    'muhammad al-bukheet': 121,
    'muhammad al-monshed': 122,
    'muhammad rashad al-shareef': 124,
    'muhammad saleh alim shah': 126,
    'muhammad al-luhaidan': 128,
    'muhammad al-muhasny': 129,
    'muhammad ayyub': 130,
    'muhammad jibreel': 132,
    'muhammad osman khan': 133,
    'muhammad siddiq al-minshawi': 136,
    'mousa bilal': 137,
    'muftah al-saltany': 139,
    'mustafa al-lahoni': 146,
    'mustafa ismail': 147,
    'mustafa raad al-azawi': 148,
    'nabil al-rifai': 149,
    'nasser al-obaid': 150,
    'nasser al-majed': 151,
    'nasser alosfor': 152,
    'nasser al-qatami': 153,
    'neamah al-hassan': 154,
    'omar al-qazabri': 156,
    'othman al-ansary': 157,
    'raad al-kurdi': 158,
    'rachid belalya': 159,
    'rami aldeais': 162,
    'saad al-ghamdi': 166,
    'saad almqren': 167,
    'saber abdul hakim': 168,
    'sahl yasin': 169,
    'salah al-budair': 171,
    'salah al-hasim': 172,
    'salah al-sahood': 177,
    'saud al-shuraym': 182,
    'sayeed ramadan': 183,
    'shirazad taher': 186,
    'salah bukhatir': 187,
    'tareq abdulgani daawob': 188,
    'tawfeeq al-sayegh': 189,
    'wadeea al-yamani': 191,
    'waleed alnaehi': 192,
    'yahya hawwa': 196,
    'yasser al-dossary': 197,
    'yasser al-faylakawi': 198,
    'yasser al-mazroyee': 199,
    'yasser al-qurashi': 200,
    'yasser salamah': 201,
    'yousef alshoaey': 202,
    'yousef bin noah ahmad': 203,
    'zaki daghistani': 206
}

everyayah_reciters = {
    'abdulrahman al-sudais': 'Abdurrahmaan_As-Sudais_192kbps',
    'mishary al-afasy': 'Alafasy_128kbps',
    'abdullah basfar': 'Abdullah_Basfar_192kbps',
    'abu bakr al-shatri': 'Abu_Bakr_Ash-Shaatree_128kbps',
    'abdulbaset abdulsamad': 'Abdul_Basit_Murattal_192kbps',
    'ahmed al-ajmy': 'Ahmed_ibn_Ali_al-Ajamy_128kbps_ketaballah.net',
    'hani al-rifai': 'Hani_Rifai_192kbps',
    'ali al-hudhaify': 'Hudhaify_128kbps',
    'maher al-muaiqly': 'MaherAlMuaiqly128kbps',
    'muhammad al-minshawi': 'Minshawy_Mujawwad_192kbps',
    'muhammad jibreel': 'Muhammad_Jibreel_128kbps',
    'muhsin al-qasim': 'Muhsin_Al_Qasim_192kbps',
    'muhammad ayyub': 'Muhammad_Ayyoub_128kbps',
    'saud al-shuraym': 'Saood_ash-Shuraym_128kbps',
    'abdullah matroud': 'Abdullah_Matroud_128kbps',
    'mahmoud khalil al-hussary': 'Husary_128kbps',
    'muhammad al-tablawi': 'Mohammad_al_Tablaway_128kbps'
}

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

    async def get_qplay_meta(self, reciter):
        async with self.session.get(self.reciter_info_url) as r:
            data = await r.json()

            index_url = data['reciters'][reciter]['Server']
            riwayah = data['reciters'][reciter]['rewaya']

        return index_url, riwayah

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
            await ctx.send('**Invalid arguments**. For help, type `-qhelp qplay`.')

    @qplay.command()
    async def surah(self, ctx, surah: int, *, reciter: str = 'mishary al-afasy'):
        if not isinstance(surah, int):
            return await ctx.send('Usage: `-qplay surah <surah number> <reciter>`\nExample: `-qplay surah 1 abdul '
                                  'rahman al-sudais`\n\nType `-reciters` for a list of reciters.')

        reciter = reciter.lower()

        if reciter not in mp3quran_reciters.keys():
            return await ctx.send(RECITER_NOT_FOUND)

        if not 0 < surah <= 114:
            return await ctx.send(SURAH_NOT_FOUND)

        reciter_name = reciter.replace('-', ' - ').title().replace(' - ', '-')
        reciter = mp3quran_reciters[reciter]

        index_url, riwayah = await self.get_qplay_meta(reciter)
        file_url = self.get_qplay_file(index_url, surah)

        try:
            player = await YTDLSource.from_url(file_url, loop=self.bot.loop, stream=True)
        except: return await ctx.send(RECITATION_NOT_FOUND)

        players[ctx.guild.id] = player

        try:
            await ctx.author.voice.channel.connect()
            ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect()
                                  , self.bot.loop))
        except discord.errors.ClientException: return

        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}).\nReciter: **{reciter_name}**.' \
                      f'\nRiwayah: {riwayah}'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400)
        await ctx.send(embed=em)

    @qplay.command()
    async def ayah(self, ctx, ref: str, *, reciter: str = 'mishary al-afasy'):
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
            await ctx.author.voice.channel.connect()
            ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect()
                                                                                           , self.bot.loop))
        except discord.errors.ClientException:
            return

        reciter = reciter.replace('-', ' - ').title().replace(' - ', '-')
        transliterated_surah, arabic_surah = await self.get_surah_info(surah)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}), Ayah {ayah}. ' \
                      f'\nReciter: **{reciter}**.'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
                             f'https://everyayah.com/data/QuranText_jpg/{surah}_{ayah}.jpg')
        await ctx.send(embed=em)

    @qplay.command()
    async def page(self, ctx, page: int, *, reciter: str = 'mishary al-afasy'):

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
            await ctx.author.voice.channel.connect()
            ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect()
                                                                                           , self.bot.loop))
        except discord.errors.ClientException:
            return

        description = f'Playing **Page {page}.**\nReciter: **{readable_reciter}**.'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400,
                             f'https://www.searchtruth.org/quran/images2/large/page-{url_page}.jpeg')
        await ctx.send(embed=em)

    @commands.command(name="qstop")
    async def qstop(self, ctx):
        voice_client = ctx.voice_client
        await voice_client.disconnect()
        await ctx.send(DISCONNECTED)

    @commands.command(name="qlive")
    async def qlive(self, ctx, *, link: str = 'makkah'):
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

    @commands.command(name="qsearch")
    async def qsearch(self, ctx, search_term: str):
        reciters = mp3quran_reciters.keys()
        results = process.extractWithoutOrder(search_term, reciters, score_cutoff=65)
        formatted_results = ''
        i = 0
        for result in results:
            i += 1
            formatted_result = result[0].replace('-', ' - ').title().replace(' - ', '-')
            formatted_results = formatted_results + f'\n{i}. {formatted_result}'
        if formatted_results == '':
            await ctx.send('**No results.**')
        else:
            em = self.make_embed(title='Search Results', description=formatted_results, colour=0x006400, footer='',
                                 image=None)
            await ctx.send(embed=em)

    @commands.command(name="reciters")
    async def reciters(self, ctx):
        everyayah_reciter_list = ''
        for key in everyayah_reciters.keys():
            everyayah_reciter_list = everyayah_reciter_list + f'{key}, '
        em = discord.Embed(description='\n\n__**Surah Reciters**__\n\nAvailable reciters: '
                                       f'**{len(mp3quran_reciters.keys())}\n\n'
                                       f'[Full surah reciter list](https://github.com/galacticwarrior9/QuranBot/blob/ma'
                                       f'ster/Reciters.md)'
                                       f'**\n\nTo search this list, type `-qsearch <reciter name>`, e.g. '
                                       f'`-qsearch dossary`\n'
                                       f'\n\n__**Ayah and Page Reciters**__'
                                       f'\n\nAvailable reciters: **{len(everyayah_reciters.keys())}**\n\n'
                                       f'List: ```{everyayah_reciter_list}```', colour=0x006400, title="Reciters")
        await ctx.send(embed=em)

    @qplay.before_invoke
    @qlive.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if not ctx.author.voice:
                await ctx.send("**You are not connected to a voice channel.**")
        elif ctx.voice_client.is_playing():
            await ctx.send("**Already playing**. To stop playing, type `-qstop`.")

    # Leave empty voice channels.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is None:
            if len(before.channel.members) == 1 and self.bot.user in before.channel.members:
                voice_client = discord.utils.get(self.bot.voice_clients, guild=before.channel.guild)
                await voice_client.disconnect()


def setup(bot):
    bot.add_cog(Quran(bot))
