# classes/video_loader.py
import os
import re
import sys
from pathlib import Path

# Импортируем утилиты для работы с путями
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.path_utils import get_base_dir, get_videos_input_path


def natural_sort_key(text):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    return [convert(c) for c in re.split('([0-9]+)', text)]


class VideoLoader:
    """Класс для загрузки видео из папки"""

    def __init__(self, folder_name=None):
        # Получаем базовую директорию
        self.base_dir = get_base_dir()

        # Используем правильный путь к папке
        if folder_name:
            self.folder_path = os.path.join(self.base_dir, folder_name)
        else:
            self.folder_path = get_videos_input_path()

        self.video_files = []

    def load_videos(self):
        """Загрузка всех видео из папки с естественной сортировкой"""
        print("=" * 50)
        print("ШАГ 1: Загрузка видео из папки")
        print("=" * 50)

        if not os.path.exists(self.folder_path):
            print(f"❌ Папка '{self.folder_path}' не найдена!")
            os.makedirs(self.folder_path)
            print(f"✅ Папка создана: {self.folder_path}")
            print(f"📁 Положите видео файлы в папку: {self.folder_path}")
            return False

        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        self.video_files = []

        for file in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in video_extensions:
                    self.video_files.append(file_path)

        if not self.video_files:
            print(f"❌ В папке '{self.folder_path}' нет видео файлов!")
            print(f"📁 Поддерживаемые форматы: {', '.join(video_extensions)}")
            return False

        self.video_files.sort(key=lambda x: natural_sort_key(os.path.basename(x)))

        print(f"✅ Найдено видео файлов: {len(self.video_files)}")
        for i, video in enumerate(self.video_files, 1):
            file_size = os.path.getsize(video) / (1024 * 1024)
            print(f"   {i}. {os.path.basename(video)} ({file_size:.1f} MB)")

        return True

    def get_video_files(self):
        return self.video_files

    def get_folder_path(self):
        return self.folder_path