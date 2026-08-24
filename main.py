# main.py
import os
import sys
import time
import shutil
import traceback
from pathlib import Path

# Добавляем путь к папке classes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'classes'))

# Прямые импорты из папки classes
from classes.browser_manager import BrowserManager
from classes.video_loader import VideoLoader
from classes.email_manager import EmailManager
from classes.vizard_registrator import VizardRegistrator
from classes.email_confirmer import EmailConfirmer
from classes.vizard_manager import VizardManager
from classes.vizard_uploader import VizardUploader
from classes.vizard_template_manager import VizardTemplateManager
from classes.vizard_downloader import VizardDownloader

# Импортируем конфигурацию из ai_config
from ai_config import AIConfigBeast

# Импортируем конфиг
from config import Config


def mark_video_as_finished(video_path):
    """
    Переименовывает видео, добавляя _(finished) к имени файла
    """
    try:
        folder = os.path.dirname(video_path)
        filename = os.path.basename(video_path)
        name, ext = os.path.splitext(filename)

        new_filename = f"{name}_(finished){ext}"
        new_path = os.path.join(folder, new_filename)

        os.rename(video_path, new_path)
        print(f"   📝 Видео помечено как обработанное: {new_filename}")
        return new_path

    except Exception as e:
        print(f"   ⚠️ Не удалось переименовать видео: {e}")
        return video_path


def process_video_batch(browser, video_batch, batch_index, total_batches):
    """
    Обработка одной партии видео (до 3 видео) на одном аккаунте
    """
    print("\n" + "=" * 60)
    print(f"📦 ОБРАБОТКА ПАРТИИ {batch_index}/{total_batches}")
    print(f"📹 Видео в партии: {len(video_batch)}")
    print("=" * 60)

    email_manager = EmailManager(browser)
    if not email_manager.get_email():
        print("⚠️ Проблемы с получением email")
        return False, video_batch

    email = email_manager.get_email_address()
    if not email:
        print("❌ Email не получен")
        return False, video_batch

    registrator = VizardRegistrator(browser)
    if not registrator.register(email):
        print("⚠️ Проблемы с регистрацией")
        return False, video_batch

    confirmer = EmailConfirmer(browser)
    if not confirmer.confirm_email():
        print("⚠️ Проблемы с подтверждением email")
        return False, video_batch

    vizard_manager = VizardManager(browser)
    if not vizard_manager.refresh_vizard_page():
        print("⚠️ Проблемы с обновлением Vizard")
        return False, video_batch

    template_config = AIConfigBeast()
    uploader = VizardUploader(browser, config=template_config)

    if not uploader.upload_videos(video_batch):
        print("⚠️ Проблемы с загрузкой видео")
        return False, video_batch

    downloader = VizardDownloader(browser)
    if not downloader.download_all_videos():
        print("⚠️ Проблемы со скачиванием видео")
        return False, video_batch

    finished_videos = []
    for video_path in video_batch:
        new_path = mark_video_as_finished(video_path)
        finished_videos.append(new_path)

    print(f"\n✅ Партия {batch_index}/{total_batches} успешно обработана!")
    return True, finished_videos


def get_videos_to_process(video_loader):
    """
    Получает список видео, которые еще не обработаны
    (не содержат _(finished) в имени)
    """
    all_videos = video_loader.get_video_files()

    videos_to_process = []
    for video in all_videos:
        filename = os.path.basename(video)
        if "_(finished)" not in filename:
            videos_to_process.append(video)
        else:
            print(f"   ⏭️ Пропускаем уже обработанное видео: {filename}")

    return videos_to_process


def main():
    """Главная функция"""
    print("\n" + "🚀" * 15)
    print("НАЧАЛО МНОГОПРОХОДНОЙ АВТОМАТИЗАЦИИ")
    print("🚀" * 15 + "\n")

    # 1. Загрузка всех видео из папки videos_input
    video_loader = VideoLoader("videos_input")
    if not video_loader.load_videos():
        print("❌ Нет видео для обработки")
        return

    # 2. Получаем только НЕобработанные видео (без _(finished))
    print("\n📌 Проверка обработанных видео...")
    all_videos = get_videos_to_process(video_loader)

    if not all_videos:
        print("✅ Все видео уже обработаны!")
        return

    print(f"\n📊 Осталось видео для обработки: {len(all_videos)}")

    # 3. Получаем максимальное количество видео на аккаунт
    max_per_account = 3
    print(f"📊 Максимум видео на один аккаунт: {max_per_account}")

    # 4. Разбиваем видео на партии
    batches = []
    for i in range(0, len(all_videos), max_per_account):
        batch = all_videos[i:i + max_per_account]
        batches.append(batch)

    total_batches = len(batches)
    print(f"📊 Всего партий для обработки: {total_batches}\n")

    # 5. Обрабатываем каждую партию
    for batch_index, video_batch in enumerate(batches, 1):
        print("\n" + "🔥" * 15)
        print(f"НАЧАЛО ОБРАБОТКИ ПАРТИИ {batch_index}/{total_batches}")
        print("🔥" * 15)

        browser = BrowserManager(speed=Config.SPEED)
        if not browser.init_browser():
            print("❌ Не удалось запустить браузер")
            continue

        success, processed_videos = process_video_batch(
            browser=browser,
            video_batch=video_batch,
            batch_index=batch_index,
            total_batches=total_batches
        )

        browser.close()

        if not success:
            print(f"⚠️ Партия {batch_index} обработана с ошибками")
        else:
            print(f"✅ Партия {batch_index} успешно обработана!")

        if batch_index < total_batches:
            print(f"\n⏳ Ожидание 10 секунд перед следующей партией...")
            time.sleep(10)

    # 6. Итоговый статус
    video_loader.load_videos()
    remaining = get_videos_to_process(video_loader)

    print("\n" + "=" * 60)
    if remaining:
        print("⚠️ НЕ ВСЕ ВИДЕО ОБРАБОТАНЫ!")
        print(f"📁 Осталось видео: {len(remaining)}")
    else:
        print("🎉 ВСЕ ВИДЕО УСПЕШНО ОБРАБОТАНЫ!")
    print("=" * 60)
    print(f"📦 Всего использовано аккаунтов: {total_batches}")
    print(f"📂 Видео сохранены в папку: videos_output/")
    print("=" * 60)


# ================================================================
# ТОЧКА ВХОДА С ОБРАБОТКОЙ ОШИБОК И УДЕРЖАНИЕМ КОНСОЛИ
# ================================================================

if __name__ == "__main__":
    try:
        main()

        # Если скрипт дошел до конца - ждем нажатия Enter
        print("\n" + "=" * 60)
        print("✅ СКРИПТ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 60)

        # Проверяем, запущен ли как .exe
        if getattr(sys, 'frozen', False):
            input("\n📌 Нажмите Enter для выхода...")

    except KeyboardInterrupt:
        print("\n\n⚠️ Скрипт остановлен пользователем")
        if getattr(sys, 'frozen', False):
            input("\n📌 Нажмите Enter для выхода...")

    except Exception as e:
        print("\n" + "❌" * 30)
        print(f"❌ НЕПРЕДВИДЕННАЯ ОШИБКА:")
        print(f"   {e}")
        print("\n📋 ПОДРОБНОСТИ:")
        traceback.print_exc()
        print("❌" * 30)

        # Если запущен как .exe - ждем нажатия Enter
        if getattr(sys, 'frozen', False):
            input("\n📌 Нажмите Enter для выхода...")
        else:
            # Если запущен как .py - можно не ждать, но для удобства тоже ждем
            input("\n📌 Нажмите Enter для выхода...")