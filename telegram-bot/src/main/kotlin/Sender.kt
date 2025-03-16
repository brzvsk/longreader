package goldenluk.readlaterbpt

import com.google.gson.Gson
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.meta.api.methods.send.SendMessage
import org.telegram.telegrambots.meta.api.methods.updatingmessages.EditMessageText
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardRow
import org.telegram.telegrambots.meta.api.objects.message.Message
import org.telegram.telegrambots.meta.exceptions.TelegramApiException


fun sendText(
    id: Long,
    message: String,
    telegramClient: OkHttpTelegramClient,
    replyKeyboardMarkup: InlineKeyboardMarkup? = null,
    disableWebPagePreview: Boolean = true,
    parseMode: String? = null,
    replyToMessageId: Int? = null
): Message {
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
    if (replyToMessageId != null) {
        sendMessageBuilder.replyToMessageId(replyToMessageId)
    }
    val sendMessage = sendMessageBuilder.build()

    try {
        return telegramClient.execute(sendMessage)
    } catch (e: TelegramApiException) {
        e.printStackTrace()
        throw e
    }
}

fun editMessage(
    chatId: Long,
    messageId: Int,
    newText: String,
    telegramClient: OkHttpTelegramClient,
    replyKeyboardMarkup: InlineKeyboardMarkup? = null,
    parseMode: String? = null
) {
    val editMessageBuilder = EditMessageText.builder()
        .chatId(chatId.toString())
        .messageId(messageId)
        .text(newText)

    if (replyKeyboardMarkup != null) {
        editMessageBuilder.replyMarkup(replyKeyboardMarkup)
    }
    if (parseMode != null) {
        editMessageBuilder.parseMode(parseMode)
    }
    val editMessage = editMessageBuilder.build()

    try {
        telegramClient.execute(editMessage)
    } catch (e: TelegramApiException) {
        e.printStackTrace()
        throw e
    }
}

fun sendToParser(message: Message, telegramClient: OkHttpTelegramClient) {
    val url = message.text
    val id = message.from.id.toString()

    // Send initial "Saving..." message as a reply
    val savingMessage = sendText(
        id.toLong(), 
        "Saving...", 
        telegramClient,
        replyToMessageId = message.messageId
    )

    val client = OkHttpClient()
    val mediaType = "application/json; charset=utf-8".toMediaType()
    val jsonBody = """{
        "url": "$url"
    }""".trimIndent()
    val body = jsonBody.toRequestBody(mediaType)

    val baseUrl = System.getenv("NEXT_PUBLIC_API_URL")
    if (baseUrl.isNullOrBlank()) {
        println("NEXT_PUBLIC_API_URL is null or blank")
        return
    }

    val request = Request.Builder()
        .url("$baseUrl/users/$id/articles/parse")
        .post(body)
        .build()

    val gson = Gson()

    client.newCall(request).execute().use { response: Response ->
        val responseBody = response.body?.string() ?: ""
        if (response.isSuccessful) {
            val articleResponse = gson.fromJson(responseBody, ArticleResponse::class.java)
            val botUsername = System.getenv("TELEGRAM_BOT_USERNAME") ?: "ReadWatchLaterBot"
            val appName = System.getenv("TELEGRAM_APP_NAME") ?: "LongreaderApp"
            val articleUrl = "https://t.me/$botUsername/$appName?startapp=article_${articleResponse.article_id}"

            val button = InlineKeyboardButton.builder()
                .text("Read now 📚")
                .url(articleUrl)
                .build()

            val row = InlineKeyboardRow()
            row.add(button)

            val keyboard = InlineKeyboardMarkup.builder()
                .keyboard(listOf(row))
                .build()

            editMessage(
                chatId = id.toLong(),
                messageId = savingMessage.messageId,
                newText = "Saved ✅",
                telegramClient = telegramClient,
                replyKeyboardMarkup = keyboard
            )
            
            trackEvent(
                userId = id,
                action = "parser_success",
                data = mapOf("url" to url),
                telegramClient = telegramClient
            )
        } else {
            val errorText = if (responseBody.contains("429")) {
                "Saving failed :( Limit of 10 articles per day has been reached. Need more articles? Simply write 'no limit' in the chat below"
            } else {
                "Saving failed :( We're aware of this issue and working on it 💫"
            }
            
            editMessage(
                chatId = id.toLong(),
                messageId = savingMessage.messageId,
                newText = errorText,
                telegramClient = telegramClient
            )
            
            trackEvent(
                userId = id,
                action = "parser_error",
                data = mapOf(
                    "url" to url,
                    "error" to responseBody,
                    "code" to response.code
                ),
                telegramClient = telegramClient
            )
        }
    }
}

fun trackEvent(
    userId: String,
    action: String,
    data: Any,
    userName: String? = null,
    telegramClient: OkHttpTelegramClient,
) {
    // Send event to API
    val client = OkHttpClient()
    val mediaType = "application/json; charset=utf-8".toMediaType()
    
    val eventJson = """
        {
            "user_id": "$userId",
            "action": "$action",
            "data": ${if (data is String) "\"$data\"" else Gson().toJson(data)},
            "user_name": ${if (userName != null) "\"$userName\"" else "null"},
            "source": "telegram-bot"
        }
    """.trimIndent()

    val body = eventJson.toRequestBody(mediaType)

    val baseUrl = System.getenv("NEXT_PUBLIC_API_URL")
    if (!baseUrl.isNullOrBlank()) {
        val request = Request.Builder()
            .url("$baseUrl/analytics/events")
            .post(body)
            .build()

        try {
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    println("Failed to store event in MongoDB: ${response.code}")
                }
            }
        } catch (e: Exception) {
            println("Error storing event in MongoDB: ${e.message}")
        }
    }

    // Skip Telegram sending in test environment
    val environment = System.getenv("TELEGRAM_BOT_ENVIRONMENT") ?: "test"
    if (environment != "prod") {
        return
    }

    val timestamp = java.time.Instant.ofEpochMilli(System.currentTimeMillis())
        .atZone(java.time.ZoneOffset.UTC)
        .format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS"))
    
    // Format message for Telegram
    val message = """
        Timestamp: $timestamp UTC
        User ID: $userId
        Name: ${userName ?: "-"}
        Action: $action
        Data: ${if (data is String) data else Gson().toJson(data)}
        Source: telegram-bot
    """.trimIndent()

    val sendMessageBuilder = SendMessage.builder()
        .chatId(-1002328089278)
        .messageThreadId(552)
        .text(message)
        .disableWebPagePreview(true)

    val sendMessage = sendMessageBuilder.build()

    try {
        telegramClient.execute(sendMessage)
    } catch (e: TelegramApiException) {
        e.printStackTrace()
    }
}