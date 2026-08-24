# utils/path_utils.py
import os
import sys


def get_base_dir():
    """
    Возвращает правильную базовую директорию:
    - Для .exe: папка, где находится .exe
    - Для скрипта: папка, где находится .py
    """
    if getattr(sys, 'frozen', False):
        # Запущено как .exe (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Запущено как .py
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_app_path():
    """Возвращает путь к папке приложения"""
    return get_base_dir()


def get_videos_input_path():
    """Путь к папке с исходными видео"""
    return os.path.join(get_base_dir(), "videos_input")


def get_videos_output_path():
    """Путь к папке со скачанными видео"""
    return os.path.join(get_base_dir(), "videos_output")


def get_drivers_path():
    """Путь к папке с драйверами"""
    return os.path.join(get_base_dir(), "drivers")


def get_chromedriver_path():
    """Поиск ChromeDriver в папке drivers или корне проекта"""
    base_dir = get_base_dir()

    # Список возможных имен файлов ChromeDriver
    driver_names = [
        "chromedriver.exe",  # Windows
        "chromedriver",  # Linux/Mac
        "chromedriver_win32.exe",
        "chromedriver_linux64",
        "chromedriver_mac64"
    ]

    # Проверяем папку drivers/
    drivers_folder = os.path.join(base_dir, "drivers")
    if os.path.exists(drivers_folder):
        for name in driver_names:
            driver_path = os.path.join(drivers_folder, name)
            if os.path.exists(driver_path):
                return driver_path

    # Проверяем корневую папку
    for name in driver_names:
        driver_path = os.path.join(base_dir, name)
        if os.path.exists(driver_path):
            return driver_path

    return None