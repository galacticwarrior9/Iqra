package com.gmail.galacticwarrior9.listeners

import com.gmail.galacticwarrior9.audioplayer.AudioManager
import net.dv8tion.jda.api.entities.Guild
import net.dv8tion.jda.api.entities.channel.middleman.AudioChannel
import net.dv8tion.jda.api.events.guild.voice.GuildVoiceUpdateEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import net.jodah.expiringmap.ExpirationPolicy
import net.jodah.expiringmap.ExpiringMap
import java.util.concurrent.TimeUnit

class VoiceChannelListener : ListenerAdapter() {
    companion object {
        private val channelLastInteractionMap: ExpiringMap<Guild, AudioChannel> = ExpiringMap.builder()
            .expirationPolicy(ExpirationPolicy.ACCESSED)
            .expiration(1, TimeUnit.DAYS)
            .expirationListener { guild: Guild, channel: AudioChannel ->
                if (channel.members.size <= 1) {
                    guild.audioManager.closeAudioConnection()
                    AudioManager.removeGuildHandler(guild)
                } else {
                    updateLastInteractionTime(guild, channel)
                }
            }
            .build()

        fun updateLastInteractionTime(guild: Guild, channel: AudioChannel) {
            channelLastInteractionMap[guild] = channel
        }
    }

    override fun onGuildVoiceUpdate(event: GuildVoiceUpdateEvent) {
        // Bot left voice chat - remove guild handler
        if (event.member === event.guild.selfMember && event.channelJoined == null) {
            return AudioManager.removeGuildHandler(event.guild)
        }

        // Someone has left a voice channel - check if the bot is now alone. If so, disconnect.
        processBotMove(event.guild, event.channelLeft, event.channelJoined)
    }

    private fun processBotMove(guild: Guild, channelLeft: AudioChannel?, channelJoined: AudioChannel?) {
        val botChannel = guild.audioManager.connectedChannel ?: return
        if (botChannel !== channelLeft && botChannel !== channelJoined) {
            return
        }

        /* Someone has joined/left the bot's voice channel or moved the bot.
           Refresh cache, so it doesn't automatically leave. */
        updateLastInteractionTime(guild, botChannel)

        val guildAudioManager = AudioManager.getGuildHandler(guild)
        if (guildAudioManager.player.playingTrack !== null) {
            // Pause if nobody is in the channel, otherwise resume.
            if (botChannel === channelLeft && channelLeft.members.size == 1
                || botChannel === channelJoined && channelJoined.members.size == 1) {
                guildAudioManager.player.isPaused = true
            } else {
                guildAudioManager.player.isPaused = false
            }
        }
    }
}