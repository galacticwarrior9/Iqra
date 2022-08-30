package com.gmail.galacticwarrior9.audioplayer

import com.sedmelluq.discord.lavaplayer.player.AudioPlayerManager

class GuildAudioManager(val playerManager: AudioPlayerManager) {
    val player = playerManager.createPlayer()
    val trackScheduler = TrackScheduler(player)
    val playerSendHandler = AudioPlayerSendHandler(player)

    fun GuildAudioManager() {
        player.addListener(trackScheduler)
    }
}