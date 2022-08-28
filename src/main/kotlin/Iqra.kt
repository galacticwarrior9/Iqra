import com.jagrosh.jdautilities.commons.waiter.EventWaiter
import com.sedmelluq.discord.lavaplayer.player.AudioPlayerManager
import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers
import commands.LeaveCommand
import commands.RadioCommand
import commands.RecitersCommand
import dev.minn.jda.ktx.events.listener
import listeners.VoiceChannelListener
import net.dv8tion.jda.api.JDA
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.interactions.commands.build.Commands
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class Iqra(private val bot: JDA) {
    companion object {
        val audioPlayerManager: AudioPlayerManager = DefaultAudioPlayerManager()
    }

    fun start() {
        val waiter = EventWaiter()
        val logger: Logger = LoggerFactory.getLogger(this::class.java)

        AudioSourceManagers.registerRemoteSources(audioPlayerManager);

        // Commands
        bot.addEventListener(waiter)
        bot.addEventListener(LeaveCommand())
        bot.addEventListener(RadioCommand())
        bot.addEventListener(RecitersCommand(waiter, logger))

        // Other listeners
        bot.addEventListener(VoiceChannelListener())

        val guild = bot.getGuildById(308241121165967362)!!
        guild.updateCommands().addCommands(
            Commands.slash("radio", "Stream Qur'an recitations in your voice channel."),
            Commands.slash("leave", "Instructs the bot to leave its voice channel."),
            Commands.slash("reciters", "Browse or search for reciters.")
        ).queue()
    }

}