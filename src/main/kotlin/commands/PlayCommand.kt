package commands

import Iqra
import com.sedmelluq.discord.lavaplayer.player.AudioLoadResultHandler
import com.sedmelluq.discord.lavaplayer.tools.FriendlyException
import com.sedmelluq.discord.lavaplayer.track.AudioPlaylist
import com.sedmelluq.discord.lavaplayer.track.AudioTrack
import dev.minn.jda.ktx.events.CoroutineEventListener
import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.events.GenericEvent
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import org.slf4j.Logger
import util.getSurahMeta
import util.getVoiceData
import util.sendDeferredReply

class PlayCommand(private val logger: Logger) : CoroutineEventListener {
    override suspend fun onEvent(event: GenericEvent) {
        if (event !is SlashCommandInteractionEvent || event.name != "play") {
            return
        }

        event.deferReply().queue()

        val slashVoiceData = event.getVoiceData() ?: return
        val audioManager = slashVoiceData.guild.audioManager
        val guildAudioManager = slashVoiceData.guildAudioManager
        val memberVoiceChannel = slashVoiceData.audioChannel

        // Get surah meta.
        val surahNumber = event.getOption("surah_num") { option -> option.asInt } ?: return
        val surahMeta = getSurahMeta(surahNumber) ?: run {
            return event.sendDeferredReply(":warning: Failed to retrieve information for this surah. Please try again later.", true)
        }

        // Get reciter, if specified.
        val reciterName = event.getOption("reciter_name") { option -> option.asString } ?: "Mishary Alafasi"
        val reciters = getReciters() ?: run {
            return event.sendDeferredReply("Could not retrieve reciters list! Please try again later.", true)
        }

        var reciter: Reciter? = null
        for (testReciter in reciters) {
            if (testReciter.name.contentEquals(reciterName, true)) {
                reciter = testReciter
                break
            }
        }
        reciter ?: run {
            return event.sendDeferredReply("Could not find a reciter with the name $reciterName! Use `/reciters` to see the list of reciters.", true)
        }

        if (event.subcommandName == "surah") {
            audioManager.openAudioConnection(memberVoiceChannel)
            audioManager.sendingHandler = guildAudioManager.playerSendHandler

            val newUrl = "${reciter.Server}/${surahNumber.toString().padStart(3, '0')}.mp3"

            guildAudioManager.playerManager.loadItem(newUrl, object : AudioLoadResultHandler {
                override fun trackLoaded(track: AudioTrack) {
                    guildAudioManager.player.playTrack(track)

                    val embedBuilder = EmbedBuilder()
                        .setTitle("Playing Surah ${surahMeta.transliteratedName} (${surahMeta.translatedName}) / ${surahMeta.arabicName}")
                        .setColor(0x2a6b2b)
                        .setFooter("Provided through mp3quran.net.")

                    embedBuilder.descriptionBuilder
                        .append("This is a ${surahMeta.revelationLocation.asAdjective()} surah with ${surahMeta.verseCount} ayat.\n\n")
                        .append("• **Reciter**: ${reciter.name}\n")
                        .append("• **Riwayah**: ${reciter.rewaya}\n")

                    return event.hook.sendMessageEmbeds(embedBuilder.build()).queue()
                }

                override fun playlistLoaded(playlist: AudioPlaylist) {
                    // This will not happen.
                }

                override fun noMatches() {
                    return event.sendDeferredReply("There was an error while attempting to find the audio source.", true)
                }

                override fun loadFailed(throwable: FriendlyException) {
                    logger.error(throwable.toString())
                    return event.sendDeferredReply("There was an error while attempting to find the audio source.", true)
                }
            })
        }
    }
}