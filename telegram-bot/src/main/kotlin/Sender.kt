package goldenluk.readlaterbpt

import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.meta.api.methods.send.SendMessage
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

    // Execute the request
    client.newCall(request).execute().use { response: Response ->
        if (response.isSuccessful) {
            sendText(id.toLong(), sentToParserSuccessMessage, telegramClient)
            println("Response: ${response.body?.string()}")
        } else {
            sendText(id.toLong(), "Saving is failed :( We're aware of this issue and working on it 💫", telegramClient)
            println("Request failed: ${response.code}")
        }
    }
}