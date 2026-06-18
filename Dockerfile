FROM ubuntu:22.04

# نصب تمام پیش‌نیازهای لازم برای کامپایل C++
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    git \
    libboost-all-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    zlib1g-dev \
    && rm -rf /lib/apt/lists/*

WORKDIR /app
COPY . .

# کامپایل برنامه
RUN mkdir build && cd build && cmake .. && make

# دستور اجرای ربات
CMD ["./build/my_bot"]
