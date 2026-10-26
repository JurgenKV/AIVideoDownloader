# classes/vizard_uploader.py
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class VizardUploader:
    """Класс для загрузки видео на Vizard.ai"""

    def __init__(self, browser_manager, config=None):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait

        if config is None:
            from ai_config import AIConfig
            self.config = AIConfig()
        else:
            self.config = config

        self.uploaded_count = 0

    def upload_videos(self, video_paths):
        """Загрузка нескольких видео на Vizard в отдельных вкладках"""
        print("\n" + "=" * 50)
        print("ШАГ 7: Загрузка видео на Vizard")
        print("=" * 50)

        max_videos = getattr(self.config, 'MAX_VIDEOS', 3)
        print(f"📊 Максимум видео для загрузки: {max_videos}")

        videos_to_upload = video_paths[:max_videos]
        if not videos_to_upload:
            print("❌ Нет видео для загрузки")
            return False

        print(f"📹 Будет загружено видео: {len(videos_to_upload)}")

        main_tab = self.driver.current_window_handle
        print(f"📌 Главная вкладка сохранена: {main_tab[:20]}...")

        video_tabs = []

        for i, video_path in enumerate(videos_to_upload, 1):
            print(f"\n{'=' * 50}")
            print(f"📹 ЗАГРУЗКА ВИДЕО {i}/{len(videos_to_upload)}: {os.path.basename(video_path)}")
            print(f"{'=' * 50}")

            try:
                tab_handle = self._upload_single_video_in_new_tab(video_path, i)
                if tab_handle:
                    video_tabs.append(tab_handle)
                    print(f"   ✅ Видео {i} загружено, вкладка оставлена открытой")
                else:
                    print(f"   ⚠️ Не удалось загрузить видео {i}")
                    continue

                if i < len(videos_to_upload):
                    print(f"   ⏳ Пауза 3 секунды перед следующим видео...")
                    self.browser._sleep(1.5)

            except Exception as e:
                print(f"   ❌ Ошибка загрузки видео {i}: {e}")
                continue

        wait_time = getattr(self.config, 'UPLOAD_WAIT_TIME', 120)
        print(f"\n{'=' * 50}")
        print(f"📌 Ожидание загрузки всех видео на сервер ({wait_time} секунд)...")
        print(f"{'=' * 50}")

        for i in range(wait_time // 5):
            self.browser._sleep(5)         # прерываемый
            remaining = wait_time - (i + 1) * 5
            if remaining > 0:
                print(f"   ⏳ Осталось {remaining} секунд...")

        try:
            self.driver.switch_to.window(main_tab)
            print(f"   ✅ Переключились на главную вкладку для скачивания")
        except:
            print("   ⚠️ Главная вкладка не найдена, открываем новую...")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])

        print(f"\n✅ Все {len(videos_to_upload)} видео успешно загружены!")
        return True

    def _upload_single_video_in_new_tab(self, video_path, video_num):
        tab_handle = None
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            tab_handle = self.driver.current_window_handle
            print(f"   📌 Открыта новая вкладка для видео {video_num}: {tab_handle[:20]}...")

            print(f"   📌 1) Переход на страницу загрузки...")
            self.driver.get("https://vizard.ai/upload?from=home_upload")
            self.browser.wait_short()

            print(f"   📌 2) Загружаем видео: {os.path.basename(video_path)}...")
            if not self._upload_video_file(video_path):
                print("   ❌ Не удалось загрузить видео")
                self.driver.close()
                return None

            print("   📌 3) Настройка параметров видео...")
            self.browser._sleep(1)

            print("      📌 Выбор языка: Russian (Pусский)...")
            self._select_language()

            print("      📌 Включение Get AI clips...")
            self._enable_ai_clips()

            print(f"      📌 Выбор модели: {self.config.MODEL}...")
            self._select_model(self.config.MODEL)

            print("   📌 4) Нажимаем кнопку Upload...")
            if not self._click_upload_button():
                print("   ❌ Не удалось нажать Upload")
                self.driver.close()
                return None

            print("   📌 5) Ожидание перехода на страницу конфигурации...")
            if not self._wait_for_config_page(timeout=120):
                print("   ⚠️ Не удалось перейти на страницу конфигурации")
                self.driver.close()
                return None

            print("   📌 6) Настройка AI шаблона...")
            if not self._configure_template():
                print("   ⚠️ Не удалось настроить шаблон")
                self.driver.close()
                return None

            print(f"   📌 Вкладка {video_num} оставлена открытой для обработки")

            self.driver.switch_to.window(self.driver.window_handles[0])
            print(f"   📌 Переключились на главную вкладку")

            return tab_handle

        except Exception as e:
            print(f"   ❌ Ошибка загрузки видео: {e}")
            try:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return None

    def _wait_for_config_page(self, timeout=120):
        """Ожидание перехода на страницу конфигурации (прерываемый цикл)."""
        print(f"      ⏱️ Таймаут: {timeout} секунд")
        waited = 0

        while waited < timeout:
            try:
                try:
                    clip_length = self.driver.find_element(
                        By.XPATH,
                        "//div[contains(@class, 'pre') and contains(text(), 'Clip length')]"
                    )
                    if clip_length and clip_length.is_displayed():
                        print(f"      ✅ Страница конфигурации загружена! Время: {waited} сек")
                        return True
                except:
                    pass

                try:
                    get_ai_btn = self.driver.find_element(
                        By.XPATH, "//*[contains(text(), 'Get AI clips')]"
                    )
                    if get_ai_btn and get_ai_btn.is_displayed():
                        print(f"      ✅ Страница конфигурации загружена! Время: {waited} сек")
                        return True
                except:
                    pass

                try:
                    template = self.driver.find_element(By.CSS_SELECTOR, ".template-list-area")
                    if template and template.is_displayed():
                        print(f"      ✅ Страница конфигурации загружена! Время: {waited} сек")
                        return True
                except:
                    pass

                if waited % 10 == 0 and waited > 0:
                    print(f"      ⏳ Ожидание загрузки страницы конфигурации... {waited} сек")

                self.browser._sleep(3)         # ✅ прерываемый sleep
                waited += 3

            except Exception as e:
                print(f"      ⚠️ Ошибка проверки: {e}")
                self.browser._sleep(3)
                waited += 3

        print(f"      ⚠️ Время ожидания страницы конфигурации истекло ({timeout} сек)")
        return False

    def _configure_template(self):
        try:
            self.browser._sleep(1)

            from classes.vizard_template_manager import VizardTemplateManager
            template_manager = VizardTemplateManager(self.browser, config=self.config)

            if template_manager.configure_template():
                print("      ✅ Шаблон настроен успешно, Get AI clips нажата")
                return True
            else:
                print("      ⚠️ Не удалось настроить шаблон")
                return False

        except Exception as e:
            print(f"      ⚠️ Ошибка настройки шаблона: {e}")
            return False

    def _select_language(self):
        try:
            print("      🔍 Поиск поля выбора языка...")
            self.browser._sleep(0.5)

            try:
                language_input = self.driver.find_element(
                    By.XPATH, "//input[@placeholder='Select spoken language']"
                )
                if language_input:
                    print("      🎯 Найдено поле выбора языка")
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", language_input
                    )
                    self.browser._sleep(0.5)
                    language_input.click()
                    print("      ✅ Открыт список языков")
                    self.browser._sleep(0.5)

                    try:
                        russian_option = self.driver.find_element(
                            By.XPATH,
                            "//li[contains(@class, 'lang-select-item')]//span[contains(text(), 'Russian (Pусский)')]"
                        )
                        if russian_option:
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});", russian_option
                            )
                            self.browser._sleep(0.5)
                            russian_option.click()
                            print("      ✅ Выбран язык: Russian (Pусский)")
                            self.browser._sleep(0.5)
                            return True
                    except:
                        pass

                    try:
                        russian_option = self.driver.find_element(
                            By.XPATH,
                            "//li[contains(@class, 'lang-select-item')]//span[contains(text(), 'Russian')]"
                        )
                        if russian_option:
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});", russian_option
                            )
                            self.browser._sleep(0.5)
                            russian_option.click()
                            print("      ✅ Выбран язык: Russian (Pусский)")
                            self.browser._sleep(0.5)
                            return True
                    except:
                        pass
            except:
                pass

            try:
                print("      🔍 Поиск через родительский контейнер...")
                lang_container = self.driver.find_element(By.CSS_SELECTOR, ".language")
                if lang_container:
                    select_input = lang_container.find_element(By.CSS_SELECTOR, ".el-select input")
                    if select_input:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", select_input
                        )
                        self.browser._sleep(0.5)
                        select_input.click()
                        print("      ✅ Открыт список языков")
                        self.browser._sleep(0.5)

                        try:
                            russian_option = self.driver.find_element(
                                By.XPATH,
                                "//li[contains(@class, 'lang-select-item')]//span[contains(text(), 'Russian')]"
                            )
                            if russian_option:
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});", russian_option
                                )
                                self.browser._sleep(0.5)
                                russian_option.click()
                                print("      ✅ Выбран язык: Russian (Pусский)")
                                self.browser._sleep(0.5)
                                return True
                        except:
                            pass
            except:
                pass

            try:
                print("      🔍 Поиск через select-item...")
                items = self.driver.find_elements(By.CSS_SELECTOR, ".select-item.lang-select-item")
                for item in items:
                    try:
                        text = item.text
                        if "Russian" in text or "Pусский" in text:
                            print(f"      🎯 Найден язык: {text}")
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});", item
                            )
                            self.browser._sleep(0.5)
                            item.click()
                            print(f"      ✅ Выбран язык: {text}")
                            self.browser._sleep(0.5)
                            return True
                    except:
                        continue
            except:
                pass

            try:
                print("      🔍 Поиск через JavaScript...")
                self.driver.execute_script("""
                    var items = document.querySelectorAll('.select-item.lang-select-item');
                    for (var i = 0; i < items.length; i++) {
                        if (items[i].textContent.includes('Russian') || items[i].textContent.includes('Pусский')) {
                            items[i].click();
                            return true;
                        }
                    }
                """)
                print("      ✅ Выбран язык через JavaScript")
                self.browser._sleep(0.5)
                return True
            except:
                pass

            print("      ⚠️ Не удалось выбрать язык, продолжаем...")
            return False

        except Exception as e:
            print(f"      ⚠️ Ошибка выбора языка: {e}")
            return False

    def _upload_video_file(self, video_path):
        try:
            self.browser.wait_short()
            self.browser.close_ad_if_exists()

            try:
                file_input = self.driver.find_element(
                    By.CSS_SELECTOR, "input[type='file'][accept*='mp4']"
                )
                if file_input:
                    file_input.send_keys(os.path.abspath(video_path))
                    print("      ✅ Видео отправлено на загрузку")
                    self.browser.wait_medium()
                    return True
            except:
                pass

            try:
                file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
                if file_input:
                    file_input.send_keys(os.path.abspath(video_path))
                    print("      ✅ Видео отправлено на загрузку")
                    self.browser.wait_medium()
                    return True
            except:
                pass

            print("      ❌ Не удалось найти элемент для загрузки файла")
            return False

        except Exception as e:
            print(f"      ❌ Ошибка загрузки видео: {e}")
            return False

    def _enable_ai_clips(self):
        try:
            print("      🔍 Поиск переключателя Get AI clips...")

            try:
                switch = self.driver.find_element(By.CSS_SELECTOR, ".switch-ai .el-switch")
                if switch:
                    is_checked = switch.get_attribute("aria-checked")
                    if is_checked == "true":
                        print("      ℹ️ Get AI clips уже включен")
                        return True
                    else:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", switch
                        )
                        self.browser._sleep(0.5)
                        switch.click()
                        print("      ✅ Get AI clips включен")
                        self.browser._sleep(0.5)
                        return True
            except:
                pass

            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR, ".switch-ai input[type='checkbox']")
                if checkbox and not checkbox.is_selected():
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", checkbox
                    )
                    self.browser._sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", checkbox)
                    print("      ✅ Get AI clips включен (через checkbox)")
                    self.browser._sleep(0.5)
                    return True
                elif checkbox and checkbox.is_selected():
                    print("      ℹ️ Get AI clips уже включен")
                    return True
            except:
                pass

            print("      ⚠️ Не удалось включить Get AI clips, продолжаем...")
            return False

        except Exception as e:
            print(f"      ⚠️ Ошибка включения AI clips: {e}")
            return False

    def _select_model(self, model_name):
        """Выбор модели по имени из конфига (Model v1, Model v2, ...)"""
        if not model_name:
            model_name = "Model v2"
        model_name = model_name.strip()

        print(f"      🔍 Поиск модели: '{model_name}'")

        try:
            self.browser._sleep(0.5)

            # --- 1. Открываем dropdown моделей ---
            opened = False
            try:
                model_select = self.driver.find_element(
                    By.CSS_SELECTOR, ".select-model .choose-model"
                )
                if model_select and model_select.is_displayed():
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", model_select
                    )
                    self.browser._sleep(0.5)
                    model_select.click()
                    self.browser._sleep(0.5)
                    opened = True
                    print("      ✅ Dropdown моделей открыт")
            except Exception as e:
                print(f"      ⚠️ Не удалось открыть dropdown: {e}")

            if not opened:
                print("      ⚠️ Продолжаем без открытия dropdown...")

            # --- 2. Ищем модель по точному имени (case-insensitive) ---
            try:
                clicked = self.driver.execute_script("""
                    var target = arguments[0].trim().toLowerCase();
                    var cards = document.querySelectorAll('.model-card');
                    for (var i = 0; i < cards.length; i++) {
                        var children = cards[i].querySelectorAll('span, div');
                        for (var j = 0; j < children.length; j++) {
                            var t = (children[j].textContent || '').trim().toLowerCase();
                            if (t === target) {
                                cards[i].click();
                                return children[j].textContent.trim();
                            }
                        }
                    }
                    return null;
                """, model_name)

                if clicked:
                    print(f"      ✅ Выбрана модель: {clicked}")
                    self.browser._sleep(0.5)
                    return True
            except Exception as e:
                print(f"      ⚠️ Точный поиск не сработал: {e}")

            # --- 3. Fallback: подстрока ---
            try:
                clicked = self.driver.execute_script("""
                    var target = arguments[0].trim().toLowerCase();
                    var cards = document.querySelectorAll('.model-card');
                    for (var i = 0; i < cards.length; i++) {
                        if ((cards[i].textContent || '').toLowerCase().indexOf(target) !== -1) {
                            cards[i].click();
                            return (cards[i].textContent || '').trim().split('\\n')[0];
                        }
                    }
                    return null;
                """, model_name)

                if clicked:
                    print(f"      ✅ Выбрана модель (подстрока): {clicked}")
                    self.browser._sleep(0.5)
                    return True
            except:
                pass

            # --- 4. Показать доступные модели (для отладки) ---
            try:
                available = self.driver.execute_script("""
                    var cards = document.querySelectorAll('.model-card');
                    var names = [];
                    for (var i = 0; i < cards.length; i++) {
                        var first = (cards[i].textContent || '').trim().split('\\n')[0];
                        if (first) names.push(first);
                    }
                    return names;
                """)
                if available:
                    print(f"      ℹ️ Доступные модели в списке: {available}")
            except:
                pass

            print(f"      ❌ Модель '{model_name}' не найдена в dropdown")
            return False

        except Exception as e:
            print(f"      ⚠️ Ошибка выбора модели: {e}")
            return False

    def _click_upload_button(self):
        try:
            try:
                upload_btn = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'win-confirm-button') and contains(text(), 'Upload')]"
                )
                if upload_btn and upload_btn.is_displayed():
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", upload_btn
                    )
                    self.browser._sleep(0.5)
                    upload_btn.click()
                    print("      ✅ Кнопка Upload нажата")
                    self.browser._sleep(0.5)
                    return True
            except:
                pass

            try:
                upload_btn = self.driver.find_element(By.CSS_SELECTOR, ".win-confirm-button.flex-center")
                if upload_btn and upload_btn.is_displayed() and "Upload" in upload_btn.text:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", upload_btn
                    )
                    self.browser._sleep(0.5)
                    upload_btn.click()
                    print("      ✅ Кнопка Upload нажата")
                    self.browser._sleep(0.5)
                    return True
            except:
                pass

            print("      ❌ Не удалось найти кнопку Upload")
            return False

        except Exception as e:
            print(f"      ❌ Ошибка при нажатии Upload: {e}")
            return False

    def wait_for_processing_complete(self, timeout=300):
        print("\n⏳ Ожидание завершения обработки видео...")
        print(f"   ⏱️ Таймаут: {timeout} секунд")
        waited = 0

        while waited < timeout:
            try:
                download_btn = self.driver.find_elements(
                    By.XPATH, "//*[contains(text(), 'Download') or contains(text(), 'Export')]"
                )
                if download_btn and download_btn[0].is_displayed():
                    print(f"   ✅ Обработка завершена! Время: {waited} сек")
                    return True

                error_msg = self.driver.find_elements(
                    By.XPATH, "//*[contains(text(), 'Error') or contains(text(), 'Failed')]"
                )
                if error_msg and error_msg[0].is_displayed():
                    print(f"   ❌ Обнаружена ошибка обработки")
                    return False

                if waited % 30 == 0 and waited > 0:
                    print(f"   ⏳ Обработка... {waited} сек")

                self.browser._sleep(5)
                waited += 5
            except:
                self.browser._sleep(5)
                waited += 5

        print(f"   ⚠️ Время ожидания истекло ({timeout} сек)")
        return False