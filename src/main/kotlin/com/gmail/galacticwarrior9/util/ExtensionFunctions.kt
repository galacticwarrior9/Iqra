package com.gmail.galacticwarrior9.util

import com.gmail.galacticwarrior9.audioplayer.AudioManager
import com.gmail.galacticwarrior9.audioplayer.GuildAudioManager
import net.dv8tion.jda.api.Permission
import net.dv8tion.jda.api.entities.AudioChannel
import net.dv8tion.jda.api.entities.Guild
import net.dv8tion.jda.api.entities.GuildChannel
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent

data class SlashVoiceData(val guild: Guild, val audioChannel: AudioChannel, val guildAudioManager: GuildAudioManager)

fun SlashCommandInteractionEvent.sendReply(message: String, ephemeral: Boolean = false) {
    this.reply(message).setEphemeral(ephemeral).queue()
}

fun SlashCommandInteractionEvent.sendDeferredReply(message: String, ephemeral: Boolean = false) {
    this.hook.sendMessage(message).setEphemeral(ephemeral).queue()
}

/**
 * Replies safely to a SlashCommandInteractionEvent, sending the message through the interaction hook
 * if the interaction has already been acknowledged (e.g. in the case of deferred replies).
 */
fun SlashCommandInteractionEvent.replySafely(message: String, ephemeral: Boolean = false) {
    if (this.isAcknowledged) {
        sendDeferredReply(message, ephemeral)
    } else {
        sendReply(message, ephemeral)
    }
}

/**
 * Checks whether the bot is able to connect to and join the voice channel of the command executor.
 * @return the SlashVoiceData for this SlashCommandInteractionEvent, or null if the bot is unable to join the
 *         voice channel.
 */
fun SlashCommandInteractionEvent.getVoiceData(): SlashVoiceData? {
    val guild = this.guild ?: return null

    // Check if user is in a voice channel
    val memberVoiceChannel = this.member?.voiceState?.channel ?: run {
        this.replySafely(":warning: You must join a voice channel to use this command.", true)
        return null
    }

    // Check if bot has permission to connect to user's voice channel.
    if (!guild.selfMember.hasPermission(memberVoiceChannel as GuildChannel, Permission.VOICE_CONNECT)) {
        this.replySafely(":warning: I do not have permission to join your voice channel!", true)
        return null
    }

    // Check if bot is already playing something in this server
    val guildAudioManager = AudioManager.getGuildHandler(guild)
    if (guildAudioManager.player.playingTrack !== null) {
        this.replySafely(":warning: I am already playing something in this channel!", true)
        return null
    }

    return SlashVoiceData(guild, memberVoiceChannel, guildAudioManager)
}
