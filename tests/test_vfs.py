import os
import subprocess
import pytest
import threading

# MOUNT_POINT = "/home/doctor/myfs_mount"  # Точка монтирования FUSE
# FS_PATH = "/home/doctor/CODING/sbertech_2024/memfs-fuse/memfs"  # Путь к скомпилированной FUSE программе
MOUNT_POINT = os.getenv("MOUNT_POINT", "/home/doctor/myfs_mount")  # Точка монтирования FUSE
FS_PATH = os.getenv("FS_PATH", "/usr/src/memfs/memfs")  # Путь к скомпилированной FUSE программе

# Функция для монтирования файловой системы
def mount_fs():
    if not os.path.exists(MOUNT_POINT):
        os.makedirs(MOUNT_POINT)
    print(f"Монтируем файловую систему в точку {MOUNT_POINT}")
    result = subprocess.run([FS_PATH, MOUNT_POINT], check=False, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Ошибка при монтировании: {result.stderr.decode()}")
    else:
        print("Монтирование прошло успешно")

# Функция для размонтирования файловой системы
def umount_fs():
    print(f"Размонтируем файловую систему из точки {MOUNT_POINT}")
    # result = subprocess.run(["fusermount3", "-u", MOUNT_POINT], check=False, stderr=subprocess.PIPE)
    result = subprocess.run(["fusermount", "-u", MOUNT_POINT], check=False, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Ошибка при размонтировании: {result.stderr.decode()}")
    else:
        print("Размонтирование прошло успешно")

# Фикстура для подготовки точки монтирования
@pytest.fixture(scope="function", autouse=True)
def prepare_mount():
    # Убедимся, что точка монтирования размонтирована перед каждым тестом
    if os.path.ismount(MOUNT_POINT):
        umount_fs()
    
    # Удалим точку монтирования (если она существует) и создадим ее заново
    if os.path.exists(MOUNT_POINT):
        subprocess.run(["rm", "-rf", MOUNT_POINT], check=True)
    os.makedirs(MOUNT_POINT)
    print(f"Точка монтирования {MOUNT_POINT} создана заново.")
    
    # Монтируем файловую систему
    mount_fs()

    # Возвращаем управление тесту
    yield

    # Размонтируем файловую систему после выполнения теста
    umount_fs()

# Функция для отображения содержимого каталога
def print_directory_contents(path):
    print(f"Содержимое каталога {path}:")
    for root, dirs, files in os.walk(path):
        for name in files:
            print(f"Файл: {os.path.join(root, name)}")
        for name in dirs:
            print(f"Каталог: {os.path.join(root, name)}")


# ===========================================
# 1. Создание файлов и каталогов:
# ===========================================

# Тест создания файла
def test_create_file():
    print("\nТест: создание файла")

    mount_fs()

    filename = os.path.join(MOUNT_POINT, "file1.txt")
    
    # Создаем файл
    subprocess.run(["touch", filename], check=True)
    print(f"Создан файл: {filename}")

    # Проверяем существование файла
    assert os.path.exists(filename)
    print(f"Файл {filename} существует.")

    # Печатаем содержимое монтированного каталога после создания файла
    print_directory_contents(MOUNT_POINT)

    umount_fs()

# Тест создания каталога
def test_create_directory():
    print("\nТест: создание каталога")

    mount_fs()

    dir_path = os.path.join(MOUNT_POINT, "dir1")
    
    # Создаем каталог
    subprocess.run(["mkdir", dir_path], check=True)
    print(f"Создан каталог: {dir_path}")

    # Проверяем существование каталога
    assert os.path.isdir(dir_path)
    print(f"Каталог {dir_path} существует.")

    # Печатаем содержимое монтированного каталога после создания каталога
    print_directory_contents(MOUNT_POINT)

    umount_fs()

# Тест создания иерархической структуры каталогов
def test_create_hierarchical_directories():
    print("\nТест: создание иерархической структуры каталогов")

    mount_fs()

    dir_path = os.path.join(MOUNT_POINT, "parent_dir", "child_dir")
    
    # Создаем иерархию каталогов
    subprocess.run(["mkdir", "-p", dir_path], check=True)
    print(f"Создана иерархия каталогов: {dir_path}")

    # Проверяем существование каталогов
    assert os.path.isdir(os.path.join(MOUNT_POINT, "parent_dir"))
    assert os.path.isdir(dir_path)
    print(f"Каталоги {os.path.join(MOUNT_POINT, 'parent_dir')} и {dir_path} существуют.")

    # Печатаем содержимое монтированного каталога после создания каталогов
    print_directory_contents(MOUNT_POINT)

    umount_fs()

# ===========================================
# 2. Удаление файлов и каталогов:
# ===========================================

# Тест удаления файла
def test_delete_file():
    print("\nТест: удаление файла")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "file_to_delete.txt")
    
    # Создаем файл
    subprocess.run(["touch", filename], check=True)
    print(f"Создан файл для удаления: {filename}")
    
    # Удаляем файл
    subprocess.run(["rm", filename], check=True)
    print(f"Удален файл: {filename}")
    
    # Проверяем, что файл удален
    assert not os.path.exists(filename)
    print(f"Файл {filename} удален.")

    umount_fs()

# Тест удаления пустого каталога
def test_delete_empty_directory():
    print("\nТест: удаление пустого каталога")
    mount_fs()

    dir_path = os.path.join(MOUNT_POINT, "empty_dir")
    
    # Создаем каталог
    subprocess.run(["mkdir", dir_path], check=True)
    print(f"Создан каталог для удаления: {dir_path}")
    
    # Удаляем каталог
    subprocess.run(["rmdir", dir_path], check=True)
    print(f"Удален каталог: {dir_path}")
    
    # Проверяем, что каталог удален
    assert not os.path.isdir(dir_path)
    print(f"Каталог {dir_path} удален.")

    umount_fs()

# Тест ошибки при удалении несуществующего файла
def test_delete_nonexistent_file():
    print("\nТест: ошибка при удалении несуществующего файла")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "nonexistent_file.txt")
    
    # Пробуем удалить несуществующий файл и проверяем, что ошибка не возникает
    result = subprocess.run(["rm", filename], stderr=subprocess.PIPE)
    print(f"Попытка удалить несуществующий файл: {filename}")
    assert result.returncode != 0  # Ошибка при удалении несуществующего файла

    umount_fs()

