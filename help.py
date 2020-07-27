import discord
from discord.ext import commands

ICON = 'https://cdn.discordapp.com/app-icons/706134327200841870/e6bb860daa7702ea70e6d6e29c3d36f6.png'


class Help(commands.Cog):

    @commands.command(name="qhelp")
    async def qhelp(self, ctx, command: str = None):

        em = discord.Embed(colour=0x006400)
        em.set_thumbnail(url=ICON)

        if command is None:

            em.set_author(name='Iqra Help')
            em.add_field(value="**Use `-qhelp <command>` for more information about a command.** Example: "
                               "`-qhelp qplay`\n\n"
                               "• `-qplay` - plays the recitation of a surah, ayah or mushaf page.\n"
                               "• `-qlive` - plays live audio either from Makkah or online Qur'an radio.\n"
                               "• `-reciters` - lists the reciters that can be used with `-qplay`.\n"
                               "• `-qsearch` - search the reciter list for `-qplay`\n"
                               "• `-qstop` - disconnects the bot from voice chat.\n"
                               "• `-qpause` - pauses the bot.\n"
                               "• `-qresume` - resumes the bot.\n"
                               "• `-qvolume` - changes the volume of the bot.", name='Overview')
            em.add_field(name="Links", value="• [GitHub](https://github.com/galacticwarrior9/QuranBot)\n"
                                             "• [Support Server](https://discord.gg/Ud3MHJR)", inline=False)

        if command == "qplay":
            em.set_author(name='-qplay')
            em.add_field(value="**-qplay** plays a surah, ayah or page from the mushaf in a voice channel."
                               , name='Description', inline=False)
            em.add_field(value="`-qplay surah <surah number> <reciter>`\n\nExample: `-qplay surah 1 Mishary Alafasi`"
                               "\n\n__**OR**__ `-qplay surah <surah name> <reciter>`\n\nExample: `-qplay surah al-fatiha"
                               " Mishary Alafasi`", name='Playing a surah', inline=True)
            em.add_field(value="`-qplay ayah <surah>:<ayah> <reciter>`\n\nExample: `-qplay ayah 1:6 hani al-rifai`"
                               , name='Playing an ayah', inline=True)
            em.add_field(value="`-qplay page <page number> <reciter>`\n\nExample: `-qplay page 342 hani al-rifai`"
                               , name='Playing a page from the mushaf', inline=True)
            em.add_field(value="Type `-reciters` for a list of reciters.", name='Reciters', inline=False)

        if command == "qvolume":
            em.set_author(name='-qvolume')
            em.add_field(value="**-qvolume** changes the volume of the bot.", name='Description', inline=True)
            em.add_field(value="`-qvolume <volume>`\n\n`<volume>` must be between 1 and 100.\n\nExample: `-qvolume 50`"
                               , name='Usage', inline=True)

        if command == "qsearch":
            em.set_author(name='-qsearch')
            em.add_field(value="**-qsearch** searches the list of surah reciters.", name='Description', inline=True)
            em.add_field(value="`-qsearch <reciter name>`\n\nExample: `-qsearch dossary`", name='Usage', inline=True)

        if command == "reciters":
            em.set_author(name='-reciters')
            em.add_field(value="**-reciters** sends the lists of reciters for `-qplay`.", name='Description',
                         inline=True)

        if command == "qlive":
            em.set_author(name='-qlive')
            em.add_field(value="**-qlive** streams live audio.", name='Description', inline=False)
            em.add_field(value="Type `-qlive Makkah` for a live audio stream from al-Masjid al-Ḥarām in Makkah.\n\n"
                               "Type `-qlive Quran Radio` for live Quran radio.", name='Usage', inline=False)

        if command == "qstop":
            em.set_author(name='-qstop')
            em.add_field(value="**-qstop** disconnects the bot from voice chat.", name='Description', inline=True)

        if command == "qresume":
            em.set_author(name='-qresume')
            em.add_field(value="**-qresume** resumes the bot if it is paused.", name='Description', inline=True)

        if command == "qpause":
            em.set_author(name='-qpause')
            em.add_field(value="**-qpause** pauses the bot if it is playing.", name='Description', inline=True)

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Help(bot))
