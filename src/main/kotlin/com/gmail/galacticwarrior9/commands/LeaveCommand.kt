package com.gmail.galacticwarrior9.commands

import com.gmail.galacticwarrior9.audioplayer.AudioManager
import com.gmail.galacticwarrior9.util.sendReply
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter

class LeaveCommand : ListenerAdapter() {

    override fun onSlashCommandInteraction(event: SlashCommandInteractionEvent) {
        if (event.name != "leave" || event.guild == null) {
            return
        }

        val audioManager = event.guild?.audioManager
            ?: return event.sendReply("I am not connected to a voice channel.", true)

        if (!audioManager.isConnected) {
            return event.sendReply("I am not connected to a voice channel.", true)
        }

        audioManager.closeAudioConnection()

        val guildAudioManager = AudioManager.getGuildHandler(event.guild!!)
        guildAudioManager.trackScheduler.clearQueue()

        return event.sendReply(":white_check_mark: Successfully disconnected.")
    }

}