cmake_minimum_required(VERSION 3.10)
project(TelegramBotCPP)

set(CMAKE_CXX_STANDARD 17)

# دانلود کتابخانه ربات تلگرام
include(FetchContent)
FetchContent_Declare(
    tgbot
    GIT_REPOSITORY https://github.com/reo7sp/tgbot-cpp.git
    GIT_TAG master
)
FetchContent_MakeAvailable(tgbot)

# دانلود یک کتابخانه وب‌سرور بسیار سبک برای فعال نگه داشتن پورت ریلووی
FetchContent_Declare(
    httplib
    GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
    GIT_TAG v0.15.3
)
FetchContent_MakeAvailable(httplib)

add_executable(my_bot main.cpp)
target_link_libraries(my_bot TgBot ssl crypto curl z pthread)
