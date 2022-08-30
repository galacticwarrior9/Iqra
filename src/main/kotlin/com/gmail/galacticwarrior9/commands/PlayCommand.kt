package com.gmail.galacticwarrior9.commands

import com.gmail.galacticwarrior9.util.getSurahMeta
import com.gmail.galacticwarrior9.util.getVoiceData
import com.gmail.galacticwarrior9.util.replySafely
import com.gmail.galacticwarrior9.util.sendDeferredReply
import com.sedmelluq.discord.lavaplayer.player.AudioLoadResultHandler
import com.sedmelluq.discord.lavaplayer.tools.FriendlyException
import com.sedmelluq.discord.lavaplayer.track.AudioPlaylist
import com.sedmelluq.discord.lavaplayer.track.AudioTrack
import dev.minn.jda.ktx.events.CoroutineEventListener
import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.events.GenericEvent
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import org.slf4j.Logger

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
        if (surahNumber < 1 || surahNumber > 114) {
            return event.replySafely(":warning: The surah number must be between 1 and 114.", true)
        }

        val surahMeta = getSurahMeta(surahNumber) ?: run {
            return event.sendDeferredReply(":warning: Failed to retrieve information for this surah. Please try again later.", true)
        }

        // Get recitation type
        val type: ReciterType = if (event.subcommandName == "surah") {
            ReciterType.SURAH
        } else {
            ReciterType.AYAH
        }

        // Validate the ayah, if specified.
        var ayahNumber = 0
        val ayatToPlay = mutableListOf<Int>()
        if (type === ReciterType.AYAH) {
            ayahNumber = event.getOption("ayah_num") { option -> option.asInt }!!
            if (ayahNumber < 1 || ayahNumber > surahMeta.verseCount) {
                return event.replySafely(":warning: There are only ${surahMeta.verseCount} ayat in this surah.")
            }

            val providedLastAyahNumber = event.getOption("last_ayah_num") { option -> option.asInt }
            if (providedLastAyahNumber != null) {
                if (providedLastAyahNumber < ayahNumber) {
                    return event.replySafely(":warning: The last ayah to play must be after the first ayah to play!", true)
                } else if (providedLastAyahNumber > surahMeta.verseCount) {
                    return event.replySafely(":warning: There are only ${surahMeta.verseCount} ayat in this surah.")
                }
                ayatToPlay.addAll(ayahNumber.rangeTo(providedLastAyahNumber))
            } else {
                ayatToPlay.add(ayahNumber)
            }
        }

        // Get reciter, if specified.
        val reciterName = event.getOption("reciter_name") { option -> option.asString } ?:"Mishary Alafasi"

        val reciters = getReciters(type)
        if (reciters.isEmpty()) {
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

        if (type === ReciterType.SURAH) {
            reciter = reciter as SurahReciter
            val newUrl = "${reciter.server}/${surahNumber.toString().padStart(3, '0')}.mp3"

            guildAudioManager.playerManager.loadItem(newUrl, object : AudioLoadResultHandler {
                override fun trackLoaded(track: AudioTrack) {
                    audioManager.openAudioConnection(memberVoiceChannel)
                    audioManager.sendingHandler = guildAudioManager.playerSendHandler

                    guildAudioManager.player.playTrack(track)

                    val embedBuilder = EmbedBuilder()
                        .setTitle("Playing Surah ${surahMeta.transliteratedName} (${surahMeta.translatedName}) / ${surahMeta.arabicName}")
                        .setColor(0x2a6b2b)
                        .setFooter("Source: mp3quran.net.")

                    embedBuilder.descriptionBuilder
                        .append("This is a ${surahMeta.revelationLocation.asAdjective()} surah with ${surahMeta.verseCount} ayat.\n\n")
                        .append("• **Reciter**: ${(reciter as SurahReciter).name}\n")
                        .append("• **Riwayah**: ${(reciter as SurahReciter).riwayah}\n")

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

        else {
            reciter = reciter as AyahReciter
            // e.g. https://verse.mp3quran.net/arabic/salaah_bukhatir/128/001003.mp3
            val recitationUrl = reciter.server
            val paddedSurah = surahNumber.toString().padStart(3, '0')

            val embedBuilder = EmbedBuilder()
                .setColor(0x2a6b2b)
                .setFooter("Source: mp3quran.net.")

            embedBuilder.descriptionBuilder
                .append("• **Reciter**: ${reciter.name}\n")
                .append("• **Style**: ${reciter.style}\n")

            if (ayatToPlay.size > 1) {
                embedBuilder.setTitle("Playing Surah ${surahMeta.transliteratedName} (${surahMeta.translatedName}) / ${surahMeta.arabicName}, Ayat ${ayatToPlay[0]} - ${ayatToPlay[ayatToPlay.lastIndex]}")
            } else {
                embedBuilder.setTitle("Playing Surah ${surahMeta.transliteratedName} (${surahMeta.translatedName}) / ${surahMeta.arabicName}, Ayah $ayahNumber")
            }

            for (ayah in ayatToPlay) {
                val paddedAyah = ayah.toString().padStart(3, '0')
                val mp3FileName = "$paddedSurah$paddedAyah.mp3"

                guildAudioManager.playerManager.loadItemOrdered(guildAudioManager.player, "$recitationUrl$mp3FileName",  object : AudioLoadResultHandler {
                    override fun trackLoaded(track: AudioTrack) {
                        audioManager.openAudioConnection(memberVoiceChannel)
                        audioManager.sendingHandler = guildAudioManager.playerSendHandler

                        if (guildAudioManager.player.playingTrack == null) {
                            event.hook.sendMessageEmbeds(embedBuilder.build()).queue()
                            guildAudioManager.player.playTrack(track)
                            return
                        }

                        guildAudioManager.trackScheduler.queue(track)
                    }

                    override fun playlistLoaded(playlist: AudioPlaylist) {
                        // This will not happen.
                    }

                    override fun noMatches() {
                        return event.sendDeferredReply(
                            "There was an error while attempting to find the audio source.",
                            true
                        )
                    }

                    override fun loadFailed(throwable: FriendlyException) {
                        logger.error(throwable.toString())
                        return event.sendDeferredReply(
                            "There was an error while attempting to find the audio source.",
                            true
                        )
                    }
                })
            }
        }
    }
}