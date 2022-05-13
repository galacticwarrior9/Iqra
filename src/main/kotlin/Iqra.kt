import com.sedmelluq.discord.lavaplayer.player.AudioPlayerManager
import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers
import commands.LeaveCommand
import commands.RadioCommand
import listeners.VoiceChannelListener
import net.dv8tion.jda.api.JDA
import net.dv8tion.jda.api.interactions.commands.build.Commands
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class Iqra(private val bot: JDA) {
    companion object {
        val audioPlayerManager: AudioPlayerManager = DefaultAudioPlayerManager()
        val logger: Logger = LoggerFactory.getLogger(this::class.java)
    }

    fun start() {
        AudioSourceManagers.registerRemoteSources(audioPlayerManager);

        bot.addEventListener(LeaveCommand())
        bot.addEventListener(RadioCommand())

        bot.addEventListener(VoiceChannelListener())

        val guild = bot.getGuildById(308241121165967362)!!
        guild.updateCommands().addCommands(
            Commands.slash("radio", "Play a Qur'an recitation stream."),
            Commands.slash("leave", "Instructs the bot to leave the voice channel it is in.")
        ).queue()
    }

}