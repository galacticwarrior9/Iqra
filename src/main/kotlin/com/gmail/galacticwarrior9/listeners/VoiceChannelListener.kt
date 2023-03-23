package com.gmail.galacticwarrior9.listeners

import com.gmail.galacticwarrior9.audioplayer.AudioManager
import net.dv8tion.jda.api.entities.Guild
import net.dv8tion.jda.api.entities.channel.middleman.AudioChannel
import net.dv8tion.jda.api.events.guild.voice.GuildVoiceUpdateEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter

class VoiceChannelListener : ListenerAdapter() {

    override fun onGuildVoiceUpdate(event: GuildVoiceUpdateEvent) {
        // Bot left voice chat - remove guild handler
        if (event.member === event.guild.selfMember && event.channelJoined == null) {
            return AudioManager.removeGuildHandler(event.guild)
        }

        // Someone has left a voice channel - check if the bot is now alone. If so, disconnect.
        if (event.channelLeft != null) {
            processBotMove(event.guild, event.channelLeft!!, event.channelJoined)
        }
    }

    private fun processBotMove(guild: Guild, channelLeft: AudioChannel, channelJoined: AudioChannel?) {
        val botChannel = guild.audioManager.connectedChannel ?: return

        if (botChannel === channelLeft && channelLeft.members.size == 1
            || botChannel === channelJoined && channelJoined.members.size == 1) {
            guild.audioManager.closeAudioConnection()
            AudioManager.removeGuildHandler(guild)
        }
    }
}