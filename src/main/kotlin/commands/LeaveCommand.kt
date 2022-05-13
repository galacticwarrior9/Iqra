package commands

import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import util.replyAndSend

class LeaveCommand : ListenerAdapter() {

    override fun onSlashCommandInteraction(event: SlashCommandInteractionEvent) {
        if (event.name != "leave") {
            return
        }

        val guildAudioManager = event.guild?.audioManager
            ?: return event.replyAndSend("I am not connected to a voice channel.", true)

        if (!guildAudioManager.isConnected) {
            return event.replyAndSend("I am not connected to a voice channel.", true)
        }

        guildAudioManager.closeAudioConnection()
        return event.replyAndSend(":white_check_mark: Successfully disconnected.")
    }

}