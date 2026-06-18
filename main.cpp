#include <iostream>
#include <string>
#include <cstdlib>
#include <tgbot/tgbot.h>

using namespace std;
using namespace TgBot;

int main() {
    // خواندن توکن از متغیرهای Railway
    const char* token_env = getenv("BOT_TOKEN");
    if (!token_env) {
        cerr << "Error: BOT_TOKEN is not set!" << endl;
        return 1;
    }
    string botToken(token_env);

    Bot bot(botToken);

    // رفتار ربات هنگام زدن دستور /start
    bot.getEvents().onCommand("start", [&bot](Message::Ptr message) {
        bot.getApi().sendMessage(message->chat->id, "سلام! ربات فوق‌العاده سریع C++ شما روشن است و کار می‌کند. 🚀");
    });

    try {
        cout << "C++ Bot is running via Long Polling..." << endl;
        TgLongPoll longPoll(bot);
        while (true) {
            longPoll.start();
        }
    } catch (TgException& e) {
        cerr << "Telegram Error: " << e.what() << endl;
    }

    return 0;
}
