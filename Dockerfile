FROM ubuntu:22.04

# جلوگیری از توقف نصب به خاطر درخواست‌های تایم‌زون و کیبورد ابونتو
ENV DEBIAN_FRONTEND=noninteractive

# نصب تمامی پیش‌نیازهای حیاتی با دقت کامل (شامل curl و zlib)
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
    && rm -rf /lib/apt/lists/*

WORKDIR /app
COPY . .

# ساخت پوشه و کامپایل کدها
RUN mkdir -p build && cd build && cmake .. && make

# اجرای ربات پس از اتمام بیلد
CMD ["./build/my_bot"]
