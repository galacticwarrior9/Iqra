import aiohttp
import asyncio
import discord
import math
from discord.ext import commands
from fuzzywuzzy import process

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


async def get_reciter_data(for_type: str = 'surah'):
    if for_type == 'ayah':
        url = 'https://api.mp3quran.net/verse/verse_en.json'
    else:
        url = 'http://mp3quran.net/api/_english.php'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            try:
                data = await r.json()
            # If the JSON response is malformed - which occasionally occurs - then we select HTML as the content type.
            except aiohttp.ContentTypeError:
                data = await r.json(content_type='text/html')
    return data


async def get_surah_reciters():
    """
    Creates a list of reciter objects using mp3quran.net's API.
    We fetch the list anew every time because the API is occasionally updated with new reciters and information.
    """
    data = await get_reciter_data()
    raw_reciters = data['reciters']

    # Filter out reciters with recitations of < 90 surahs.
    raw_reciters = [reciter for reciter in raw_reciters if int(reciter['count']) >= 90]

    # Create reciter object from each reciter and add it to the reciters list
    reciters = []
    for reciter in raw_reciters:
        name = reciter['name']
        riwayah = reciter['rewaya']
        server = reciter['Server']

        # Avoid duplicate names by renaming reciters to reflect differences in riwayat
        for test_obj in reciters:
            if name == test_obj.name:
                name = f'{name} - {riwayah}'

        reciter_obj = Reciter(name, riwayah)
        reciter_obj.server = server

        reciters.append(reciter_obj)

    return reciters


async def get_surah_reciter(name):
    reciter_list = await get_surah_reciters()
    for reciter in reciter_list:
        if reciter.name.lower() == name:
            return reciter
    return None


async def get_ayah_reciters():
    data = await get_reciter_data('ayah')
    raw_reciters = data['reciters_verse']

    # Only get reciters whose recitations are available in 128kbps.
    raw_reciters = [reciter for reciter in raw_reciters if reciter['audio_url_bit_rate_128'] != '']

    # Create reciter object from each reciter and add it to the reciters list
    reciters = []
    for reciter in raw_reciters:
        name = reciter['name']
        riwayah = reciter['rewaya']
        mushaf_type = reciter['musshaf_type']
        ayah_url = reciter['audio_url_bit_rate_128']

        # Avoid duplicate names by renaming reciters to reflect differences in recitation style
        for test_obj in reciters:
            if name == test_obj.name:
                name = f'{name} - {mushaf_type}'

        reciter_obj = Reciter(name, riwayah)
        reciter_obj.mushaf_type = mushaf_type
        reciter_obj.ayah_url = ayah_url
        reciters.append(reciter_obj)

    return reciters


async def get_ayah_reciter(name):
    reciter_list = await get_ayah_reciters()
    for reciter in reciter_list:
        if reciter.name.lower() == name:
            return reciter
    return None


class Reciter:
    def __init__(self, name, riwayah):
        self.name = name
        self.riwayah = riwayah


class Page:
    def __init__(self, num, reciters):
        self.name = num
        self.reciters = reciters


class Reciters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def qsearch(self, ctx, search_term: str):
        """
        Use fuzzy search to allow users to search the mp3quran.net reciter list.
        """
        reciter_list = await get_surah_reciters()
        reciters = [reciter.name for reciter in reciter_list]

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
            em = discord.Embed(title='Search Results', colour=0x006400, description=formatted_results)
            await ctx.send(embed=em)

    @commands.group()
    async def reciters(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="Reciters", color=0x006400)
            embed.description = "Please specify a reciter list: *surah*, *ayah* or *page*.\n\n**Example**: `-reciters" \
                                " surah`"
            await ctx.send(embed=embed)

    @reciters.command()
    async def ayah(self, ctx):
        reciter_list = await get_ayah_reciters()
        await self.create_reciters_message(ctx, reciter_list)

    @reciters.command()
    async def surah(self, ctx):
        reciter_list = await get_surah_reciters()
        await self.create_reciters_message(ctx, reciter_list)

    @reciters.command()
    async def page(self, ctx):
        reciter_list = list(everyayah_reciters.keys())
        await self.create_reciters_message(ctx, reciter_list)

    @staticmethod
    def list_reciters(page):
        lst = ''
        for reciter in page.reciters:
            try:
                lst = lst + f'• {reciter.name}\n'
            except AttributeError:  # For -reciters page
                lst = lst + f'• {reciter.title()}\n'
        return lst

    async def create_reciters_message(self, ctx, reciter_list):
        num_pages = int(math.ceil(len(reciter_list) / 10))
        pages = []
        i = 0
        for page_num in range(0, num_pages):
            reciters = reciter_list[i:i + 10]
            page = Page(page_num, reciters)
            pages.append(page)
            i += 10

        page_num = 1
        page = pages[page_num - 1]
        lst = self.list_reciters(page)

        embed = discord.Embed(title="Reciters", color=0x006400, description=lst)
        embed.set_footer(text=f'Page 1/{len(pages)}')

        msg = await ctx.send(embed=embed)
        await msg.add_reaction(emoji='⬅')
        await msg.add_reaction(emoji='➡')

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=120, check=lambda reaction, user:
                (reaction.emoji == '➡' or reaction.emoji == '⬅')
                and user != self.bot.user
                and reaction.message.id == msg.id)

            except asyncio.TimeoutError:
                await msg.remove_reaction(emoji='➡', member=self.bot.user)
                await msg.remove_reaction(emoji='⬅', member=self.bot.user)
                break

            if reaction.emoji == '➡':
                page_num += 1
                if page_num > num_pages:
                    page_num = 1
                page = pages[page_num - 1]

            if reaction.emoji == '⬅':
                page_num -= 1
                if page_num < 1:
                    page_num = num_pages
                page = pages[page_num - 1]

            lst = self.list_reciters(page)
            embed = discord.Embed(title="Reciters", color=0x006400, description=lst)
            embed.set_footer(text=f'Page {page_num}/{num_pages}')
            await msg.edit(embed=embed)

            try:
                await msg.remove_reaction(reaction.emoji, user)
            except:
                pass


def setup(bot):
    bot.add_cog(Reciters(bot))
