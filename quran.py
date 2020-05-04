import discord
import asyncio
import youtube_dl
import aiohttp
from discord.ext import commands

RECITATION_NOT_FOUND = "**Could not find a recitation for the surah by this reciter.** Try a different surah."
RECITER_NOT_FOUND = "**Couldn't find reciter!** Type `-reciters` for a list of available reciters."
SURAH_NOT_FOUND = "**Sorry, that is not a valid surah.**"
PAGE_NOT_FOUND = "**Sorry, the page must be between 1 and 604.**"
DISCONNECTED = "**Successfully disconnected.**"
INVALID_VOLUME = "**The volume must be between 0 and 100.**"
INVALID_VERSE = "**Please provide a verse.** For example, 1:2 is Surah al-Fatiha, ayah 2."
NON_EXISTENT_VERSE = "**There are only {} verses in this surah.**"

quranicaudio_reciters = {
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
    'mahmood ali al-bana': 'mahmood_ali_albana',
    'muhammad ayyub': 'muhammad_ayyoob_hq',
    'sahl yasin': 'sahl_yaaseen',
    'hamad sinan': 'hamad_sinan',
    'salah al-budair': 'salahbudair',
    'hatem farid': 'hatem_farid',
}

everyayah_reciters = {
    'sudais': 'Abdurrahmaan_As-Sudais_192kbps',
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

readable_reciters = {
    'abdulbaset abdulsamad': 'Abdul Baset Abdul Samad',
    'sudais': 'Abdur-Rahman as-Sudais',
    'adel kalbani': 'Adel Kalbani',
    'abdur-rashid sufi': 'Abdur-Rahman Sufi',
    'mishary al-afasy': 'Mishari Rashid al-`Afasy',
    'muhammad al-minshawi': 'Muhammad Siddiq al-Minshawi',
    'abu bakr al-shatri': 'Abu Bakr al-Shatri',
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
    'mahmood ali al-bana': 'Mahmood Ali Al-Bana',
    'muhammad ayyub': 'Muhammad Ayyub (Taraweeh)',
    'sahl yasin': 'Sahl Yaseen',
    'hamad sinan': 'Hamad Sinan',
    'salah al-budair': 'Salah al-Budair',
    'hatem farid': 'Hatem Farid',
    'muhsin al-qasim': 'Muhsin al-Qasim',
    'muhammad al-tablawi': 'Muhammad al-Tablawi'
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
        self.audio_url_3 = 'https://download.quranicaudio.com/quran/{}/collection/{}.mp3'
        self.info_url = 'http://api.quran.com:3000/api/v3/chapters/{}'
        self.live_url = 'http://66.226.10.51:8000/SaudiTVArabic?dl=1'
        self.page_url = 'https://everyayah.com/data/{}/PageMp3s/Page{}.mp3'
        self.ayah_url = 'https://everyayah.com/data/{}/{}.mp3'
        self.mushaf_url = 'https://www.searchtruth.org/quran/images1/{}.jpg'

    def make_url(self, surah, reciter, url_number):
        if 0 < surah < 10:          url_surah = f'00{surah}'
        elif 10 <= surah < 100:     url_surah = f'0{surah}'
        else:                       url_surah = f'{surah}'

        try: url_reciter = quranicaudio_reciters[reciter]
        except KeyError: return None

        if url_number == 1: url =   self.audio_url.format(url_reciter, url_surah)
        elif url_number == 2: url = self.audio_url_2.format(url_reciter, url_surah)
        else: url =                 self.audio_url_3.format(url_reciter, url_surah)

        return url

    def make_ayah_url(self, surah, ayah, reciter):
        if 0 < surah < 10:          url_surah = f'00{surah}'
        elif 10 <= surah < 100:     url_surah = f'0{surah}'
        else:                       url_surah = f'{surah}'

        if 0 < ayah < 10:           url_ayah = f'00{ayah}'
        elif 10 <= ayah < 100:      url_ayah = f'0{ayah}'
        else:                       url_ayah = f'{ayah}'

        try: url_reciter = everyayah_reciters[reciter]
        except KeyError: return None

        url_ref = f'{url_surah}{url_ayah}'
        url = self.ayah_url.format(url_reciter, url_ref)

        return url

    def make_page_url(self, page, reciter):
        if 0 < page < 10:          url_page = f'00{page}'
        elif 10 <= page < 100:     url_page = f'0{page}'
        else:                      url_page = f'{page}'

        try: url_reciter = everyayah_reciters[reciter]
        except KeyError: return None

        url = self.page_url.format(url_reciter, url_page)

        return url, url_page

    async def get_info(self, surah, reciter):
        async with self.session.get(self.info_url.format(surah)) as r:
            data = await r.json()

            name = data['chapter']['name_simple']
            arabic_name = data['chapter']['name_arabic']

        reciter = readable_reciters[reciter.lower()]

        return name, arabic_name, reciter

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

    @commands.command(name="qplay")
    async def qplay(self, ctx, surah: int, *, reciter: str = 'mishary al-afasy'):
        if not isinstance(surah, int):
            await ctx.send('Usage: `-qplay <surah number> <reciter>`\nExample: `-qplay 1 sudais`'
                           '\n\nType `-reciters` for a list of reciters.')

        reciter = reciter.lower()

        if reciter not in quranicaudio_reciters:
            await ctx.voice_client.disconnect()
            return await ctx.send(RECITER_NOT_FOUND)

        if not 0 < surah <= 114:
            return await ctx.send(SURAH_NOT_FOUND)

        url = self.make_url(surah, reciter, 1)

        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            try:
                url = self.make_url(surah, reciter, 2)
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            except:
                try:
                    url = self.make_url(surah, reciter, 3)
                    player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                except:
                    await ctx.voice_client.disconnect()
                    return await ctx.send(RECITATION_NOT_FOUND)

        players[ctx.guild.id] = player
        ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(),
                                                                                       self.bot.loop))

        transliterated_surah, arabic_surah, reciter = await self.get_info(surah, reciter)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}). \nReciter: **{reciter}**.'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x006400)
        await ctx.send(embed=em)

    @commands.command(name="qayah")
    async def qayah(self, ctx, ref: str, *, reciter: str = 'mishary al-afasy'):
        try:
            surah, ayah = ref.split(':')
            surah = int(surah)
            ayah = int(ayah)

        except:
            await ctx.voice_client.disconnect()
            return await ctx.send("Invalid arguments. Commands: `-qayah <surah>:<ayah> <reciter>`."
                                  "\n\nExample: `-qayah 2:255 sudais`.")

        reciter = reciter.lower()

        if reciter not in everyayah_reciters:
            await ctx.voice_client.disconnect()
            return await ctx.send(RECITER_NOT_FOUND)

        if not 0 < surah <= 114:
            await ctx.voice_client.disconnect()
            return await ctx.send(SURAH_NOT_FOUND)

        verse_count = await self.get_verse_count(surah)
        if ayah > verse_count:
            await ctx.voice_client.disconnect()
            return await ctx.send(NON_EXISTENT_VERSE.format(verse_count))

        url = self.make_ayah_url(surah, ayah, reciter)
        print(url)
        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            await ctx.voice_client.disconnect()
            return await ctx.send(RECITATION_NOT_FOUND)

        players[ctx.guild.id] = player
        ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(),
                                                                                       self.bot.loop))

        transliterated_surah, arabic_surah, reciter = await self.get_info(surah, reciter)
        description = f'Playing **Surah {transliterated_surah}** ({arabic_surah}), Ayah {ayah}. ' \
                      f'\nReciter: **{reciter}**.'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x36393F, f'https://everyayah.com/data/QuranText_jpg/{surah}_{ayah}.jpg')
        await ctx.send(embed=em)

    @commands.command(name="qpage")
    async def qpage(self, ctx, page: int, *, reciter: str = 'mishary al-afasy'):

        try:
            page = int(page)
        except:
            await ctx.voice_client.disconnect()
            return await ctx.send("Invalid arguments. Commands: `-qpage <page>:<ayah> <reciter>`."
                                  "\n\nExample: `-qayah 604 sudais`.")

        reciter = reciter.lower()
        readable_reciter = readable_reciters[reciter.lower()]

        if reciter not in everyayah_reciters:
            await ctx.voice_client.disconnect()
            return await ctx.send(RECITER_NOT_FOUND)

        if not 0 < page <= 604:
            await ctx.voice_client.disconnect()
            return await ctx.send(PAGE_NOT_FOUND)

        url, url_page = self.make_page_url(page, reciter)

        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        except:
            await ctx.voice_client.disconnect()
            return await ctx.send(RECITATION_NOT_FOUND)

        players[ctx.guild.id] = player
        ctx.voice_client.play(player, after=lambda x: asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(),
                                                                                       self.bot.loop))

        description = f'Playing **Page {page}.**\nReciter: **{readable_reciter}**.'

        em = self.make_embed("Qurʼān", description, f'Requested by {ctx.message.author}', 0x36393F,
                             f'https://www.searchtruth.org/quran/images2/large/page-{url_page}.jpeg')
        await ctx.send(embed=em)

    @commands.command(name="qstop")
    async def qstop(self, ctx):
        voice_client = ctx.voice_client
        await voice_client.disconnect()
        await ctx.send(DISCONNECTED)

    @commands.command(name="qlive")
    async def qlive(self, ctx):
        player = await YTDLSource.from_url(self.live_url, loop=self.bot.loop, stream=True)
        ctx.voice_client.play(player)

        await ctx.send("Now playing **Makkah Live** (قناة القرآن الكريم- بث مباشر).")

    @commands.command(name="qvolume")
    async def qvolume(self, ctx, volume: int):
        if not isinstance(volume, int) or not 0 <= volume <= 100:
            await ctx.send(INVALID_VOLUME)
        player = players[ctx.guild.id]
        player.volume = int
        await ctx.send(f"Successfully changed volume to {volume}")

    @commands.command(name="reciters")
    async def reciters(self, ctx):
        main_reciter_list = ''
        secondary_reciter_list = ''
        for key in readable_reciters.keys():
            if key in everyayah_reciters.keys():
                secondary_reciter_list = secondary_reciter_list + f'{key}, '
            if key in quranicaudio_reciters.keys():
                main_reciter_list = main_reciter_list + f'{key}, '

        await ctx.send(f'**`-qplay` Reciter List**\n\n```fix\n{main_reciter_list}```\n\n**`-qayah` and `-qpage` Reciter'
                       f' List**\n\n```{secondary_reciter_list}```')

    @commands.command(name="qhelp")
    async def qhelp(self, ctx):
        em = discord.Embed(title='Help', colour=0x006400)
        em.add_field(name="-qplay", value="Plays a recitation of a surah.\n\n`-qplay <surah number> <reciter>`"
                                          "\n\nExample: `-qplay 1 abu bakr al-shatri`", inline=True)
        em.add_field(name="-qayah", value="Plays a recitation of a single verse.\n\n`-qplay <surah>:<ayah>`"
                                          "\n\nExample: `-qayah 2:255 hatem farid`", inline=True)
        em.add_field(name="-qpage", value="Plays a recitation of a page from the mushaf.\n\n`-qpage <page> "
                                          "<reciter>`\n\nExample: `-qpage 60 sudais`", inline=True)
        em.add_field(name="-reciters", value="Shows the list of reciters.", inline=True)
        em.add_field(name="-qlive", value="Plays a live audio stream from al-Masjid al-Ḥarām in Makkah.", inline=True)
        em.add_field(name="-qstop", value="Stops playing.", inline=True)
        em.add_field(name="-qvolume", value="Changes the audio volume. The volume must be between 1 and "
                                            "100.\n\n`-qvolume <volume>`\n\nExample: `-qvolume 100`", inline=True)
        em.add_field(name="Information", value="• [GitHub](https://github.com/galacticwarrior9/QuranBot)"
                                               "\n• [Support Server](https://discord.gg/Ud3MHJR)", inline=True)
        await ctx.send(embed=em)

    @qplay.before_invoke
    @qayah.before_invoke
    @qlive.before_invoke
    @qpage.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("**You are not connected to a voice channel.**")
        elif ctx.voice_client.is_playing():
            await ctx.send("**Already playing**. To stop playing, type `-qstop`.")

    @qvolume.before_invoke
    async def ensure_volume(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.send("**Nothing is being played.**")
            else:
                await ctx.send("**You are not connected to a voice channel.**")
        elif not ctx.voice_client.is_playing():
            await ctx.send("**Nothing is being played.**")

    # Leave empty voice channels.
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is None:
            if len(before.channel.members) == 1 and self.bot.user in before.channel.members:
                voice_client = discord.utils.get(self.bot.voice_clients, guild=before.channel.guild)
                await voice_client.disconnect()


def setup(bot):
    bot.add_cog(Quran(bot))
