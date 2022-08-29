package commands

import audioplayer.AudioManager
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import util.replySafely

class ResumeCommand : ListenerAdapter() {

    override fun onSlashCommandInteraction(event: SlashCommandInteractionEvent) {
        if (event.name != "resume" || event.guild == null) {
            return
        }

        val guildAudioManager = AudioManager.getGuildHandler(event.guild!!)
        return if (guildAudioManager.player.playingTrack !== null) {
            if (!guildAudioManager.player.isPaused) {
                event.replySafely("Playback is not paused.", true)
            }
            guildAudioManager.player.isPaused = false
            event.replySafely(":arrow_forward: Playback has resumed.")
        } else {
            event.replySafely("The bot is not playing.", true)
        }
    }

}