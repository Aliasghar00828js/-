#include <iostream>
#include <string>
#include <cstdlib>
#include <thread>
#include <tgbot/tgbot.h>
#define CPPHTTPLIB_OPENSSL_SUPPORT
#include <httplib.h>

using namespace std;
using namespace TgBot;

// این تابع پورت سرور را بیدار نگه می‌دارد تا سرور ارتباط شبکه ربات را قطع نکند
void run_health_check_server() {
    httplib::Server svr;
    svr.Get("/", [](const httplib::Request&, httplib::Response& res) {
        res.set_content("C++ Bot is active!", "text/plain");
    });
    
    // خواندن پورتی که ریلووی اختصاص میده (معمولا 8080)
    const char* port_env = getenv("PORT");
    int port = port_env ? stoi(port_env) : 8080;
    
    cout << "Health check server listening on port " << port << endl;
    svr.listen("0.0.0.0", port);
}

int main() {
    const char* token_env = getenv("BOT_TOKEN");
    if (!token_env) {
        cerr << "Error: BOT_TOKEN is not set!" << endl;
        return 1;
    }
    string botToken(token_env);

    // روشن کردن سرور وب در پس‌زمینه برای تایید صحت دپلوی
    thread env_thread(run_health_check_server);
    env_thread.detach();

    Bot bot(botToken);

    bot.getEvents().onCommand("start", [&bot](Message::Ptr message) {
        bot.getApi().sendMessage(message->chat->id, "سلام! ربات فوق‌العاده سریع C++ شما با موفقیت متصل شد و پاسخ می‌دهد! 🚀");
    });

    try {
        cout << "C++ Bot started long polling..." << endl;
        TgLongPoll longPoll(bot);
        while (true) {
            longPoll.start();
        }
    } catch (TgException& e) {
        cerr << "Telegram Error: " << e.what() << endl;
    }

    return 0;
}
