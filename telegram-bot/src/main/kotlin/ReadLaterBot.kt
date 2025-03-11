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
            trackEvent(
                userId = message.from.id.toString(),
                action = "link_sent_to_parser",
                data = mapOf("url" to message.text),
                userName = "${message.from.firstName} ${message.from.lastName}",
                telegramClient = telegramClient
            )
            sendToParser(message, telegramClient)
        } else {
            trackEvent(
                userId = message.from.id.toString(),
                action = "not_a_link",
                data = message.text ?: "-",
                userName = "${message.from.firstName} ${message.from.lastName}",
                telegramClient = telegramClient
            )
            sendText(fromId, "It's not a link to save, but we got your message! If it's a feedback, we appreciate it 💌", telegramClient)
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
        when {
            message.text?.startsWith("/start") == true -> {
                val startParam = message.text?.substringAfter(" ", "")?.takeIf { it.isNotEmpty() }
                val startType = when {
                    message.chat.isGroupChat || message.chat.isSuperGroupChat -> "group"
                    message.webAppData != null -> "webapp"
                    startParam?.startsWith("article_") == true -> "article_share"
                    else -> "direct"
                }
                
                trackEvent(
                    userId = message.from.id.toString(),
                    action = "start",
                    data = mapOf(
                        "start_param" to (startParam ?: ""),
                        "start_type" to startType,
                        "chat_type" to message.chat.type
                    ),
                    userName = "${message.from.firstName} ${message.from.lastName}",
                    telegramClient = telegramClient
                )
                sendText(fromId, startMessage, telegramClient, parseMode = "HTML")
            }
            message.text == "/help" -> sendText(fromId, startMessage, telegramClient, parseMode = "HTML")
        }
    }
}