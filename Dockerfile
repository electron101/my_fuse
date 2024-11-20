FROM ubuntu:20.04

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-setuptools \
    fuse \
    libfuse-dev \  
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Копирование исходников и Makefile
WORKDIR /usr/src/memfs
COPY src /usr/src/memfs/

# Сборка программы
RUN make

# Установка зависимостей для тестирования
WORKDIR /tests
COPY tests /tests/
RUN pip3 install -r /tests/requirements.txt

# Установка переменных окружения
ENV MOUNT_POINT=/mnt/memfs_mount_point
ENV FS_PATH=/usr/src/memfs/memfs

# Создание директории для монтирования
RUN mkdir -p $MOUNT_POINT

# Установка устройства /dev/fuse для контейнера
# RUN mknod /dev/fuse c 10 229 && chmod 666 /dev/fuse

# Запуск тестов
CMD pytest /tests/test_vfs.py -s

