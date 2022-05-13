package util

import net.dv8tion.jda.api.events.interaction.command.SlashCommandInteractionEvent

fun SlashCommandInteractionEvent.replyAndSend(message: String, ephemeral: Boolean = false) {
    this.reply(message).setEphemeral(ephemeral).queue()
}
