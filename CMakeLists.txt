cmake_minimum_required(VERSION 3.10)
project(TelegramBotCPP)

set(CMAKE_CXX_STANDARD 17)

# ۱. دانلود کتابخانه ربات تلگرام
include(FetchContent)
FetchContent_Declare(
    tgbot
    GIT_REPOSITORY https://github.com/reo7sp/tgbot-cpp.git
    GIT_TAG master
)
FetchContent_MakeAvailable(tgbot)

# ۲. دانلود کتابخانه وب‌سرور سبک برای پورت ریلووی
FetchContent_Declare(
    httplib
    GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
    GIT_TAG v0.15.3
)
FetchContent_MakeAvailable(httplib)

# ۳. معرفی فایل اجرایی
add_executable(my_bot main.cpp)

# ۴. اضافه کردن مسیر پوشه httplib به کامپایلر (حل قطعی ارور عدم شناسایی فایل)
target_include_directories(my_bot PRIVATE ${httplib_SOURCE_DIR})

# ۵. لینک کردن کتابخانه‌های سیستم
target_link_libraries(my_bot TgBot ssl crypto curl z pthread)
