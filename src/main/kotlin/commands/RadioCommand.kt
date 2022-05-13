package commands

import audioplayer.AudioManager
import com.sedmelluq.discord.lavaplayer.player.AudioLoadResultHandler
import com.sedmelluq.discord.lavaplayer.tools.FriendlyException
import com.sedmelluq.discord.lavaplayer.track.AudioPlaylist
import com.sedmelluq.discord.lavaplayer.track.AudioTrack
import net.dv8tion.jda.api.Permission
import net.dv8tion.jda.api.entities.GuildChannel
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import util.replyAndSend


class RadioCommand : ListenerAdapter() {

    private val radioUrl = "https://Qurango.net/radio/tarateel"

    override fun onSlashCommandInteraction(event: SlashCommandInteractionEvent) {
        if (event.name != "radio") {
            return
        }

        val guild = event.guild ?: return
        val memberVoiceChannel = event.member?.voiceState?.channel
            ?: return event.replyAndSend("You must join a voice channel to use this command.", true)

        if (!guild.selfMember.hasPermission(memberVoiceChannel as GuildChannel, Permission.VOICE_CONNECT)) {
            return event.replyAndSend("I do not have permission to join this voice channel!", true)
        }

        val guildAudioManager = AudioManager.getGuildHandler(guild)
        if (guildAudioManager.player.playingTrack !== null) {
            return event.replyAndSend("I am already playing something in this channel!", true)
        }

        val audioManager = guild.audioManager
        audioManager.openAudioConnection(memberVoiceChannel)

        audioManager.sendingHandler = guildAudioManager.playerSendHandler

        guildAudioManager.playerManager.loadItem(radioUrl, object : AudioLoadResultHandler {
            override fun trackLoaded(track: AudioTrack) {
                guildAudioManager.player.playTrack(track)
                event.replyAndSend("Now streaming Qur'an recitations.")
            }

            override fun playlistLoaded(playlist: AudioPlaylist) {
                // This will not happen.
            }

            override fun noMatches() {
                event.replyAndSend("There was an error while attempting to find the audio source.")
            }

            override fun loadFailed(throwable: FriendlyException) {
                event.replyAndSend("There was an error while attempting to find the audio source.")
            }
        })

    }

}