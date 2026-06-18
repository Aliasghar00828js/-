#include <iostream>
#include <string>
#include <cstdlib>
#include <thread>
#include <tgbot/tgbot.h>
#include <httplib.h>

using namespace std;
using namespace TgBot;

// سرور کمکی ساده (فقط HTTP) برای بیدار نگه داشتن پورت اختصاصی Railway
void run_health_check_server() {
    httplib::Server svr;
    svr.Get("/", [](const httplib::Request&, httplib::Response& res) {
        res.set_content("C++ Telegram Bot is running perfectly!", "text/plain");
    });
    
    const char* port_env = getenv("PORT");
    int port = port_env ? stoi(port_env) : 8080;
    
    cout << "Health check server online on port " << port << endl;
    svr.listen("0.0.0.0", port);
}

int main() {
    // خواندن توکن امنیت
    const char* token_env = getenv("BOT_TOKEN");
    if (!token_env) {
        cerr << "Error: BOT_TOKEN variable is empty!" << endl;
        return 1;
    }
    string botToken(token_env);

    // راه اندازی وب‌سرور در یک ترد مستقل
    thread env_thread(run_health_check_server);
    env_thread.detach();

    // ایجاد ربات با تنظیمات پیش‌فرض شبکه
    Bot bot(botToken);

    // تعریف عملکرد پایه دستور استارت
    bot.getEvents().onCommand("start", [&bot](Message::Ptr message) {
        try {
            bot.getApi().sendMessage(message->chat->id, "سلام! ربات C++ با سرعت نور متصل شد و آماده کار است! 🚀");
        } catch (exception& e) {
            cerr << "Error inside start command: " << e.what() << endl;
        }
    });

    try {
        cout << "Testing connection to Telegram servers..." << endl;
        // گرفتن مشخصات ربات برای اطمینان از صحت اتصال شبکه
        User::Ptr me = bot.getApi().getMe();
        cout << "Connected successfully! Bot Username: @" << me->username << endl;
        
        cout << "C++ Bot started long polling safely..." << endl;
        TgLongPoll longPoll(bot);
        while (true) {
            longPoll.start();
        }
    } catch (TgException& e) {
        cerr << "Telegram Core Error: " << e.what() << endl;
    } catch (exception& e) {
        cerr << "Standard System Error: " << e.what() << endl;
    }

    return 0;
}
