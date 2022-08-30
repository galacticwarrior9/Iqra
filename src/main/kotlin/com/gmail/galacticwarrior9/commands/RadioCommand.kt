package com.gmail.galacticwarrior9.commands

import com.gmail.galacticwarrior9.util.getVoiceData
import com.gmail.galacticwarrior9.util.sendReply
import com.sedmelluq.discord.lavaplayer.player.AudioLoadResultHandler
import com.sedmelluq.discord.lavaplayer.tools.FriendlyException
import com.sedmelluq.discord.lavaplayer.track.AudioPlaylist
import com.sedmelluq.discord.lavaplayer.track.AudioTrack
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter


class RadioCommand : ListenerAdapter() {

    private val radioUrl = "https://Qurango.net/radio/tarateel"

    override fun onSlashCommandInteraction(event: SlashCommandInteractionEvent) {
        if (event.name != "radio") {
            return
        }

        val slashVoiceData = event.getVoiceData() ?: return

        val audioManager = slashVoiceData.guild.audioManager
        val guildAudioManager = slashVoiceData.guildAudioManager
        val memberVoiceChannel = slashVoiceData.audioChannel

        audioManager.openAudioConnection(memberVoiceChannel)

        audioManager.sendingHandler = guildAudioManager.playerSendHandler

        guildAudioManager.playerManager.loadItem(radioUrl, object : AudioLoadResultHandler {
            override fun trackLoaded(track: AudioTrack) {
                guildAudioManager.player.playTrack(track)
                return event.sendReply("Now streaming Qur'an recitations.")
            }

            override fun playlistLoaded(playlist: AudioPlaylist) {
                // This will not happen.
            }

            override fun noMatches() {
                return event.sendReply("There was an error while attempting to find the audio source.")
            }

            override fun loadFailed(throwable: FriendlyException) {
                return event.sendReply("There was an error while attempting to find the audio source.")
            }
        })

    }

}