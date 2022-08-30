package com.gmail.galacticwarrior9.commands

import net.dv8tion.jda.api.EmbedBuilder
import net.dv8tion.jda.api.entities.MessageEmbed
import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent
import net.dv8tion.jda.api.events.interaction.component.SelectMenuInteractionEvent
import net.dv8tion.jda.api.hooks.ListenerAdapter
import net.dv8tion.jda.api.interactions.components.selections.SelectMenu
import net.dv8tion.jda.api.utils.messages.MessageCreateBuilder

class HelpCommand : ListenerAdapter() {

    private val embedColour = 0x2a6b2b
    private val thumbnailUrl = "https://cdn.discordapp.com/app-icons/706134327200841870/e6bb860daa7702ea70e6d6e29c3d36f6.png"

    override fun onSlashCommandInteraction(event: SlashCommandInteractionEvent) {
        if (event.name != "help") {
            return
        }

        val embedBuilder = EmbedBuilder()
            .setTitle("Iqra")
            .setThumbnail(thumbnailUrl)
            .setColor(embedColour)
            .addField(MessageEmbed.Field("Links",
                "• [Support Server](https://discord.gg/Ud3MHJR)" +
                        "\n• [Source Code](https://github.com/galacticwarrior9/Iqra)" +
                        "\n• Running Iqra is not free. Please consider [donating](https://ko-fi.com/zaify).",
                false))

        embedBuilder.descriptionBuilder
            .append("**Iqra** is a Discord bot that plays Qur'an recitations in voice channels.")
            .append("\nUse the help menu below to learn more.")

        val menu = SelectMenu.create("iqra:help")
            .setMinValues(1)
            .setMaxValues(1)
            .setPlaceholder("Choose a help topic")
            .addOption("Playing", "Learn how to play recitations in voice chat.")
            .addOption("Reciters", "Learn how to browse and search for reciters.")
            .build()

        event.reply(MessageCreateBuilder().setEmbeds(embedBuilder.build()).setActionRow(menu).build()).queue()
    }

    override fun onSelectMenuInteraction(event: SelectMenuInteractionEvent) {
        if (event.componentId != "iqra:help") {
            return
        }

        val options = event.interaction.selectedOptions
        if (options.size > 1) {
            return
        }

        event.deferEdit().queue()

        val playingEmbed = EmbedBuilder()
            .setTitle("Playing")
            .setThumbnail(thumbnailUrl)
            .setColor(embedColour)
        playingEmbed.descriptionBuilder
            .append("**Use the `/play` command to play recitations to a voice channel.** ")
            .append("You can choose between playing full surat and specific ayat within a surah.")
            .append("\n\nSpecific **reciters** can be specified. There are different reciters for whole surah and ayah-by-ayah recitations. The `/reciters` command displays the full list.")
            .append("\n\nThe `/radio` command streams online Qur'an radio to a voice channel.")
            .append("\n\n`/pause` and `/resume` pause and resume playback respectively.")
            .append("\n\nIf you need the bot to stop playing and leave the voice channel, use `/leave`.")

        val recitersEmbed = EmbedBuilder()
            .setTitle("Reciters")
            .setThumbnail(thumbnailUrl)
            .setColor(embedColour)
        recitersEmbed.descriptionBuilder
            .append("**Use `/reciters` to browse and search the list of reciters that can be used in `/play`.**")
            .append("\n\nThere are **two lists** of reciters — one for whole surah recitations, and the other for ayah-by-ayah recitations. ")
            .append("These reciters can be selected in `/play surah` and `/play ayah` respectively. Browse them with `/reciters list`. ")
            .append("\n\nKeep in mind that you need to provide the **exact** name of the reciters to the `/play` commands.")
            .append("\n\nTo search the reciter lists for a specific reciter, use `/reciters search`.")

        when (options[0].label) {
            "Playing" -> return event.hook.editOriginalEmbeds(playingEmbed.build()).queue()
            "Reciters" -> return event.hook.editOriginalEmbeds(recitersEmbed.build()).queue()
        }
    }
}