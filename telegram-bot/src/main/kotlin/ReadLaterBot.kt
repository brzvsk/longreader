package goldenluk.readlaterbpt

import org.telegram.telegrambots.client.okhttp.OkHttpTelegramClient
import org.telegram.telegrambots.longpolling.util.LongPollingSingleThreadUpdateConsumer
import org.telegram.telegrambots.meta.api.objects.Update
import org.telegram.telegrambots.meta.api.objects.messageorigin.*
import org.telegram.telegrambots.meta.api.objects.replykeyboard.InlineKeyboardMarkup
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardButton
import org.telegram.telegrambots.meta.api.objects.replykeyboard.buttons.InlineKeyboardRow
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.*

class ReadLaterBot : LongPollingSingleThreadUpdateConsumer {

    private val telegramClient = OkHttpTelegramClient(System.getenv("READ_LATER_BOT_KEY").orEmpty())
    private val dbHelper = DatabaseHelper()

    override fun consume(update: Update?) {
        if (update == null) return

        if (update.hasCallbackQuery()) {
            val callbackQuery = update.callbackQuery

            val chatId = callbackQuery.message.chatId
            val queryId = callbackQuery.id
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
            return
        }

        if (update.hasMessage() && update.message.isCommand) {
            val message = update.message
            val fromId = message.from.id
            when (message.text) {
                "/start" -> sendText(fromId, "Start TBD", telegramClient)
                "/help" -> sendText(fromId, "Help TBD", telegramClient)
                "/all" -> sendAllBookmarks(fromId)
                "/clear_all" -> dbHelper.removeAllBookmarks(fromId.toString())
            }
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

        val date = LocalDateTime.now()
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

        sendText(fromId, successMessage, telegramClient)
    }

    private fun extractId(input: String): String? {
        val idParam = input.split("&").find { it.startsWith("id=") }
        return idParam?.substringAfter("id=")
    }

    fun notifyChangelog() {
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
    }
}