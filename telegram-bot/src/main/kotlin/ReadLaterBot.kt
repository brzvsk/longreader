package goldenluk.readlaterbpt

import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.longpolling.util.LongPollingSingleThreadUpdateConsumer
import org.telegram.telegrambots.meta.TelegramUrl
import org.telegram.telegrambots.meta.api.objects.CallbackQuery
import org.telegram.telegrambots.meta.api.objects.Update
import org.telegram.telegrambots.meta.api.objects.message.Message
import java.net.URL

class ReadLaterBot : LongPollingSingleThreadUpdateConsumer {

    private val botEnvironment = System.getenv("TELEGRAM_BOT_ENVIRONMENT")
    private val telegramUrl = if (botEnvironment == "prod") {
        TelegramUrl("https", "api.telegram.org", 443, false)
    } else {
        TelegramUrl("https", "api.telegram.org", 443, true)
    }
    private val telegramClient = OkHttpTelegramClient(System.getenv("TELEGRAM_BOT_TOKEN").orEmpty(), telegramUrl)

    override fun consume(update: Update?) {
        if (update == null) return

        if (update.hasCallbackQuery()) {
            handleCallbackQuery(update.callbackQuery)
            return
        }

        if (update.hasMessage() && update.message.isCommand) {
            handleCommand(update.message)
            return
        }

        if (update.hasMessage()) {
            handleMessage(update)
        }
    }

    private fun handleMessage(update: Update) {
        val message = update.message
        val fromId = message.from.id

        if (message != null && message.text.isNullOrBlank().not() && isValidUrl(message.text)) {
            sendToParser(message.text, fromId.toString(), telegramClient)
        } else {
            sendText(fromId, "Not a link", telegramClient)
        }
    }

    private fun isValidUrl(url: String): Boolean {
        return try {
            URL(url).toURI() // Converts to URI to check validity
            true
        } catch (e: Exception) {
            false
        }
    }

    private fun handleCallbackQuery(callbackQuery: CallbackQuery) {
        // no actions yet. Will be used for buttons
    }

    private fun handleCommand(message: Message) {
        val fromId = message.from.id
        when (message.text) {
            "/start" -> sendText(fromId, startMessage, telegramClient)
            "/help" -> sendText(fromId, startMessage, telegramClient)
        }
    }
}