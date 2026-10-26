# ai_config.py
import json
import os


class AIConfig:
    """Глобальная конфигурация. Редактируется из UI, сохраняется в config.json."""

    # --- AI параметры ---
    TEMPLATE_NAME = "Modern"
    CLIP_LENGTH = 2
    LANGUAGE = "Russian (Pусский)"
    MODEL = "Model v2"
    ENABLE_EMOJIS = True
    ENABLE_KEYWORDS = True
    ENABLE_B_ROLLS = False
    ENABLE_SILENCE_REMOVAL = True
    ENABLE_AUTO_CENSOR = False

    # --- Лимиты и таймауты ---
    MAX_VIDEOS = 3               # видео на один аккаунт
    UPLOAD_WAIT_TIME = 120       # сек ожидания загрузки на сервер

    # --- Временная почта ---
    # Домен (без @). Пользователь меняет через UI.
    TEMP_MAIL_DOMAIN = "deepmails.org"
    # Последний сгенерированный email (для отображения, перезаписывается каждую партию)
    TEMP_EMAIL = ""

    # --- Скорость ---
    SPEED = "medium"

    _CONFIG_PATH = "config.json"

    @classmethod
    def to_dict(cls):
        return {
            k: getattr(cls, k) for k in dir(cls)
            if k.isupper() and not k.startswith("_")
        }

    @classmethod
    def from_dict(cls, data: dict):
        for k, v in data.items():
            if k.isupper() and hasattr(cls, k):
                setattr(cls, k, v)

    @classmethod
    def save(cls, path=None):
        path = path or cls._CONFIG_PATH
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cls.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path=None):
        path = path or cls._CONFIG_PATH
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    cls.from_dict(json.load(f))
            except Exception as e:
                print(f"⚠️ Не удалось загрузить config.json: {e}")
        return cls


AIConfigBeast = AIConfig