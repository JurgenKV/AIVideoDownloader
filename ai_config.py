# ai_config.py
"""
Конфигурация для настройки AI шаблонов Vizard
"""


class AIConfig:
    """Базовые настройки AI шаблона"""

    # ==================== НАСТРОЙКИ КОЛИЧЕСТВА ВИДЕО ====================
    # Максимальное количество видео для загрузки на один аккаунт
    MAX_VIDEOS = 3  # По умолчанию 3 видео

    # ==================== НАСТРОЙКИ ДЛИТЕЛЬНОСТИ ====================
    CLIP_LENGTH = 0  # <30s

    # ==================== НАСТРОЙКИ ШАБЛОНА ====================
    TEMPLATE_NAME = "Mr. Beast"

    # ==================== AI ОПЦИИ ====================
    ENABLE_EMOJIS = True
    ENABLE_KEYWORDS = True
    ENABLE_B_ROLLS = False
    ENABLE_SILENCE_REMOVAL = False
    ENABLE_AUTO_CENSOR = True

    # ==================== ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ ====================
    LANGUAGE = "Russian (Pусский)"
    MODEL = "Model v2"

    # ==================== ВРЕМЯ ОЖИДАНИЯ ЗАГРУЗКИ ====================
    UPLOAD_WAIT_TIME = 60  # 60 секунд


class AIConfigBeast(AIConfig):
    """Стиль Mr. Beast"""
    MAX_VIDEOS = 3
    CLIP_LENGTH = 0
    TEMPLATE_NAME = "Mr. Beast"
    ENABLE_EMOJIS = True
    ENABLE_KEYWORDS = True
    ENABLE_B_ROLLS = False
    ENABLE_SILENCE_REMOVAL = False
    ENABLE_AUTO_CENSOR = True
    UPLOAD_WAIT_TIME = 60