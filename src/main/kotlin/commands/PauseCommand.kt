package commands

import audioplayer.AudioManager
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import util.replySafely

class PauseCommand : ListenerAdapter() {

    override fun onSlashCommandInteraction(event: SlashCommandInteractionEvent) {
        if (event.name != "pause" || event.guild == null) {
            return
        }

        val guildAudioManager = AudioManager.getGuildHandler(event.guild!!)
        if (guildAudioManager.player.playingTrack !== null) {
            if (guildAudioManager.player.isPaused) {
                return event.replySafely("Playback is already paused.", true)
            }
            guildAudioManager.player.isPaused = true
            return event.replySafely(":pause_button: Playback has been paused.")
        } else {
            return event.replySafely("The bot is not playing.", true)
        }
    }

}