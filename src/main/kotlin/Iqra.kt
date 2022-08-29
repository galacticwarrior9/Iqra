import com.jagrosh.jdautilities.commons.waiter.EventWaiter
import com.sedmelluq.discord.lavaplayer.player.AudioPlayerManager
import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers
import commands.LeaveCommand
import commands.PlayCommand
import commands.RadioCommand
import commands.RecitersCommand
import listeners.VoiceChannelListener
import net.dv8tion.jda.api.JDA
import net.dv8tion.jda.api.interactions.commands.OptionType
import net.dv8tion.jda.api.interactions.commands.build.Commands
import net.dv8tion.jda.api.interactions.commands.build.OptionData
import net.dv8tion.jda.api.interactions.commands.build.SubcommandData
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class Iqra(private val bot: JDA) {
    companion object {
        val audioPlayerManager: AudioPlayerManager = DefaultAudioPlayerManager()
        val logger: Logger = LoggerFactory.getLogger(this::class.java)
    }

    fun start() {
        val waiter = EventWaiter()

        AudioSourceManagers.registerRemoteSources(audioPlayerManager);

        // Commands
        bot.addEventListener(waiter)
        bot.addEventListener(LeaveCommand())
        bot.addEventListener(RadioCommand())
        bot.addEventListener(RecitersCommand(waiter))
        bot.addEventListener(PlayCommand(logger))

        // Other listeners
        bot.addEventListener(VoiceChannelListener())

        val guild = bot.getGuildById(308241121165967362)!!

        guild.updateCommands().addCommands(
            Commands.slash("radio", "Stream Qur'an recitations in your voice channel."),
            Commands.slash("leave", "Instructs the bot to leave its voice channel."),
            Commands.slash("reciters", "Browse or search for reciters.")
                .addSubcommands(
                    SubcommandData("list", "List reciters.")
                        .addOptions(
                            OptionData(OptionType.STRING, "type", "Should we list reciters for per-surah recitations or per-ayah recitations?")
                                .addChoice("surah", "surah")
                                .addChoice("ayah", "ayah")
                        ),
                    SubcommandData("search", "Search reciters.")
                        .addOptions(
                            OptionData(OptionType.STRING, "type", "Should we search reciters for per-surah recitations or per-ayah recitations?")
                                .addChoice("surah", "surah")
                                .addChoice("ayah", "ayah"),
                            OptionData(OptionType.STRING, "name", "The name of the reciter.")
                        )
                ),
            Commands.slash("play", "Play selected portions of the Qur'an.")
                .addSubcommands(SubcommandData("surah", "Play a surah.")
                    .addOption(OptionType.INTEGER, "surah_num", "The order in which this surah appears in the Qur'an, e.g. 1 for al-Fatihah.")
                    .addOption(OptionType.STRING, "reciter_name", "The name of the reciter.", false))
        ).queue()
    }

}