# Тест ошибки при удалении несуществующего каталога
def test_delete_nonexistent_directory():
    print("\nТест: ошибка при удалении несуществующего каталога")
    mount_fs()

    dir_path = os.path.join(MOUNT_POINT, "nonexistent_dir")
    
    # Пробуем удалить несуществующий каталог и проверяем, что ошибка не возникает
    result = subprocess.run(["rmdir", dir_path], stderr=subprocess.PIPE)
    print(f"Попытка удалить несуществующий каталог: {dir_path}")
    assert result.returncode != 0  # Ошибка при удалении несуществующего каталога

    umount_fs()


# ===========================================
# 3. Чтение файлов:
# ===========================================
    
# Тест чтения файла
def test_read_file():
    print("\nТест: чтение файла")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "test_file.txt")

    # Создаем файл и записываем в него данные
    with open(filename, "w") as f:
        f.write("Hello, World!")
    print(f"Создан файл: {filename} с содержимым 'Hello, World!'")

    # Читаем файл
    result = subprocess.run(["cat", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Содержимое файла {filename}: {result.stdout.decode()}")

    # Проверяем, что содержимое файла соответствует
    # assert result.stdout.decode() == "Hello, World!\n"
    assert result.stdout.decode() == "Hello, World!"

    umount_fs()


# Тест чтения данных с использованием смещения
def test_read_file_with_offset():
    print("\nТест: чтение файла с использованием смещения")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "test_file_with_offset.txt")

    # Создаем файл и записываем в него данные с помощью Python
    with open(filename, "w") as f:
        f.write("0123456789")
    print(f"Создан файл: {filename} с содержимым '0123456789'")

    # Читаем данные с смещением, используя команду dd
    result = subprocess.run(
        ["dd", f"if={filename}", "bs=1", "skip=5", "count=5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    print(f"Чтение файла с смещением: {result.stdout.decode()}")

    # Проверяем, что содержимое файла с смещением корректно
    assert result.stdout.decode() == "56789"

    umount_fs()


# ===========================================
# 4. Запись файлов:
# ===========================================

# Тест записи в файл
def test_write_file():
    print("\nТест: запись в файл")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "write_test_file.txt")

    # Записываем в файл с использованием subprocess и перенаправления
    subprocess.run(f"echo 'Test Data' > {filename}", shell=True, check=True)
    print(f"Записано в файл {filename}: 'Test Data'")

    # Читаем файл и проверяем содержимое
    result = subprocess.run(["cat", filename], stdout=subprocess.PIPE)
    print(f"Содержимое файла {filename}: {result.stdout.decode()}")

    # Проверяем, что содержимое файла соответствует ожидаемому
    assert result.stdout.decode() == "Test Data\n"

    umount_fs()


# Тест добавления данных в файл
def test_append_to_file():
    print("\nТест: добавление данных в файл")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "append_test_file.txt")

    # Создаем файл и записываем в него начальные данные
    subprocess.run(f"echo 'Hello' > {filename}", shell=True, check=True)
    print(f"Создан файл {filename} с содержимым 'Hello'")

    # Добавляем данные в файл
    subprocess.run(f"echo 'World' >> {filename}", shell=True, check=True)
    print(f"Добавлены данные в файл {filename}: 'World'")

    # Читаем файл и проверяем содержимое
    result = subprocess.run(["cat", filename], stdout=subprocess.PIPE)
    print(f"Содержимое файла {filename}: {result.stdout.decode()}")

    # Проверяем, что содержимое файла соответствует
    assert result.stdout.decode() == "Hello\nWorld\n"

    umount_fs()


# ===========================================
# 5. Права доступа:
# ===========================================

# Тест чтения файла с правами доступа
def test_read_file_permissions():
    print("\nТест: чтение файла с правами доступа")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "read_permission_test.txt")
    
    # Создаем файл с правами доступа
    subprocess.run(["touch", filename], check=True)
    subprocess.run(["chmod", "444", filename], check=True)  # Только чтение
    print(f"Файл {filename} создан с правами только для чтения")
    
    # Пробуем прочитать файл
    result = subprocess.run(["cat", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Содержимое файла {filename}: {result.stdout.decode()}")
    
    # Проверяем, что файл можно прочитать
    assert result.stdout.decode() == ""

    umount_fs()

# Тест записи в файл с правами доступа
def test_write_file_permissions():
    print("\nТест: запись в файл с правами доступа")
    mount_fs()

    filename = os.path.join(MOUNT_POINT, "write_permission_test.txt")

    # Создаем файл с правами доступа
    subprocess.run(["touch", filename], check=True)
    subprocess.run(["chmod", "444", filename], check=True)  # Только чтение
    print(f"Файл {filename} создан с правами только для чтения")

    # Пробуем записать в файл с помощью команды tee
    result = subprocess.run(f'echo "Hello" | tee {filename} > /dev/null', shell=True, stderr=subprocess.PIPE)
    print(f"Попытка записи в файл {filename}")

    # Проверяем, что произошла ошибка записи (т.к. файл только для чтения)
    assert result.returncode != 0  # Ожидаем ошибку при записи в файл с правами только для чтения

    umount_fs()


# ===========================================
# 6. Обработка одновременных запросов:
# ===========================================

# Пример теста для одновременного чтения и записи
def test_concurrent_read_write():
    print("\nТест: одновременное чтение и запись")

    # Используем Lock для синхронизации
    lock = threading.Lock()
    
    filename = os.path.join(MOUNT_POINT, "concurrent_test.txt")

    def write_file():
        with lock:  # Используем блокировку для синхронизации
            print(f"Записано в файл {filename}: 'Data'")
            with open(filename, "w") as f:
                f.write("Data")

    def read_file():
        with lock:  # Используем блокировку для синхронизации
            print(f"Чтение из файла {filename}")
            with open(filename, "r") as f:
                data = f.read()
            print(f"Содержимое файла {filename}: {data}")
            assert data == "Data"

    mount_fs()

    # Запускаем два потока: один для записи, второй для чтения
    writer_thread = threading.Thread(target=write_file)
    reader_thread = threading.Thread(target=read_file)

    writer_thread.start()
    reader_thread.start()

    writer_thread.join()
    reader_thread.join()

    umount_fs()
