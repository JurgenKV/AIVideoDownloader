# classes/vizard_downloader.py (только измененная часть __init__)
import os
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
# Импортируем pywinauto для работы с Windows-диалогами
try:
    from pywinauto import Application
    from pywinauto.timings import Timings
    from pywinauto.keyboard import send_keys, parse_keys

    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("⚠️ pywinauto не установлена. Установите: pip install pywinauto")


class VizardDownloader:
    """Класс для скачивания видео из Vizard"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait

        # Папка для скачиваний (из браузера)
        self.downloads_dir = self.browser.download_dir

        # Создаем папку если её нет
        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)
            print(f"📁 Создана папка для скачиваний: {self.downloads_dir}")

        # Настройка pywinauto
        if PYWINAUTO_AVAILABLE:
            Timings.slow()
            print("✅ pywinauto инициализирована")

    def _handle_save_file_dialog(self, file_path, timeout=15):
        """Обработка диалога сохранения файла (Save As)"""
        if not PYWINAUTO_AVAILABLE:
            print("   ⚠️ pywinauto не установлена")
            return False

        try:
            print(f"   ⏳ Ожидание диалога сохранения...")
            time.sleep(0.3)

            titles = ['Сохранить как', 'Save As', 'Сохранение', 'Сохранить', 'Save']
            dialog = None

            for title in titles:
                try:
                    app = Application().connect(title_re=title)
                    dialog = app.window(title_re=title)
                    if dialog.exists():
                        print(f"   🎯 Найдено окно: {title}")
                        break
                except:
                    continue

            if not dialog or not dialog.exists():
                print("   ⚠️ Не удалось найти диалог сохранения")
                return False

            dialog.wait('ready', timeout=timeout)
            dialog.set_focus()
            time.sleep(0.3)
            original_filename = None

            # СПОСОБ 4: Через буфер обмена (Ctrl+A, Ctrl+C)
            if not original_filename:
                try:
                    # Выделяем все и копируем в буфер
                    dialog.set_focus()
                    pyperclip.copy("")
                    time.sleep(0.01)
                    send_keys('^a')  # Ctrl+A
                    time.sleep(0.01)
                    send_keys('^c')  # Ctrl+C
                    time.sleep(0.01)

                    original_filename = pyperclip.paste()
                    original_filename = original_filename.replace(" ", "_")
                    original_filename = original_filename.replace(".mp4", "].mp4")
                    if original_filename:
                        print(f"   📄 Имя файла из диалога (буфер обмена): {original_filename}")
                except Exception as e:
                    print(f"   ⚠️ Буфер обмена не сработал: {e}")
            print("Оригинальное название файла: " + original_filename )
            if not original_filename:
                original_filename = ".mp4"

            try:
                send_keys('^a')
                time.sleep(0.01)
                send_keys('{DEL}')
                time.sleep(0.01)

                print(f"   📝 Ввод пути: {file_path}")

                send_keys(file_path.replace(".mp4", f"_[{original_filename}"), pause=0.001)
                print(f"   ✅ Путь введен")
                time.sleep(0.1)
            except Exception as e:
                print(f"   ⚠️ Ошибка ввода пути: {e}")
                return False

            time.sleep(0.1)

            try:
                send_keys('{ENTER}')
                print("   💾 Нажата клавиша Enter")
                return True
            except:
                try:
                    dialog.type_keys('{ENTER}')
                    print("   💾 Нажата клавиша Enter (type_keys)")
                    return True
                except:
                    pass

            print("   ⚠️ Не удалось нажать Enter")
            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка при работе с диалогом: {e}")
            return False

    def _close_ai_agent_popup(self):
        """Закрытие всплывающего окна View your clips"""
        try:
            popup = self.driver.find_elements(By.CSS_SELECTOR, ".bubble-inner")
            if popup and popup[0].is_displayed():
                print("   🎯 Найдено всплывающее окно 'View your clips'")

                try:
                    close_btn = popup[0].find_element(By.CSS_SELECTOR, "iconpark-icon[name='closesmall']")
                    if close_btn and close_btn.is_displayed():
                        close_btn.click()
                        print("   ✅ Всплывающее окно закрыто через крестик")
                        time.sleep(0.5)
                        return True
                except:
                    pass

                try:
                    next_btn = popup[0].find_element(By.CSS_SELECTOR, ".bubble-btn:not(.bubble-disabled)")
                    if next_btn and next_btn.is_displayed():
                        next_btn.click()
                        print("   ✅ Всплывающее окно закрыто через Next")
                        time.sleep(0.5)
                        return True
                except:
                    pass

                try:
                    self.driver.execute_script("""
                        var popup = document.querySelector('.bubble-inner');
                        if (popup) {
                            popup.remove();
                            return true;
                        }
                        return false;
                    """)
                    print("   ✅ Всплывающее окно удалено через JavaScript")
                    time.sleep(0.5)
                    return True
                except:
                    pass
            return False
        except Exception as e:
            print(f"   ⚠️ Ошибка при закрытии всплывающего окна: {e}")
            return False

    def download_all_videos(self):
        """Скачивание всех видео из проектов"""
        print("\n" + "=" * 50)
        print("ШАГ 9: Скачивание видео из Vizard")
        print("=" * 50)

        try:
            # Открываем новую вкладку для скачивания
            print("📌 0) Открытие новой вкладки для скачивания...")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print("   ✅ Новая вкладка открыта")

            # 1) Переходим на страницу проектов
            print("📌 1) Переход на страницу проектов...")
            self.driver.get("https://vizard.ai/workspace")
            self.browser.wait_medium()
            self._close_ai_agent_popup()

            # Получаем список имен проектов для обработки
            print("📌 2) Получение списка проектов...")
            project_names = self._get_project_names()

            if not project_names:
                print("   ❌ Проекты не найдены")
                return False

            print(f"   📊 Найдено проектов: {len(project_names)}")

            # 3) Обрабатываем каждый проект по имени
            for i, project_name in enumerate(project_names, 1):
                try:
                    if "Demo" in project_name:
                        print(f"\n📌 {i}) Проект '{project_name}' - пропускаем (Demo)")
                        continue

                    print(f"\n📌 {i}) Обработка проекта: {project_name}")

                    # Находим проект по имени на странице
                    project = self._find_project_by_name(project_name)
                    if not project:
                        print(f"   ⚠️ Проект '{project_name}' не найден на странице")
                        continue

                    # Открываем проект
                    if not self._open_project_via_view_clips(project):
                        print(f"   ⚠️ Не удалось открыть проект {project_name}")
                        continue

                    # Ждем появления кнопок Download
                    print(f"   ⏳ Ожидание появления кнопок Download...")
                    if not self._wait_for_download_buttons_with_refresh(timeout=600):
                        print(f"   ⚠️ Время ожидания истекло для проекта {project_name}")
                        self.driver.get("https://vizard.ai/workspace")
                        self.browser.wait_medium()
                        self._close_ai_agent_popup()
                        continue

                    # Скачиваем видео
                    print(f"   📥 Скачивание видео из проекта...")
                    downloaded = self._download_videos_from_project(project_name)
                    print(f"   ✅ Скачано видео: {downloaded}")

                    # Возвращаемся на страницу проектов
                    self.driver.get("https://vizard.ai/workspace")
                    self.browser.wait_medium()
                    self._close_ai_agent_popup()

                except Exception as e:
                    print(f"   ⚠️ Ошибка обработки проекта {i}: {e}")
                    try:
                        self.driver.get("https://vizard.ai/workspace")
                        self.browser.wait_medium()
                        self._close_ai_agent_popup()
                    except:
                        pass
                    continue

            print(f"\n✅ Все видео скачаны в папку: {self.downloads_dir}")
            return True

        except Exception as e:
            print(f"❌ Ошибка скачивания видео: {e}")
            return False

    def _get_project_names(self):
        """Получение списка имен проектов"""
        try:
            time.sleep(2)
            projects = self.driver.find_elements(By.CSS_SELECTOR, ".project-item")

            if not projects:
                projects = self.driver.find_elements(By.CSS_SELECTOR, ".list-item-space .project-item")

            if not projects:
                return []

            names = []
            for project in projects:
                try:
                    name_element = project.find_element(By.CSS_SELECTOR, ".item-name")
                    if name_element:
                        name = name_element.text.strip()
                        if name:
                            names.append(name)
                except:
                    continue

            print(f"   🎯 Найдено проектов: {len(names)}")
            return names

        except Exception as e:
            print(f"   ⚠️ Ошибка получения проектов: {e}")
            return []

    def _find_project_by_name(self, project_name):
        """Поиск проекта по имени на странице"""
        try:
            projects = self.driver.find_elements(By.CSS_SELECTOR, ".project-item")

            if not projects:
                projects = self.driver.find_elements(By.CSS_SELECTOR, ".list-item-space .project-item")

            for project in projects:
                try:
                    name_element = project.find_element(By.CSS_SELECTOR, ".item-name")
                    if name_element and name_element.text.strip() == project_name:
                        return project
                except:
                    continue

            return None

        except Exception as e:
            print(f"   ⚠️ Ошибка поиска проекта: {e}")
            return None

    def _open_project_via_view_clips(self, project):
        """Открытие проекта через кнопку View clips"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", project)
            time.sleep(0.5)

            actions = ActionChains(self.driver)
            actions.move_to_element(project).perform()
            time.sleep(0.5)

            try:
                view_clips_link = project.find_element(By.CSS_SELECTOR, "a.open-button.open-clip")
                if view_clips_link and view_clips_link.is_displayed():
                    print("   🎯 Найдена кнопка View clips")
                    href = view_clips_link.get_attribute("href")
                    if href:
                        self.driver.get(href)
                        self.browser.wait_medium()
                        return True
                    view_clips_link.click()
                    self.browser.wait_medium()
                    return True
            except:
                pass

            try:
                img_cover = project.find_element(By.CSS_SELECTOR, "a.img-cover")
                if img_cover:
                    href = img_cover.get_attribute("href")
                    if href:
                        self.driver.get(href)
                        self.browser.wait_medium()
                        return True
            except:
                pass

            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка открытия проекта: {e}")
            return False

    def _wait_for_download_buttons_with_refresh(self, timeout=600):
        """Ожидание появления кнопок Download с обновлением страницы каждые 30 секунд"""
        waited = 0
        refresh_interval = 30

        print(f"   ⏱️ Таймаут: {timeout} секунд, обновление каждые {refresh_interval} секунд")

        while waited < timeout:
            try:
                self.browser.close_ad_if_exists()
                self._close_ai_agent_popup()

                buttons = self._find_download_buttons()

                if buttons:
                    print(f"   ✅ Кнопки Download появились! ({len(buttons)} шт)")
                    return True

                try:
                    processing = self.driver.find_elements(By.CSS_SELECTOR, ".item-trans-schedule .trans-item")
                    if processing and processing[0].is_displayed():
                        status_text = processing[0].text.strip()
                        print(f"   ⏳ {status_text}... {waited} сек")
                    else:
                        loading = self.driver.find_elements(By.CSS_SELECTOR, ".loading-animation")
                        if loading and loading[0].is_displayed():
                            print(f"   ⏳ Обработка... {waited} сек")
                        else:
                            print(f"   ⏳ Ожидание... {waited} сек")
                except:
                    print(f"   ⏳ Ожидание... {waited} сек")

                if waited > 0 and waited % refresh_interval == 0:
                    print(f"   🔄 Обновление страницы... ({waited} сек)")
                    self.driver.refresh()
                    self.browser.wait_medium()
                    self.browser.close_ad_if_exists()
                    self._close_ai_agent_popup()

                time.sleep(5)
                waited += 5

            except Exception as e:
                print(f"   ⚠️ Ошибка ожидания: {e}")
                time.sleep(5)
                waited += 5

        print(f"   ⚠️ Время ожидания истекло ({timeout} сек)")
        return False

    def _find_download_buttons(self):
        """Поиск кнопок Download на странице - ТОЛЬКО с текстом Download"""
        try:
            # Ищем по точному тексту Download
            buttons = self.driver.find_elements(By.XPATH,
                                                "//div[contains(@class, 'border-button') and contains(@class, 'narrow-video-button')]//span[text()='Download']")

            if buttons:
                result = []
                for span in buttons:
                    try:
                        parent = span.find_element(By.XPATH, "./ancestor::div[contains(@class, 'border-button')]")
                        if parent and parent.is_displayed():
                            result.append(parent)
                    except:
                        pass
                if result:
                    return result

            # Альтернативный способ
            buttons = self.driver.find_elements(By.XPATH,
                                                "//div[contains(@class, 'border-button') and contains(., 'Download')]")

            visible_buttons = [btn for btn in buttons if btn.is_displayed() and "Download" in btn.text]

            return visible_buttons

        except Exception as e:
            return []

    def _download_videos_from_project(self, project_name):
        """Скачивание видео из проекта в общую папку downloads"""
        try:
            time.sleep(1)

            download_buttons = self._find_download_buttons()

            if not download_buttons:
                print("   ⚠️ Нет кнопок для скачивания")
                return 0

            downloaded_count = 0

            for i, btn in enumerate(download_buttons, 1):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.3)

                    if "Download" not in btn.text:
                        continue

                    # ✅ СОХРАНЯЕМ ПРЯМО В ПАПКУ DOWNLOADS (без подпапок)
                    filename = f"{project_name}_clip_{i}.mp4"
                    filepath = os.path.join(self.downloads_dir, filename)

                    print(f"   📥 Клик по кнопке Download {i}...")

                    try:
                        btn.click()
                        print(f"   🔔 Кнопка Download {i} нажата")
                    except:
                        self.driver.execute_script("arguments[0].click();", btn)
                        print(f"   🔔 Кнопка Download {i} нажата (JavaScript)")

                    time.sleep(1)

                    if self._handle_save_file_dialog(filepath):
                        print(f"   ✅ Файл сохранен: {filename}")
                        downloaded_count += 1

                    time.sleep(0.5)

                except Exception as e:
                    print(f"   ⚠️ Ошибка скачивания {i}: {e}")
                    continue

            return downloaded_count

        except Exception as e:
            print(f"   ❌ Ошибка скачивания из проекта: {e}")
            return 0