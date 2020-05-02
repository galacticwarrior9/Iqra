import discord
import asyncio
import youtube_dl
import aiohttp
from discord.ext import commands

reciters = {
    'abdulbaset abdulsamad': 'abdulbaset_mujawwad',
    'sudais': 'abdurrahmaan_as-sudays',
    'adel kalbani': 'adel_kalbani',
    'abdur-rashid sufi': 'abdurrashid_sufi',
    'mishary al-afasy': 'mishaari_raashid_al_3afaasee',
    'muhammad al-minshawi': 'muhammad_siddeeq_al-minshaawee',
    'abu bakr al-shatri': 'abu_bakr_ash-shatri_tarawee7',
    'muhammad al-luhaidan': 'muhammad_alhaidan',
    'yasser al-dussary': 'yasser_ad-dussary',
    'saad al-ghamdi': 'sa3d_al-ghaamidi',
    'ahmed al-ajmy': 'ahmed_ibn_3ali_al-3ajamy',
    'maher al-muaiqly': 'maher_256',
    'abdullah basfar': 'abdullaah_basfar',
    'ali al-hudhaify': 'huthayfi',
    'saud al-shuraym': 'sa3ood_al-shuraym',
    'muhammad jibreel': 'muhammad_jibreel',
    'hani al-rifai': 'rifai',
    'ibrahim al-jibrin': 'jibreen',
    'idris akbar': 'idrees_akbar',
    'salah bukhatir': 'salaah_bukhaatir',
    'mahmoud khalil al-hussary': 'mahmood_khaleel_al-husaree_iza3a',
    'nasser al-qatami': 'nasser_bin_ali_alqatami',
    'aziz alili': 'aziz_alili',
    'fares abbad': 'fares',
    'abdullah awad al-juhani': 'abdullaah_3awwaad_al-juhaynee',
    'muhammad al-mehysni': 'mehysni',
    'muhammad sulayman patel': 'muhammad_patel',
    'abdullah matroud': 'abdullah_matroud',
    'abdullah jabir': 'abdullaah_alee_jaabir',
    'nabil al-rifai': 'nabil_rifa3i',
    'abdulbari al-thubaity': 'thubaity',
    'khalid al-qahtani': 'khaalid_al-qahtaanee',
    'wadee hammadi al-yamani': 'wadee_hammadi_al-yamani',
    'tawfeeq al-sawaigh': 'tawfeeq_bin_saeed-as-sawaaigh',
    'mahmood ali al-bana': 'mahmood_ali_albana'
}

