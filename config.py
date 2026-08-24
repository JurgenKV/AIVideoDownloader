# config.py
class Config:
    """Конфигурация приложения"""

    # Настройки скорости
    SPEED = "medium"  # "fast", "medium", "slow"

    # Путь к папкам с видео
    VIDEO_INPUT_FOLDER = "videos_input"   # Папка с исходными видео
    VIDEO_OUTPUT_FOLDER = "videos_output" # Папка для скачанных видео

    # URL-адреса
    TEMP_MAIL_URL = "https://www.temporary-mail.net/"
    VIZARD_URL = "https://vizard.ai/upload?from=home_upload"

    # Таймауты
    TIMEOUT = 30

    # Ожидание обновления почты (сек)
    REFRESH_WAIT = 6

    # Настройки Chrome
    CHROME_OPTIONS = {
        "incognito": True,
        "window_size": "1920,1080",
        "start_maximized": True
    }