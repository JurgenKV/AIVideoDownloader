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

        # Загружаем конфигурацию
        if config is None:
            from ai_config import AIConfig
            self.config = AIConfig()
        else:
            self.config = config

        # Счетчик загруженных видео
        self.uploaded_count = 0

    def upload_videos(self, video_paths):
        """Загрузка нескольких видео на Vizard в отдельных вкладках"""
        print("\n" + "=" * 50)
        print("ШАГ 7: Загрузка видео на Vizard")
        print("=" * 50)

        # Получаем максимальное количество видео из конфига
        max_videos = getattr(self.config, 'MAX_VIDEOS', 3)
        print(f"📊 Максимум видео для загрузки: {max_videos}")

        # Ограничиваем количество видео
        videos_to_upload = video_paths[:max_videos]

        if not videos_to_upload:
            print("❌ Нет видео для загрузки")
            return False

        print(f"📹 Будет загружено видео: {len(videos_to_upload)}")

        # Сохраняем текущую вкладку (она будет использована для скачивания)
        main_tab = self.driver.current_window_handle
        print(f"📌 Главная вкладка сохранена: {main_tab[:20]}...")

        # Список для хранения вкладок с видео
        video_tabs = []

        # Загружаем каждое видео в новой вкладке
        for i, video_path in enumerate(videos_to_upload, 1):
            print(f"\n{'=' * 50}")
            print(f"📹 ЗАГРУЗКА ВИДЕО {i}/{len(videos_to_upload)}: {os.path.basename(video_path)}")
            print(f"{'=' * 50}")

            try:
                # Загружаем одно видео в новой вкладке
                tab_handle = self._upload_single_video_in_new_tab(video_path, i)
                if tab_handle:
                    video_tabs.append(tab_handle)
                    print(f"   ✅ Видео {i} загружено, вкладка оставлена открытой")
                else:
                    print(f"   ⚠️ Не удалось загрузить видео {i}")
                    continue

                # Небольшая пауза между видео
                if i < len(videos_to_upload):
                    print(f"   ⏳ Пауза 3 секунды перед следующим видео...")
                    time.sleep(3)

            except Exception as e:
                print(f"   ❌ Ошибка загрузки видео {i}: {e}")
                continue

        # После загрузки всех видео ждем UPLOAD_WAIT_TIME
        wait_time = getattr(self.config, 'UPLOAD_WAIT_TIME', 60)
        print(f"\n{'=' * 50}")
        print(f"📌 Ожидание загрузки всех видео на сервер ({wait_time} секунд)...")
        print(f"{'=' * 50}")

        for i in range(wait_time // 5):
            time.sleep(5)
            remaining = wait_time - (i + 1) * 5
            if remaining > 0:
                print(f"   ⏳ Осталось {remaining} секунд...")

        # Переключаемся на главную вкладку для шага 9
        try:
            self.driver.switch_to.window(main_tab)
            print(f"   ✅ Переключились на главную вкладку для скачивания")
        except:
            # Если главная вкладка закрыта, открываем новую
            print("   ⚠️ Главная вкладка не найдена, открываем новую...")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])

        print(f"\n✅ Все {len(videos_to_upload)} видео успешно загружены!")
        return True

    def _upload_single_video_in_new_tab(self, video_path, video_num):
        """Загрузка одного видео в новой вкладке"""
        tab_handle = None

        try:
            # Открываем новую вкладку
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            tab_handle = self.driver.current_window_handle
            print(f"   📌 Открыта новая вкладка для видео {video_num}: {tab_handle[:20]}...")

            # 1) Переходим на страницу загрузки
            print(f"   📌 1) Переход на страницу загрузки...")
            self.driver.get("https://vizard.ai/upload?from=home_upload")
            self.browser.wait_medium()

            # 2) Загружаем видео
            print(f"   📌 2) Загружаем видео: {os.path.basename(video_path)}...")
            if not self._upload_video_file(video_path):
                print("   ❌ Не удалось загрузить видео")
                self.driver.close()
                return None

            # 3) Настраиваем параметры на странице загрузки
            print("   📌 3) Настройка параметров видео...")

            time.sleep(3)

            # Выбираем язык
            print("      📌 Выбор языка: Russian (Pусский)...")
            self._select_language()

            # Включаем Get AI clips
            print("      📌 Включение Get AI clips...")
            self._enable_ai_clips()

            # Выбираем модель Model v2
            print("      📌 Выбор модели: Model v2...")
            self._select_model_v2()

            # 4) Нажимаем Upload
            print("   📌 4) Нажимаем кнопку Upload...")
            if not self._click_upload_button():
                print("   ❌ Не удалось нажать Upload")
                self.driver.close()
                return None

            # 5) Ждем перехода на страницу конфигурации
            print("   📌 5) Ожидание перехода на страницу конфигурации...")
            if not self._wait_for_config_page(timeout=120):
                print("   ⚠️ Не удалось перейти на страницу конфигурации")
                self.driver.close()
                return None

            # 6) Настраиваем шаблон (ВНУТРИ ЭТОГО МЕТОДА НАЖИМАЕТСЯ Get AI clips)
            print("   📌 6) Настройка AI шаблона...")
            if not self._configure_template():
                print("   ⚠️ Не удалось настроить шаблон")
                self.driver.close()
                return None

            # Оставляем вкладку открытой - она будет обрабатываться на сервере
            print(f"   📌 Вкладка {video_num} оставлена открытой для обработки")

            # Переключаемся обратно на первую вкладку (главную)
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
        """Ожидание перехода на страницу конфигурации"""
        print(f"      ⏱️ Таймаут: {timeout} секунд")

        waited = 0

        while waited < timeout:
            try:
                # Проверяем появление элементов на странице конфигурации
                try:
                    clip_length = self.driver.find_element(By.XPATH,
                                                           "//div[contains(@class, 'pre') and contains(text(), 'Clip length')]")
                    if clip_length and clip_length.is_displayed():
                        print(f"      ✅ Страница конфигурации загружена! Время: {waited} сек")
                        return True
                except:
                    pass

                try:
                    get_ai_btn = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Get AI clips')]")
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

                time.sleep(3)
                waited += 3

            except Exception as e:
                print(f"      ⚠️ Ошибка проверки: {e}")
                time.sleep(3)
                waited += 3

        print(f"      ⚠️ Время ожидания страницы конфигурации истекло ({timeout} сек)")
        return False

    def _configure_template(self):
        """Настройка AI шаблона на странице конфигурации (включая нажатие Get AI clips)"""
        try:
            time.sleep(2)

            from classes.vizard_template_manager import VizardTemplateManager

            template_manager = VizardTemplateManager(self.browser, config=self.config)

            # Этот метод настраивает шаблон И нажимает Get AI clips
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
        """Выбор языка Russian (Pусский) из списка"""
        try:
            print("      🔍 Поиск поля выбора языка...")

            time.sleep(2)

            # СПОСОБ 1: Ищем поле ввода языка и кликаем по нему
            try:
                language_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Select spoken language']")
                if language_input:
                    print("      🎯 Найдено поле выбора языка")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", language_input)
                    time.sleep(0.5)
                    language_input.click()
                    print("      ✅ Открыт список языков")
                    time.sleep(1)

                    try:
                        russian_option = self.driver.find_element(By.XPATH,
                                                                  "//li[contains(@class, 'lang-select-item')]//span[contains(text(), 'Russian (Pусский)')]")
                        if russian_option:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                       russian_option)
                            time.sleep(0.5)
                            russian_option.click()
                            print("      ✅ Выбран язык: Russian (Pусский)")
                            time.sleep(0.5)
                            return True
                    except:
                        pass

                    try:
                        russian_option = self.driver.find_element(By.XPATH,
                                                                  "//li[contains(@class, 'lang-select-item')]//span[contains(text(), 'Russian')]")
                        if russian_option:
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                       russian_option)
                            time.sleep(0.5)
                            russian_option.click()
                            print("      ✅ Выбран язык: Russian (Pусский)")
                            time.sleep(0.5)
                            return True
                    except:
                        pass
            except:
                pass

            # СПОСОБ 2: Ищем через родительский контейнер
            try:
                print("      🔍 Поиск через родительский контейнер...")
                lang_container = self.driver.find_element(By.CSS_SELECTOR, ".language")
                if lang_container:
                    select_input = lang_container.find_element(By.CSS_SELECTOR, ".el-select input")
                    if select_input:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_input)
                        time.sleep(0.5)
                        select_input.click()
                        print("      ✅ Открыт список языков")
                        time.sleep(1)

                        try:
                            russian_option = self.driver.find_element(By.XPATH,
                                                                      "//li[contains(@class, 'lang-select-item')]//span[contains(text(), 'Russian')]")
                            if russian_option:
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                           russian_option)
                                time.sleep(0.5)
                                russian_option.click()
                                print("      ✅ Выбран язык: Russian (Pусский)")
                                time.sleep(0.5)
                                return True
                        except:
                            pass
            except:
                pass

            # СПОСОБ 3: Ищем через класс select-item
            try:
                print("      🔍 Поиск через select-item...")
                items = self.driver.find_elements(By.CSS_SELECTOR, ".select-item.lang-select-item")
                for item in items:
                    try:
                        text = item.text
                        if "Russian" in text or "Pусский" in text:
                            print(f"      🎯 Найден язык: {text}")
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                            time.sleep(0.5)
                            item.click()
                            print(f"      ✅ Выбран язык: {text}")
                            time.sleep(0.5)
                            return True
                    except:
                        continue
            except:
                pass

            # СПОСОБ 4: Используем JavaScript
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
                time.sleep(0.5)
                return True
            except:
                pass

            print("      ⚠️ Не удалось выбрать язык, продолжаем...")
            return False

        except Exception as e:
            print(f"      ⚠️ Ошибка выбора языка: {e}")
            return False

    def _switch_to_vizard_tab(self):
        """Переключение на вкладку Vizard (для совместимости)"""
        try:
            handles = self.driver.window_handles

            for handle in handles:
                self.driver.switch_to.window(handle)
                current_url = self.driver.current_url.lower()

                if "vizard" in current_url:
                    print(f"      ✅ Найдена вкладка Vizard")
                    return True

            print("      ⚠️ Вкладка Vizard не найдена, открываем новую...")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get("https://vizard.ai/upload?from=home_upload")
            self.browser.wait_medium()
            return True

        except Exception as e:
            print(f"      ❌ Ошибка переключения на Vizard: {e}")
            return False

    def _upload_video_file(self, video_path):
        """Загрузка видео файла"""
        try:
            self.browser.wait_medium()
            self.browser.close_ad_if_exists()

            # Ищем input для загрузки файла
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept*='mp4']")
                if file_input:
                    file_input.send_keys(os.path.abspath(video_path))
                    print("      ✅ Видео отправлено на загрузку")
                    self.browser.wait_long()
                    return True
            except:
                pass

            # Пробуем найти любой input
            try:
                file_input = self.driver.find_element(By.XPATH, "//input[@type='file']")
                if file_input:
                    file_input.send_keys(os.path.abspath(video_path))
                    print("      ✅ Видео отправлено на загрузку")
                    self.browser.wait_long()
                    return True
            except:
                pass

            print("      ❌ Не удалось найти элемент для загрузки файла")
            return False

        except Exception as e:
            print(f"      ❌ Ошибка загрузки видео: {e}")
            return False

    def _enable_ai_clips(self):
        """Включение Get AI clips (переключатель) - ВКЛЮЧАЕМ, если выключен"""
        try:
            print("      🔍 Поиск переключателя Get AI clips...")

            # Ищем переключатель
            switch = self.driver.find_element(By.CSS_SELECTOR, ".switch-ai .el-switch")
            if switch:
                # Проверяем, включен ли переключатель
                is_checked = switch.get_attribute("aria-checked")

                if is_checked == "true":
                    print("      ℹ️ Get AI clips уже включен")
                    return True
                else:
                    # Включаем
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", switch)
                    time.sleep(0.5)
                    switch.click()
                    print("      ✅ Get AI clips включен")
                    time.sleep(0.5)
                    return True
        except:
            pass

        # Альтернативный способ - ищем чекбокс
        try:
            checkbox = self.driver.find_element(By.CSS_SELECTOR, ".switch-ai input[type='checkbox']")
            if checkbox and not checkbox.is_selected():
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                time.sleep(0.5)
                self.driver.execute_script("arguments[0].click();", checkbox)
                print("      ✅ Get AI clips включен (через checkbox)")
                time.sleep(0.5)
                return True
            elif checkbox and checkbox.is_selected():
                print("      ℹ️ Get AI clips уже включен")
                return True
        except:
            pass

        print("      ⚠️ Не удалось включить Get AI clips, продолжаем...")
        return False

    def _select_model_v2(self):
        """Выбор модели Model v2"""
        try:
            time.sleep(2)

            # Способ 1: Кликаем по текущей модели
            try:
                model_select = self.driver.find_element(By.CSS_SELECTOR, ".select-model .choose-model")
                if model_select:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", model_select)
                    time.sleep(0.5)
                    model_select.click()
                    time.sleep(1)

                    # Ищем Model v2
                    model_v2 = self.driver.find_element(By.XPATH,
                                                        "//div[contains(@class, 'model-card')]//span[contains(text(), 'Model v2')]")
                    if model_v2:
                        parent_card = model_v2.find_element(By.XPATH, "./ancestor::div[contains(@class, 'model-card')]")
                        if parent_card:
                            parent_card.click()
                            print("      ✅ Выбрана модель: Model v2")
                            time.sleep(0.5)
                            return True
            except:
                pass

            # Способ 2: JavaScript
            try:
                self.driver.execute_script("""
                    var cards = document.querySelectorAll('.model-card');
                    for (var i = 0; i < cards.length; i++) {
                        if (cards[i].textContent.includes('Model v2')) {
                            cards[i].click();
                            return true;
                        }
                    }
                """)
                print("      ✅ Выбрана модель: Model v2 (JavaScript)")
                time.sleep(0.5)
                return True
            except:
                pass

            print("      ⚠️ Не удалось выбрать модель, продолжаем...")
            return False

        except Exception as e:
            print(f"      ⚠️ Ошибка выбора модели: {e}")
            return False

    def _click_upload_button(self):
        """Нажатие кнопки Upload на странице загрузки"""
        try:
            # Способ 1: По XPath
            try:
                upload_btn = self.driver.find_element(By.XPATH,
                                                      "//div[contains(@class, 'win-confirm-button') and contains(text(), 'Upload')]")
                if upload_btn and upload_btn.is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_btn)
                    time.sleep(0.5)
                    upload_btn.click()
                    print("      ✅ Кнопка Upload нажата")
                    time.sleep(1)
                    return True
            except:
                pass

            # Способ 2: По CSS селектору
            try:
                upload_btn = self.driver.find_element(By.CSS_SELECTOR, ".win-confirm-button.flex-center")
                if upload_btn and upload_btn.is_displayed() and "Upload" in upload_btn.text:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", upload_btn)
                    time.sleep(0.5)
                    upload_btn.click()
                    print("      ✅ Кнопка Upload нажата")
                    time.sleep(1)
                    return True
            except:
                pass

            print("      ❌ Не удалось найти кнопку Upload")
            return False

        except Exception as e:
            print(f"      ❌ Ошибка при нажатии Upload: {e}")
            return False

    def wait_for_processing_complete(self, timeout=300):
        """Ожидание завершения обработки видео (для совместимости)"""
        print("\n⏳ Ожидание завершения обработки видео...")
        print(f"   ⏱️ Таймаут: {timeout} секунд")

        waited = 0

        while waited < timeout:
            try:
                download_btn = self.driver.find_elements(By.XPATH,
                                                         "//*[contains(text(), 'Download') or contains(text(), 'Export')]")
                if download_btn and download_btn[0].is_displayed():
                    print(f"   ✅ Обработка завершена! Время: {waited} сек")
                    return True

                error_msg = self.driver.find_elements(By.XPATH,
                                                      "//*[contains(text(), 'Error') or contains(text(), 'Failed')]")
                if error_msg and error_msg[0].is_displayed():
                    print(f"   ❌ Обнаружена ошибка обработки")
                    return False

                if waited % 30 == 0 and waited > 0:
                    print(f"   ⏳ Обработка... {waited} сек")

                time.sleep(5)
                waited += 5

            except:
                time.sleep(5)
                waited += 5

        print(f"   ⚠️ Время ожидания истекло ({timeout} сек)")
        return False