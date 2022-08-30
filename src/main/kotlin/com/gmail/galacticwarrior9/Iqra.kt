package com.gmail.galacticwarrior9

import com.gmail.galacticwarrior9.commands.*
import com.gmail.galacticwarrior9.listeners.VoiceChannelListener
import com.jagrosh.jdautilities.commons.waiter.EventWaiter
import com.sedmelluq.discord.lavaplayer.player.AudioPlayerManager
import com.sedmelluq.discord.lavaplayer.player.DefaultAudioPlayerManager
import com.sedmelluq.discord.lavaplayer.source.AudioSourceManagers
import net.dv8tion.jda.api.JDA
import net.dv8tion.jda.api.interactions.commands.OptionType
import net.dv8tion.jda.api.interactions.commands.build.Commands
import net.dv8tion.jda.api.interactions.commands.build.OptionData
import net.dv8tion.jda.api.interactions.commands.build.SubcommandData
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class Iqra(private val bot: JDA) {
    companion object {
        val audioPlayerManager: AudioPlayerManager = DefaultAudioPlayerManager()
        val logger: Logger = LoggerFactory.getLogger(this::class.java)
    }

    fun start() {
        val waiter = EventWaiter()

        AudioSourceManagers.registerRemoteSources(audioPlayerManager);

        // Commands
        bot.addEventListener(waiter)
        bot.addEventListener(LeaveCommand())
        bot.addEventListener(RadioCommand())
        bot.addEventListener(RecitersCommand(waiter))
        bot.addEventListener(PlayCommand(logger))
        bot.addEventListener(PauseCommand())
        bot.addEventListener(ResumeCommand())
        bot.addEventListener(HelpCommand())

        // Other listeners
        bot.addEventListener(VoiceChannelListener())

        bot.updateCommands().addCommands(
            Commands.slash("radio", "Stream Qur'an recitations to your voice channel."),
            Commands.slash("leave", "Instructs the bot to leave its voice channel."),
            Commands.slash("pause", "Instructs the bot pause playback."),
            Commands.slash("resume", "Instructs the bot to resume playing paused playback."),
            Commands.slash("help", "Browse the bot's documentation"),

            Commands.slash("reciters", "Browse or search for reciters.")
                .addSubcommands(
                    SubcommandData("list", "List reciters.")
                        .addOptions(
                            OptionData(OptionType.STRING, "type", "Should we list reciters for per-surah recitations or per-ayah recitations?", true)
                                .addChoice("surah", "surah")
                                .addChoice("ayah", "ayah")
                        ),
                    SubcommandData("search", "Search reciters.")
                        .addOptions(
                            OptionData(OptionType.STRING, "type", "Should we search reciters for per-surah recitations or per-ayah recitations?", true)
                                .addChoice("surah", "surah")
                                .addChoice("ayah", "ayah"),
                            OptionData(OptionType.STRING, "name", "The name of the reciter.", true)
                        )
                ),

            Commands.slash("play", "Play selected portions of the Qur'an.")
                .addSubcommands(SubcommandData("surah", "Play a surah.")
                    .addOption(OptionType.INTEGER, "surah_num", "The order in which this surah appears in the Qur'an, e.g. 1 for al-Fatihah.", true)
                    .addOption(OptionType.STRING, "reciter_name", "The name of the reciter, from the /reciters command.", false))
                .addSubcommands(SubcommandData("ayah", "Play an ayah.")
                    .addOption(OptionType.INTEGER, "surah_num", "The order in which the surah of this ayah appears in the Qur'an, e.g. 1 for al-Fatihah.", true)
                    .addOption(OptionType.INTEGER, "ayah_num", "The order in which this ayah appears in the surah.", true)
                    .addOption(OptionType.INTEGER, "last_ayah_num", "The last ayah in the surah to play, if you want to play multiple ayat. Must be higher than ayah_num.", false)
                    .addOption(OptionType.STRING, "reciter_name", "The name of the reciter, from the /reciters command.", false))
        ).queue()
    }

}