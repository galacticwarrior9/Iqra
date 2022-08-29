package commands

import com.google.gson.Gson
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
import org.slf4j.Logger
import util.replyAndSend
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader
import java.net.URL
import java.net.URLConnection
import java.util.concurrent.TimeUnit


val reciterListUrl = URL("https://mp3quran.net/api/_english.php")

data class Reciter(val name: String, val count: Int, val rewaya: String, val Server: URL)

class RecitersCommand(private val waiter: EventWaiter): CoroutineEventListener {

    override suspend fun onEvent(event: GenericEvent) {
        if (event !is SlashCommandInteractionEvent || event.name != "reciters") {
            return
        }

        var reciters = getReciters() ?: run {
            return event.replyAndSend("Could not retrieve reciters list! Please try again later.", true)
        }

        // If we're searching, we need to filter the reciters using the search term.
        if (event.subcommandName == "search") {
            val searchTerm = event.getOption("name") { option -> option.asString }!!
            reciters = reciters.asSequence()
                .filter { reciter -> FuzzySearch.tokenSetPartialRatio(searchTerm, reciter.name) > 70 }
                .toList()

            if (reciters.isEmpty()) {
                return event.replyAndSend(":warning: Could not find any reciters with this name.", true)
            }
        }

        val reciterPageEmbeds = paginateReciters(reciters)

        val paginator = ButtonEmbedPaginator.Builder()
            .setUsers(event.user)
            .addItems(reciterPageEmbeds)
            .setButtonStyle(ButtonStyle.SUCCESS)
            .setEventWaiter(waiter)
            .setTimeout(3, TimeUnit.MINUTES)
            .waitOnSinglePage(true)
            .setFinalAction { message -> message.editMessage("**:warning: This message has timed out**. Please re-run the command!").queue() }
            .build()

        return event.replyEmbeds(EmbedBuilder().setDescription("Displaying reciters..").build())
            .queue { interactionHook -> interactionHook.retrieveOriginal().queue { message ->
                    paginator.display(message)
                }
            }
    }
}

private fun paginateReciters(reciters: List<Reciter>): List<MessageEmbed> {
    val reciterPageEmbeds = mutableListOf<MessageEmbed>()
    val reciterEmbedBuilder = EmbedBuilder()
        .setTitle("Reciters")
        .setFooter("Page 1")
        .setColor(0x2a6b2b)

    // For every 10 reciters, we build an embed
    var counter = 0
    val reciterIterator = reciters.iterator()
    while (reciterIterator.hasNext()) {
        val reciter = reciterIterator.next();
        counter++
        reciterEmbedBuilder.descriptionBuilder.append("• ${reciter.name}\n")
        if (!reciterIterator.hasNext() || counter > 10) {
            reciterPageEmbeds.add(reciterEmbedBuilder.build())
            reciterEmbedBuilder.descriptionBuilder.clear()
            reciterEmbedBuilder.setFooter("Page ${reciterPageEmbeds.size + 1}")
            counter = 0
        }
    }
    return reciterPageEmbeds
}

suspend fun getReciters(): List<Reciter>? = withContext(Dispatchers.IO) {
    val request: URLConnection
    try {
        request = reciterListUrl.openConnection()
        request.connect()
    } catch (ex: IOException) {
        Iqra.logger.error("Failed to connect to $reciterListUrl!")
        return@withContext null
    }

    val json: JsonElement
    try {
        json = JsonParser.parseReader(InputStreamReader(request.content as InputStream))
    } catch (ex: Exception) {
        Iqra.logger.error("Failed to parse JSON at $reciterListUrl!")
        return@withContext null
    }

    val reciters = mutableListOf<Reciter>()
    val reciterNames = mutableSetOf<String>()

    val reciterJsonArray = json.asJsonObject.getAsJsonArray("reciters")
    val gson = Gson()
    for (reciterJson in reciterJsonArray) {
        val reciter = gson.fromJson(reciterJson, Reciter::class.java)
        // TODO - support riwayat
        if (reciterNames.contains(reciter.name) || reciter.count != 114) {
            continue
        }
        reciters.add(reciter)
        reciterNames.add(reciter.name)
    }
    return@withContext reciters
}
