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
    parseMode: String? = null
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

fun sendToParser(url: String, id: String, telegramClient: OkHttpTelegramClient) {
    // Send initial "Saving..." message
    val savingMessage = sendText(id.toLong(), "Saving...", telegramClient)

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

    val gson = Gson()

    // Execute the request
    client.newCall(request).execute().use { response: Response ->
        val responseBody = response.body?.string() ?: ""
        if (response.isSuccessful) {
            val articleResponse = gson.fromJson(responseBody, ArticleResponse::class.java)
            val botUsername = System.getenv("TELEGRAM_BOT_USERNAME") ?: "ReadWatchLaterBot"
            val appName = System.getenv("TELEGRAM_APP_NAME") ?: "LongreaderApp"
            val articleUrl = "https://t.me/$botUsername/$appName?startapp=article_${articleResponse.article_id}"

            // Create inline keyboard markup using the builder pattern
            val button = InlineKeyboardButton.builder()
                .text("Open in Reader 📚")
                .url(articleUrl)
                .build()

            val row = InlineKeyboardRow()
            row.add(button)

            val keyboard = InlineKeyboardMarkup.builder()
                .keyboard(listOf(row))
                .build()

            // Edit the message with success state
            editMessage(
                chatId = id.toLong(),
                messageId = savingMessage.messageId,
                newText = "Saved ✅",
                telegramClient = telegramClient,
                replyKeyboardMarkup = keyboard
            )
            sendLog(createLogMessageForSuccessSave(responseBody, id, url), telegramClient)
        } else {
            // Edit the message with error state
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
            sendLog(createLogMessageForParserError(responseBody, id, url, response.code), telegramClient)
        }
    }
}

private fun createLogMessageForParserError(response: String, id: String, url: String, code: Int): String {
    return """
        User ID: $id
        Name: -
        Action: parser_error
        Data: URL: $url, Error: $response, Code: $code
    """.trimIndent()
}

private fun createLogMessageForSuccessSave(response: String, id: String, url: String): String {
    return """
        User ID: $id
        Name: -
        Action: parser_success
        Data: $url
    """.trimIndent()
}

fun sendLog(
    message: String,
    telegramClient: OkHttpTelegramClient,
    disableWebPagePreview: Boolean = true,
) {
    val environment = System.getenv("TELEGRAM_BOT_ENVIRONMENT") ?: "test"
    if (environment != "prod") {
        return
    }

    val timestamp = java.time.Instant.ofEpochMilli(System.currentTimeMillis())
        .atZone(java.time.ZoneOffset.UTC)
        .format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS"))
    
    val messageWithTimestamp = """
        Timestamp: $timestamp UTC
$message
    """.trimIndent()

    val sendMessageBuilder = SendMessage.builder()
        .chatId(-1002328089278)
        .messageThreadId(552)
        .text(messageWithTimestamp)
        .disableWebPagePreview(disableWebPagePreview)

    val sendMessage = sendMessageBuilder.build()

    try {
        telegramClient.execute(sendMessage)
    } catch (e: TelegramApiException) {
        e.printStackTrace()
    }
}