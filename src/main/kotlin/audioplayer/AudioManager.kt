package audioplayer

import Iqra
import net.dv8tion.jda.api.entities.Guild

object AudioManager {
    private val audioSendHandlerMap = hashMapOf<Long, GuildAudioManager>()

    fun getGuildHandler(guild: Guild): GuildAudioManager {
        return audioSendHandlerMap.computeIfAbsent(guild.idLong) { GuildAudioManager(Iqra.audioPlayerManager) }
    }

    fun removeGuildHandler(guild: Guild) {
        audioSendHandlerMap.remove(guild.idLong)
    }

    fun createGuildHandler(guild: Guild) {
        audioSendHandlerMap[guild.idLong] = GuildAudioManager(Iqra.audioPlayerManager)
    }
}