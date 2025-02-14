package goldenluk.readlaterbpt

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.longpolling.util.LongPollingSingleThreadUpdateConsumer
import org.telegram.telegrambots.meta.TelegramUrl
import org.telegram.telegrambots.meta.api.objects.CallbackQuery
import org.telegram.telegrambots.meta.api.objects.Update
import org.telegram.telegrambots.meta.api.objects.message.Message
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardRow
import java.net.URL

class ReadLaterBot : LongPollingSingleThreadUpdateConsumer {

    private val botEnvironment = System.getenv("TELEGRAM_BOT_ENVIRONMENT")
    private val telegramUrl = if (botEnvironment == "prod") {
        TelegramUrl("https", "api.telegram.org", 443, false)
    } else {
        TelegramUrl("https", "api.telegram.org", 443, true)
    }
    private val telegramClient = OkHttpTelegramClient(System.getenv("TELEGRAM_BOT_TOKEN").orEmpty(), telegramUrl)
    private val dbHelper = DatabaseHelper()

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

    private fun sendAllBookmarks(fromId: Long) {
        val bookmarks = dbHelper.getBookmarks(fromId.toString())
        if (bookmarks.isNullOrEmpty()) {
            sendText(fromId, "No bookmarks!", telegramClient)
            return
        }
        bookmarks.forEach {
            val cancelReply = InlineKeyboardMarkup(
                listOf(
                    InlineKeyboardRow(
                        InlineKeyboardButton.builder()
                            .text("Delete")
                            .callbackData("delete&id=${it.id}")
                            .build(),

                        )
                )
            )
            sendText(
                fromId,
                "\n${it.text}\n\nFrom: ${it.source}\n\nAdded: ${it.dateAdded}\n",
                telegramClient,
                cancelReply
            )
        }
    }

    private fun handleMessage(update: Update) {
        val message = update.message
        val fromId = message.from.id

        if (isValidUrl(message.text)) {
            sendToParser(message.text, fromId.toString())
        } else {
            sendText(fromId, "Not a link", telegramClient)
        }

        /*val date = LocalDateTime.now()
        val formatter = DateTimeFormatter.ofPattern("dd MMM yyyy HH:mm", Locale.ENGLISH)
        val formattedDate = date.format(formatter)

        val forwardOrigin: MessageOrigin? = message.forwardOrigin
        var sm = ""
        var originalMessageLink = ""



        if (forwardOrigin != null) {
            if (forwardOrigin is MessageOriginUser) {
                val who = if (forwardOrigin.senderUser.isBot) {
                    "bot"
                } else {
                    "user"
                }
                sm = "Forwarded from $who : https://t.me/${forwardOrigin.senderUser.userName}"
            } else if (forwardOrigin is MessageOriginChat) {
                val name = if (forwardOrigin.senderChat.userName != null) {
                    forwardOrigin.senderChat.userName
                } else {
                    "Has no name or name hidden because of privacy"
                }
                sm = "Forwarded from group: $name"
            } else if (forwardOrigin is MessageOriginChannel) {
                val channelUsername = forwardOrigin.chat.userName
                val originalMessageId = forwardOrigin.messageId

                if (channelUsername != null) {
                    originalMessageLink = "https://t.me/$channelUsername/$originalMessageId"
                    sm = "Original Message Link: $originalMessageLink"
                } else {
                    sm = "Forwarded from a private channel, cannot generate a link."
                }
            } else if (forwardOrigin is MessageOriginHiddenUser) {
                sm = "Forwarded from hidden user or/and private channel/group"
            }
        } else {
            sm = "Added manually, no forward"
        }

        val successMessage = "New bookmark has been added! $sm"

        val source = originalMessageLink.ifBlank {
            sm
        }

        dbHelper.addBookmark(
            fromId.toString(), Bookmark(
                id = "${System.currentTimeMillis()}-${Math.random()}",
                text = message.text,
                source = source,
                dateAdded = formattedDate,
                status = "new"
            ),
            message.from.userName
        )

        sendText(fromId, successMessage, telegramClient)*/
    }

    private fun extractId(input: String): String? {
        val idParam = input.split("&").find { it.startsWith("id=") }
        return idParam?.substringAfter("id=")
    }

    private fun isValidUrl(url: String): Boolean {
        return try {
            URL(url).toURI() // Converts to URI to check validity
            true
        } catch (e: Exception) {
            false
        }
    }

    private fun sendToParser(url: String, id: String) {
        val client = OkHttpClient()

        // Define the JSON media type
        val mediaType = "application/json; charset=utf-8".toMediaType()

        // JSON body with dynamic URL
        val jsonBody = """{
        "url": "$url"
    }""".trimIndent()

        // Create the request body
        val body = jsonBody.toRequestBody(mediaType)

        val baseUrl = System.getenv("NEXT_PUBLIC_API_URL")
        if (baseUrl.isNullOrBlank()) {
            println("NEXT_PUBLIC_API_URL is null or blank")
            return
        }

        // Build the request with dynamic user ID
        val request = Request.Builder()
            .url("$baseUrl/users/$id/articles/parse") // Use id dynamically
            .post(body)
            .build()

        // Execute the request
        client.newCall(request).execute().use { response: Response ->
            if (!response.isSuccessful) {
                sendText(id.toLong(), "Saving is failed :(", telegramClient)
                println("Request failed: ${response.code}")
            } else {
                sendText(id.toLong(), "Saved \uD83D\uDC4D", telegramClient)
                println("Response: ${response.body?.string()}")
            }
        }
    }

    private fun handleCallbackQuery(callbackQuery: CallbackQuery) {
        val data = callbackQuery.data
        val messageId = callbackQuery.message.messageId
        val userId = callbackQuery.from.id

        try {
            if (data.startsWith("delete")) {
                val id = extractId(data)
                if (id != null) {
                    dbHelper.removeBookmark(userId.toString(), id)
                    deleteMessage(userId, telegramClient, messageId)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun handleCommand(message: Message) {
        val fromId = message.from.id
        when (message.text) {
            "/start" -> sendStartMessage(fromId, telegramClient)
            "/help" -> sendText(fromId, "Help TBD", telegramClient)
            "/all" -> sendAllBookmarks(fromId)
            "/clear_all" -> dbHelper.removeAllBookmarks(fromId.toString())
        }
    }

    /*fun notifyChangelog() {
        val users = dbHelper.getUsers()
        users.forEach {
            try {
                sendText(
                    it._id.toLong(), "Hey, ${it.username}!\n\nI'm happy to introduce you fresh update!\n\n" +
                            "Now, when you send or forward a message to me, I'll show you where it came from, and the link, if I can.\n\n" +
                            "When you check all your entries by /all, you will see source of entry as well.\n\n" +
                            "Thank you for your attention!", telegramClient
                )
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }*/
}