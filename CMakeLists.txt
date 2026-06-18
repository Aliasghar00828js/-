cmake_minimum_required(VERSION 3.10)
project(TelegramBotCPP)

set(CMAKE_CXX_STANDARD 17)

# دانلود خودکار کتابخانه رسمی و سریع TgBot
include(FetchContent)
FetchContent_Declare(
    tgbot
    GIT_REPOSITORY https://github.com/reo7sp/tgbot-cpp.git
    GIT_TAG master
)
FetchContent_MakeAvailable(tgbot)

# معرفی فایل اصلی کد
add_executable(my_bot main.cpp)

# لینک کردن کتابخانه‌های مورد نیاز برای شبکه و امنیت
target_link_libraries(my_bot TgBot ssl crypto curl z pthread)