readable_reciters = {
    'abdulbaset abdulsamad': 'Abdul Baset Abdul Samad (Mujawwad)',
    'sudais': 'Abdur-Rahman as-Sudais',
    'adel kalbani': 'Adel Kalbani',
    'abdur-rashid sufi': 'Abdur-Rahman Sufi',
    'mishary al-afasy': 'Mishari Rashid al-`Afasy',
    'muhammad al-minshawi': 'Muhammad Siddiq al-Minshawi',
    'abu bakr al-shatri': 'Abu Bakr al-Shatri (Taraweeh)',
    'yasser al-dussary': 'Yasser al-Dussary',
    'saad al-ghamdi': "Sa'ad al-Ghamdi",
    'ahmed al-ajmy': 'Ahmed al-Ajmy',
    'maher al-muaiqly': 'Maher al-Muaiqly',
    'abdullah basfar': 'Abdullah Basfar',
    'ali al-hudhaify': 'Ali Abdur-Rahman al-Hudhaify (علي بن عبد الرحمن الحذيفي)',
    'saud al-shuraym': 'Sa`ud ash-Shuraym',
    'muhammad jibreel': 'Muhammad Jibreel',
    'hani al-rifai': 'Hani al-Rifai',
    'ibrahim al-jibrin': 'Ibarahim al-Jibrin',
    'idris akbar': 'Idris Akbar',
    'salah bukhatir': 'Salah Bukhatir',
    'mahmoud khalil al-hussary': 'Mahmoud Khalil al-Hussary',
    'nasser al-qatami': 'Nasser al-Qatami',
    'aziz alili': 'Aziz Alili',
    'fares abbad': 'Fares Abbad',
    'abdullah awad al-juhani': 'Abdullah Awad al-Juhani',
    'muhammad al-mehysni': 'Muhammad al-Mehysni',
    'muhammad sulayman patel': 'Muhammad Sulayman Patel',
    'abdullah matroud': 'Abdullah Matroud',
    'abdullah jabir': 'Abdullah Jabir (Taraweeh)',
    'nabil al-rifai': 'Nabil ar-Rifai',
    'abdulbari al-thubaity': 'Abdulbari ath-Thubaity',
    'khalid al-qahtani': 'Khalid al-Qahtani',
    'wadee hammadi al-yamani': 'Wadee Hammadi al-Yamani',
    'tawfeeq al-sawaigh': "Tawfeeq ibn Sa`id as-Sawa'igh",
    'mahmood ali al-bana': 'Mahmood Ali Al-Bana'
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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
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

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Quran(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.audio_url = 'https://download.quranicaudio.com/quran/{}/{}.mp3'
        self.audio_url_2 = 'https://download.quranicaudio.com/quran/{}/complete/{}.mp3'
        self.info_url = 'http://api.quran.com:3000/api/v3/chapters/{}'

    def make_url(self, surah , reciter, url_number):
        if 0 < surah < 10:
            url_surah = f'00{surah}'
        elif 10 <= surah < 100:
            url_surah = f'0{surah}'
        else:
            url_surah = f'{surah}'
        try:
            url_reciter = reciters[reciter]
        except KeyError:
            return None
        if url_number == 1:
            url = self.audio_url.format(url_reciter, url_surah)
        else:
            url = self.audio_url_2.format(url_reciter, url_surah)
        return url

    async def get_info(self, surah, reciter):
        async with self.session.get(self.info_url.format(surah)) as r:
            data = await r.json()

            name = data['chapter']['name_simple']
            arabic_name = data['chapter']['name_arabic']

        reciter = readable_reciters[reciter.lower()]

        return name, arabic_name, reciter

    @commands.command(name="playquran")
    async def playquran(self, ctx, surah: int, *, reciter: str = 'mishary al-afasy'):

        if not isinstance(surah, int):
            await ctx.send('Usage: `-playquran <surah number> <reciter>`\nExample: `-playquran 1 sudais`'
                           '\n\nType `-reciters` for a list of reciters.')

        reciter = reciter.lower()

        if reciter not in reciters:
            await ctx.voice_client.disconnect()
            return await ctx.send("Couldn't find reciter!")

        if surah < 0 or surah > 114:
            return await ctx.send("Sorry, that is not a valid surah.")

        url = self.make_url(surah, reciter, 1)

        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            url = self.make_url(surah, reciter, 2)
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            except:
                await ctx.voice_client.disconnect()
                return await ctx.send("Could not find a recitation for the surah by this reciter. Try a different surah"
                                      ".")

        players[ctx.guild.id] = player
        ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(),
                                                                                       self.bot.loop))

        transliterated_surah, arabic_surah, reciter = await self.get_info(surah, reciter)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}). \nReciter: **{reciter}**.'

        em = discord.Embed(title="Qurʼān", colour=0x006400, description=description)
        em.set_footer(text=f'Requested by {ctx.message.author}')
        await ctx.send(embed=em)

    @commands.command(name="stopquran")
    async def stopquran(self, ctx):
        voice_client = ctx.voice_client
        await voice_client.disconnect()
        await ctx.send("**Successfully disconnected.**")

    @playquran.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("**You are not connected to a voice channel.**")
        elif ctx.voice_client.is_playing():
            await ctx.send("**Already playing**. To stop playing, type `-stopquran`.")
            # ctx.voice_client.stop()

    @commands.command(name="reciters")
    async def reciters(self, ctx):
        reciter_list = ''
        for key in readable_reciters.keys():
            reciter_list = reciter_list + f'{key}, '

        await ctx.send(f'**Reciter List**\n```{reciter_list}```')

    @commands.command(name="qhelp")
    async def qhelp(self, ctx):
        em = discord.Embed(title='Help', colour=0x006400)
        em.add_field(name="-playquran", value="Plays a Qur'an recitation.\n\n`-playquran <surah number> <reciter>`"
                                              "\n\nExample: `-playquran 1 abu bakr al-shatri`", inline=True)
        em.add_field(name="-reciters", value="Shows the list of reciters for `-playquran`.", inline=True)
        em.add_field(name="-stopquran", value="Stops playing.", inline=True)
        em.set_footer(text="Support Server: https://discord.gg/Ud3MHJR")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Quran(bot))
