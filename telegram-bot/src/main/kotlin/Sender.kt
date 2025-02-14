package goldenluk.readlaterbpt

import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.meta.api.methods.send.SendMessage
import org.telegram.telegrambots.meta.api.methods.updatingmessages.DeleteMessage
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboard
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboardMarkup
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.KeyboardButton
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.KeyboardRow
import org.telegram.telegrambots.meta.api.objects.webapp.WebAppInfo
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

fun sendStartMessage(chatId: Long, telegramClient: OkHttpTelegramClient) {
    val webAppUrl = "https://your-mini-app-url.com" // Replace with your Mini App URL

    val keyboard = ReplyKeyboardMarkup.builder()
        .resizeKeyboard(true)
        .oneTimeKeyboard(false)  // Keeps the button visible
        .isPersistent(true)       // Ensures it stays on the bottom panel
        .keyboard(
            listOf(
                KeyboardRow(
                    listOf(
                        KeyboardButton.builder()
                            .text("🚀 Open the Reader")
                            .webApp(WebAppInfo(webAppUrl))
                            .build()
                    )
                )
            )
        )
        .build()

    sendText(chatId, "Tap the button below to open the Reader:", telegramClient, keyboard)
}
