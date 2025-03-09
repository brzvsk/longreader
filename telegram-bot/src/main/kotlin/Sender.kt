package goldenluk.readlaterbpt

import com.google.gson.Gson
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.meta.api.methods.send.SendMessage
import org.telegram.telegrambots.meta.api.objects.replykeyboard.ReplyKeyboard
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardRow
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

fun sendToParser(url: String, id: String, telegramClient: OkHttpTelegramClient) {
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
            val successMessage = "Saved ✅"

            // Create inline keyboard markup using the builder pattern
            val button = InlineKeyboardButton.builder()
                .text("Open Article 📖")
                .url(articleUrl)
                .build()

            val row = InlineKeyboardRow()
            row.add(button)

            val keyboard = InlineKeyboardMarkup.builder()
                .keyboard(listOf(row))
                .build()

            sendText(
                id.toLong(), 
                successMessage, 
                telegramClient,
                replyKeyboardMarkup = keyboard
            )
            sendLog(createLogMessageForSuccessSave(responseBody, id, url), telegramClient)
        } else {
            if (responseBody.contains("429")) {
                sendText(id.toLong(), "Saving failed :( Limit of 10 articles per day has been reached. Need more articles? Simply write 'no limit' in the chat below", telegramClient)
            } else {
                sendText(
                    id.toLong(),
                    "Saving failed :( We're aware of this issue and working on it 💫",
                    telegramClient
                )
            }
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