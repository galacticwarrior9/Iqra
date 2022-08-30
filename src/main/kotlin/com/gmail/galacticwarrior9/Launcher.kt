package com.gmail.galacticwarrior9

import com.sedmelluq.discord.lavaplayer.jdaudp.NativeAudioSendFactory
import dev.minn.jda.ktx.jdabuilder.injectKTX
import net.dv8tion.jda.api.JDABuilder
import net.dv8tion.jda.api.entities.Activity
import net.dv8tion.jda.api.requests.GatewayIntent
import net.dv8tion.jda.api.utils.cache.CacheFlag

fun main() {
    val jda = JDABuilder.createDefault(System.getenv("token"))
        .setActivity(Activity.listening("Qurʾān - /help"))
        .setAudioSendFactory(NativeAudioSendFactory())
        .disableCache(CacheFlag.ACTIVITY,
            CacheFlag.EMOJI,
            CacheFlag.STICKER,
            CacheFlag.ONLINE_STATUS,
            CacheFlag.ROLE_TAGS)
        .disableIntents(GatewayIntent.GUILD_PRESENCES,
            GatewayIntent.GUILD_MESSAGE_TYPING,
            GatewayIntent.GUILD_BANS,
            GatewayIntent.GUILD_EMOJIS_AND_STICKERS,
            GatewayIntent.GUILD_MESSAGE_REACTIONS)
        .injectKTX() // apply CoroutineEventManager
        .build()
        .awaitReady()

    val iqra = Iqra(jda)
    iqra.start()
}
