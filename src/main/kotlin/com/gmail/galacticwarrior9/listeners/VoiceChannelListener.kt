package com.gmail.galacticwarrior9.listeners

import com.gmail.galacticwarrior9.audioplayer.AudioManager
import net.dv8tion.jda.api.entities.AudioChannel
import net.dv8tion.jda.api.entities.Guild
import net.dv8tion.jda.api.events.guild.voice.GuildVoiceLeaveEvent
import net.dv8tion.jda.api.events.guild.voice.GuildVoiceMoveEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter

class VoiceChannelListener : ListenerAdapter() {

    override fun onGuildVoiceLeave(event: GuildVoiceLeaveEvent) {
        if (event.member === event.guild.selfMember) {
            return AudioManager.removeGuildHandler(event.guild)
        }
        processBotMove(event.guild, event.channelLeft, event.channelJoined)
    }

    override fun onGuildVoiceMove(event: GuildVoiceMoveEvent) {
        processBotMove(event.guild, event.channelLeft, event.channelJoined)
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