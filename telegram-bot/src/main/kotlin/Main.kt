package goldenluk.readlaterbpt

import org.telegram.telegrambots.longpolling.TelegramBotsLongPollingApplication
import org.telegram.telegrambots.longpolling.util.DefaultGetUpdatesGenerator
import org.telegram.telegrambots.meta.TelegramUrl
import org.telegram.telegrambots.meta.exceptions.TelegramApiException

fun main() {

    try {
        val botKey = System.getenv("TELEGRAM_BOT_TOKEN")
        val botEnvironment = System.getenv("TELEGRAM_BOT_ENVIRONMENT")
        if (!botKey.isNullOrEmpty()) {
            println("Bot key loaded successfully!")
        } else {
            println("TELEGRAM_BOT_TOKEN is not set!")
        }
        val botsApplication = TelegramBotsLongPollingApplication()
        val bot = ReadLaterBot()
        if (botEnvironment == "prod") {
            botsApplication.registerBot(botKey, { TelegramUrl("https", "api.telegram.org", 443, false) }, DefaultGetUpdatesGenerator(), bot)
        } else {
            botsApplication.registerBot(botKey, { TelegramUrl("https", "api.telegram.org", 443, true) }, DefaultGetUpdatesGenerator(), bot)
        }
        //bot.notifyChangelog()

    } catch (e: TelegramApiException) {
        e.printStackTrace()
    }

    val dbHelper = DatabaseHelper()
    dbHelper.initClient()
}