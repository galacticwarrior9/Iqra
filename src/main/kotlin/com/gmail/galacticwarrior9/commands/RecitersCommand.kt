package com.gmail.galacticwarrior9.commands

import com.gmail.galacticwarrior9.Iqra
import com.gmail.galacticwarrior9.util.sendReply
import com.google.gson.JsonArray
import com.google.gson.JsonElement
import com.google.gson.JsonParser
import com.jagrosh.jdautilities.commons.waiter.EventWaiter
import com.jagrosh.jdautilities.menu.ButtonEmbedPaginator
import dev.minn.jda.ktx.events.CoroutineEventListener
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import me.xdrop.fuzzywuzzy.FuzzySearch
import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.entities.MessageEmbed
import net.dv8tion.jda.api.events.GenericEvent
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.interactions.components.buttons.ButtonStyle
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader
import java.net.URL
import java.net.URLConnection
import java.util.concurrent.TimeUnit


val surahReciterListUrl = URL("https://mp3quran.net/api/_english.php")
val ayahReciterListUrl = URL("https://mp3quran.net/api/verse/verse_en.json")

enum class ReciterType {
    SURAH,
    AYAH
}

abstract class Reciter(open val id: Int, open val name: String)

data class SurahReciter(override val id: Int, override val name: String, val count: Int, val riwayah: String, val server: URL): Reciter(id, name)

data class AyahReciter(override val id: Int, override val name: String, val riwayah: String, val style: String, val server: URL): Reciter(id, name)


class RecitersCommand(private val waiter: EventWaiter): CoroutineEventListener {

    override suspend fun onEvent(event: GenericEvent) {
        if (event !is SlashCommandInteractionEvent || event.name != "reciters") {
            return
        }

        val type = event.getOption("type") { ReciterType.valueOf(it.asString.toUpperCase()) }!!
        var reciters = getReciters(type)
        if (reciters.isEmpty()) {
            return event.sendReply("Could not retrieve reciters list! Please try again later.", true)
        }

        // If we're searching, we need to filter the reciters using the search term.
        if (event.subcommandName == "search") {
            val searchTerm = event.getOption("name") { option -> option.asString }!!
            reciters = reciters.asSequence()
                .filter { FuzzySearch.tokenSetPartialRatio(searchTerm, it.name) > 70 }
                .toList()

            if (reciters.isEmpty()) {
                return event.sendReply(":warning: Could not find any reciters with this name.", true)
            }
        }

        val reciterPageEmbeds = paginateReciters(reciters)

        val paginator = ButtonEmbedPaginator.Builder()
            .setUsers(event.user)
            .addItems(reciterPageEmbeds)
            .setButtonStyle(ButtonStyle.SUCCESS)
            .setEventWaiter(waiter)
            .waitOnSinglePage(true)
            .setTimeout(3, TimeUnit.MINUTES)
            .build()

        return event.replyEmbeds(EmbedBuilder().setDescription("Displaying reciters..").build())
            .queue { interactionHook -> interactionHook.retrieveOriginal().queue { message ->
                    paginator.display(message)
                }
            }
    }
}

private fun paginateReciters(reciters: List<Reciter>): List<MessageEmbed> {
    var numberOfPages = Math.ceil(reciters.size.toDouble() / 10).toInt()

    val reciterPageEmbeds = mutableListOf<MessageEmbed>()
    val reciterEmbedBuilder = EmbedBuilder()
        .setTitle("Reciters")
        .setFooter("Page 1 of ${numberOfPages}")
        .setColor(0x2a6b2b)

    // For every 10 reciters, we build an embed
    var counter = 0
    val reciterIterator = reciters.iterator()
    while (reciterIterator.hasNext()) {
        val reciter = reciterIterator.next();
        counter++
        reciterEmbedBuilder.descriptionBuilder.append("• ${reciter.name}\n")
        if (!reciterIterator.hasNext() || counter == 10) {
            reciterPageEmbeds.add(reciterEmbedBuilder.build())
            reciterEmbedBuilder.descriptionBuilder.clear()
            reciterEmbedBuilder.setFooter("Page ${reciterPageEmbeds.size + 1} of ${numberOfPages}")
            counter = 0
        }
    }
    return reciterPageEmbeds
}

suspend fun getReciters(type: ReciterType): List<Reciter> = withContext(Dispatchers.IO) {
    val reciterList = mutableListOf<Reciter>()
    val reciterNames = mutableSetOf<String>()

    val request: URLConnection
    try {
        request = if (type === ReciterType.SURAH) {
            surahReciterListUrl.openConnection()
        } else {
            ayahReciterListUrl.openConnection()
        }
        request.connect()
    } catch (ex: IOException) {
        Iqra.logger.error("Failed to connect to $type reciters URL.")
        return@withContext reciterList
    }

    val json: JsonElement
    try {
        json = JsonParser.parseReader(InputStreamReader(request.content as InputStream))
    } catch (ex: Exception) {
        Iqra.logger.error("Failed to parse JSON at ${request.url}!")
        return@withContext reciterList
    }

    val reciterJsonArray: JsonArray = if (type === ReciterType.SURAH) {
        json.asJsonObject.getAsJsonArray("reciters")
    } else {
        json.asJsonObject.getAsJsonArray("reciters_verse")
    }

    for (reciterJson in reciterJsonArray) {
        val jsonObj = reciterJson.asJsonObject
        val reciter: Reciter = if (type === ReciterType.SURAH) {
            SurahReciter(jsonObj.get("id").asInt, jsonObj.get("name").asString, jsonObj.get("count").asInt, jsonObj.get("rewaya").asString, URL(jsonObj.get("Server").asString))
        } else {
            val url = jsonObj.get("audio_url_bit_rate_128").asString
            if (url.length <= 1) {
                continue
            }
            AyahReciter(jsonObj.get("id").asInt, jsonObj.get("name").asString, jsonObj.get("rewaya").asString, jsonObj.get("musshaf_type").asString, URL(url))
        }

        // TODO - support riwayat/styles
        if (reciterNames.contains(reciter.name) || (reciter is SurahReciter && reciter.count != 114)) {
            continue
        }
        reciterList.add(reciter)
        reciterNames.add(reciter.name)
    }
    return@withContext reciterList
}
