package commands

import com.google.gson.Gson
import com.google.gson.JsonElement
import com.google.gson.JsonParser
import com.jagrosh.jdautilities.commons.waiter.EventWaiter
import com.jagrosh.jdautilities.menu.ButtonEmbedPaginator
import dev.minn.jda.ktx.events.CoroutineEventListener
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.entities.MessageEmbed
import net.dv8tion.jda.api.events.GenericEvent
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.interactions.components.buttons.ButtonStyle
import org.slf4j.Logger
import java.io.IOException
import java.io.InputStream
import java.io.InputStreamReader
import java.net.URL
import java.net.URLConnection
import java.util.concurrent.TimeUnit


private val reciterListUrl = URL("https://mp3quran.net/api/_english.php")

data class Reciter(val name: String, val count: Int, val riwayah: String, val Server: URL)

class RecitersCommand(private val waiter: EventWaiter, private val logger: Logger): CoroutineEventListener {

    override suspend fun onEvent(event: GenericEvent) {
        if (event !is SlashCommandInteractionEvent || event.name != "reciters") {
            return
        }

        val reciters = getReciters() ?: run {
            return event.hook.sendMessage("Could not retrieve reciters list! Please try again later.")
                .setEphemeral(true)
                .queue()
        }

        val reciterPageEmbeds = mutableListOf<MessageEmbed>()
        val reciterEmbedBuilder = EmbedBuilder()
        reciterEmbedBuilder.setTitle("Reciters")
        reciterEmbedBuilder.setFooter("Page 1")
        reciterEmbedBuilder.setColor(0x2a6b2b)

        // For every 10 reciters, we build an embed
        var counter = 0
        for (reciter in reciters) {
            counter++
            if (counter > 10) {
                reciterPageEmbeds.add(reciterEmbedBuilder.build())
                reciterEmbedBuilder.descriptionBuilder.clear()
                reciterEmbedBuilder.setFooter("Page ${reciterPageEmbeds.size + 1}")
                counter = 0
            }
            // TODO - different riwayat
            reciterEmbedBuilder.descriptionBuilder.append("• ${reciter.name}\n")
        }

        val paginator = ButtonEmbedPaginator.Builder()
            .setUsers(event.user)
            .addItems(reciterPageEmbeds)
            .setButtonStyle(ButtonStyle.SUCCESS)
            .setEventWaiter(waiter)
            .setTimeout(3, TimeUnit.MINUTES)
            .setFinalAction { message -> message.editMessage("**:warning: This message has timed out**. Please re-run the command!").queue() }
            .build()

        return event.replyEmbeds(EmbedBuilder().setDescription("Displaying reciters..").build())
            .queue { interactionHook -> interactionHook.retrieveOriginal().queue { message ->
                    paginator.display(message)
                }
            }
    }

    private suspend fun getReciters(): List<Reciter>? = withContext(Dispatchers.IO) {
        val request: URLConnection
        try {
            request = reciterListUrl.openConnection()
            request.connect()
        } catch (ex: IOException) {
            logger.error("Failed to connect to $reciterListUrl!")
            return@withContext null
        }

        val json: JsonElement
        try {
            json = JsonParser.parseReader(InputStreamReader(request.content as InputStream))
        } catch (ex: Exception) {
            logger.error("Failed to parse JSON at $reciterListUrl!")
            return@withContext null
        }

        val reciters = mutableListOf<Reciter>()
        val reciterNames = mutableSetOf<String>()

        val reciterJsonArray = json.asJsonObject.getAsJsonArray("reciters")
        val gson = Gson()
        for (reciterJson in reciterJsonArray) {
            val reciter = gson.fromJson(reciterJson, Reciter::class.java)
            // TODO - support riwayat
            if (reciterNames.contains(reciter.name.lowercase()) || reciter.count != 114) {
                continue
            }
            reciters.add(reciter)
            reciterNames.add(reciter.name.lowercase())
        }
        return@withContext reciters
    }
}
