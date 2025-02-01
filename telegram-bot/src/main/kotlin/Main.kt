package goldenluk.readlaterbpt

import org.telegram.telegrambots.longpolling.TelegramBotsLongPollingApplication
import org.telegram.telegrambots.meta.exceptions.TelegramApiException

fun main() {

    try {
        val botKey = System.getenv("READ_LATER_BOT_KEY")
        if (!botKey.isNullOrEmpty()) {
            println("Bot key loaded successfully!")
        } else {
            println("BOT_KEY is not set!")
        }
        val botsApplication = TelegramBotsLongPollingApplication()
        val bot = ReadLaterBot()
        botsApplication.registerBot(botKey, bot)
        //bot.notifyChangelog()

    } catch (e: TelegramApiException) {
        e.printStackTrace()
    }

    val dbHelper = DatabaseHelper()
    dbHelper.initClient()
}