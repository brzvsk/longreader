package goldenluk.readlaterbpt

import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.meta.api.methods.send.SendMessage
import org.telegram.telegrambots.meta.api.methods.updatingmessages.DeleteMessage
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboard
import org.telegram.telegrambots.meta.exceptions.TelegramApiException


fun sendText(
    id: Long,
    message: String,
    telegramClient: OkHttpTelegramClient,
    replyKeyboardMarkup: ReplyKeyboard? = null,
    disableWebPagePreview: Boolean = true,
    parseMode: String? = null
) {
    val sendMessageBuilder = SendMessage.builder()
        .chatId(id.toString())
        .text(message)
        .disableWebPagePreview(disableWebPagePreview)

    if (replyKeyboardMarkup != null) {
        sendMessageBuilder.replyMarkup(replyKeyboardMarkup)
    }
    if (parseMode != null) {
        sendMessageBuilder.parseMode(parseMode)
    }
    val sendMessage = sendMessageBuilder.build()

    try {
        telegramClient.execute(sendMessage)
    } catch (e: TelegramApiException) {
        e.printStackTrace()
    }
}

fun deleteMessage(id: Long, telegramClient: OkHttpTelegramClient, messageId: Int) {
    val deleteMessage = DeleteMessage(id.toString(), messageId)
    try {
        telegramClient.execute(deleteMessage)
    } catch (e: TelegramApiException) {
        e.printStackTrace()
    }
}