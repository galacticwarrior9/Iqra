import com.sedmelluq.discord.lavaplayer.jdaudp.NativeAudioSendFactory
import net.dv8tion.jda.api.JDABuilder
import net.dv8tion.jda.api.entities.Activity
import net.dv8tion.jda.api.requests.GatewayIntent
import net.dv8tion.jda.api.utils.cache.CacheFlag

fun main() {
    val jda = JDABuilder.createDefault(System.getenv("token"))
        .setActivity(Activity.listening("Qurʾān"))
        .setAudioSendFactory(NativeAudioSendFactory())
        .disableCache(CacheFlag.ACTIVITY,
            CacheFlag.EMOTE,
            CacheFlag.ONLINE_STATUS,
            CacheFlag.ROLE_TAGS)
        .disableIntents(GatewayIntent.GUILD_PRESENCES,
            GatewayIntent.GUILD_MESSAGE_TYPING,
            GatewayIntent.GUILD_BANS,
            GatewayIntent.GUILD_EMOJIS,
            GatewayIntent.GUILD_MESSAGE_REACTIONS)
        .build()
        .awaitReady()

    val iqra = Iqra(jda)
    iqra.start()
}
