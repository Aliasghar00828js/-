FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# اضافه کردن ابزار wget به لیست نصب
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    make \
    git \
    pkg-config \
    libboost-all-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    zlib1g-dev \
    wget \
    && rm -rf /lib/apt/lists/*

# دانلود مستقیم فایل httplib در پوشه مرکزی و پیش‌فرض کامپایلر
RUN wget https://raw.githubusercontent.com/yhirose/cpp-httplib/v0.15.3/httplib.h -O /usr/include/httplib.h

WORKDIR /app
COPY . .

RUN mkdir -p build && cd build && cmake .. && make

CMD ["./build/my_bot"]
