#include <iostream>
#include <string>
#include <cstdlib>
#include <tgbot/tgbot.h>

using namespace std;
using namespace TgBot;

int main() {
    // خواندن توکن از متغیر محیطی Railway
    const char* token_env = getenv("BOT_TOKEN");
    if (!token_env) {
        cerr << "Error: BOT_TOKEN is not set in Railway variables!" << endl;
        return 1;
    }
    string botToken(token_env);

    // راه‌اندازی ربات
    Bot bot(botToken);

    // تعریف عملکرد دستور /start
    bot.getEvents().onCommand("start", [&bot](Message::Ptr message) {
        bot.getApi().sendMessage(message->chat->id, "سلام! ربات فوق‌العاده سریع C++ شما با موفقیت استارت شد. 🚀");
    });

    try {
        cout << "Bot username: " << bot.getApi().getMe()->username << endl;
        cout << "C++ Bot is running (Long Polling)..." << endl;
        
        // شروع گوش به زنگ بودن ربات برای پیام‌ها
        TgLongPoll longPoll(bot);
        while (true) {
            longPoll.start();
        }
    } catch (TgException& e) {
        cerr << "Telegram Error: " << e.what() << endl;
    }

    return 0;
}
