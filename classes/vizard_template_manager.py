# classes/vizard_template_manager.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class VizardTemplateManager:
    """Класс для настройки AI шаблонов видео"""

    # Маппинг шаблонов по индексам
    TEMPLATE_INDEX = {
        "Default": 0,
        "Modern": 1,
        "Bouncy": 2,
        "Mr. Beast": 3,
        "Business": 4,
        "Blur": 5,
        "Fit video": 6,
        "Tech": 7
    }

    def __init__(self, browser_manager, config=None):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait

        if config is None:
            from ai_config import AIConfig
            self.config = AIConfig()
        else:
            self.config = config

        self._print_config_info()

    def _print_config_info(self):
        """Вывод информации о текущей конфигурации"""
        print("\n" + "=" * 50)
        print("НАСТРОЙКИ AI ШАБЛОНА")
        print("=" * 50)
        print(f"📐 Шаблон: {self.config.TEMPLATE_NAME}")

        length_map = {
            0: "Any length",
            1: "<30s",
            2: "30s-60s",
            3: "60s-90s",
            4: "90s-3mins",
            5: ">3mins"
        }
        print(f"⏱️ Длительность: {length_map.get(self.config.CLIP_LENGTH, 'Unknown')}")
        print(f"📧 Язык: {self.config.LANGUAGE}")
        print(f"🤖 Модель: {self.config.MODEL}")
        print(f"😊 Эмодзи: {'Вкл' if self.config.ENABLE_EMOJIS else 'Выкл'}")
        print(f"🔑 Ключевые слова: {'Вкл' if self.config.ENABLE_KEYWORDS else 'Выкл'}")
        print(f"🎬 B-rolls: {'Вкл' if self.config.ENABLE_B_ROLLS else 'Выкл'}")
        print(f"🔇 Удаление тишины: {'Вкл' if self.config.ENABLE_SILENCE_REMOVAL else 'Выкл'}")
        print(f"🔞 Авто-цензура: {'Вкл' if self.config.ENABLE_AUTO_CENSOR else 'Выкл'}")
        print("=" * 50 + "\n")

    def configure_template(self):
        """Настройка шаблона видео"""
        print("\n" + "=" * 50)
        print("ШАГ 8: Настройка AI шаблона")
        print("=" * 50)

        try:
            print("📌 1) Ожидание загрузки настроек...")
            time.sleep(1)

            print("📌 2) Настройка длительности клипа...")
            self._set_clip_length(self.config.CLIP_LENGTH)

            print("📌 3) Выбор шаблона...")
            self._select_template_by_index(self.config.TEMPLATE_NAME)

            print("📌 4) Настройка AI опций...")
            self._configure_ai_options()

            print("📌 5) Нажатие кнопки Get AI clips...")
            self._click_get_ai_clips()

            print("\n✅ Шаблон успешно настроен!")
            return True

        except Exception as e:
            print(f"❌ Ошибка настройки шаблона: {e}")
            return False

        # classes/vizard_template_manager.py (исправленный метод _set_clip_length)

    def _set_clip_length(self, length_value):
        """Настройка длительности клипа - проверяем, нажата ли уже опция"""
        try:
            print("   🔍 Поиск Clip length...")

            # СПОСОБ 1: Ищем все set-line-button внутри set-line
            try:
                set_line_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".set-line .set-line-button")

                if set_line_buttons and len(set_line_buttons) >= 2:
                    print(f"   📊 Найдено set-line-button: {len(set_line_buttons)}")

                    # Берем второй set-line-button (индекс 1) - это Clip length
                    clip_length_button = set_line_buttons[1]
                    print("   🎯 Выбран второй set-line-button (Clip length)")

                    # Проверяем, какая опция сейчас выбрана
                    try:
                        value_element = clip_length_button.find_element(By.CSS_SELECTOR, ".value")
                        current_value = value_element.text.strip()
                        print(f"   ℹ️ Текущее значение: {current_value}")

                        # Если уже выбрана нужная опция - пропускаем
                        if length_value == 0 and "Any length" in current_value:
                            print(f"   ✅ Длительность уже выбрана: Any length")
                            return True
                        if length_value == 1 and "<30s" in current_value:
                            print(f"   ✅ Длительность уже выбрана: <30s")
                            return True
                        if length_value == 2 and "30s-60s" in current_value:
                            print(f"   ✅ Длительность уже выбрана: 30s-60s")
                            return True
                        if length_value == 3 and "60s-90s" in current_value:
                            print(f"   ✅ Длительность уже выбрана: 60s-90s")
                            return True
                        if length_value == 4 and "90s-3mins" in current_value:
                            print(f"   ✅ Длительность уже выбрана: 90s-3mins")
                            return True
                        if length_value == 5 and ">3mins" in current_value:
                            print(f"   ✅ Длительность уже выбрана: >3mins")
                            return True
                    except:
                        pass

                    # Находим внутри него multiple-select-input
                    try:
                        select_input = clip_length_button.find_element(By.CSS_SELECTOR, ".multiple-select-input")
                    except:
                        select_input = clip_length_button.find_element(By.CSS_SELECTOR,
                                                                       ".multiple-select .multiple-select-input")

                    if select_input:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_input)
                        time.sleep(0.5)
                        select_input.click()
                        print("   ✅ Открыт список длительности")
                        time.sleep(0.5)

                        if length_value == 0:
                            print("   ℹ️ Длительность: Any length (по умолчанию)")
                            self.driver.execute_script("arguments[0].click();", select_input)
                            return True

                        options = [
                            ("Any length", 0), ("<30s", 1), ("30s-60s", 2),
                            ("60s-90s", 3), ("90s-3mins", 4), (">3mins", 5)
                        ]

                        option_text = None
                        for text, value in options:
                            if value == length_value:
                                option_text = text
                                break

                        if option_text:
                            try:
                                menu = self.driver.find_element(By.CSS_SELECTOR, ".menu")
                                if menu:
                                    option = menu.find_element(By.XPATH, f".//*[contains(text(), '{option_text}')]")
                                    if option:
                                        self.driver.execute_script(
                                            "arguments[0].scrollIntoView({block: 'center'});", option)
                                        time.sleep(0.5)
                                        option.click()
                                        print(f"   ✅ Длительность: {option_text}")
                                        time.sleep(0.5)
                                        return True
                            except:
                                pass

                            try:
                                option = self.driver.find_element(By.XPATH,
                                                                  f"//ul[contains(@class, 'vizard-primary-checkbox')]//li[contains(., '{option_text}')]")
                                if option:
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                               option)
                                    time.sleep(0.5)
                                    option.click()
                                    print(f"   ✅ Длительность: {option_text}")
                                    time.sleep(0.5)
                                    return True
                            except:
                                pass
            except Exception as e:
                print(f"   ⚠️ Ошибка при поиске через set-line-button: {e}")

            # СПОСОБ 2: Ищем по тексту "Clip length"
            try:
                print("   🔍 Поиск Clip length по тексту...")
                clip_length_elements = self.driver.find_elements(By.XPATH,
                                                                 "//div[contains(@class, 'pre') and contains(text(), 'Clip length')]")

                for pre_element in clip_length_elements:
                    try:
                        select_input = pre_element.find_element(By.XPATH,
                                                                "./ancestor::div[contains(@class, 'multiple-select-input')]")
                        if select_input:
                            print("   🎯 Найден Clip length по тексту")
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",
                                                       select_input)
                            time.sleep(0.5)
                            select_input.click()
                            print("   ✅ Открыт список длительности")
                            time.sleep(0.5)

                            if length_value == 0:
                                print("   ℹ️ Длительность: Any length (по умолчанию)")
                                self.driver.execute_script("arguments[0].click();", select_input)
                                return True

                            options = [
                                ("Any length", 0), ("<30s", 1), ("30s-60s", 2),
                                ("60s-90s", 3), ("90s-3mins", 4), (">3mins", 5)
                            ]

                            option_text = None
                            for text, value in options:
                                if value == length_value:
                                    option_text = text
                                    break

                            if option_text:
                                try:
                                    option = self.driver.find_element(By.XPATH,
                                                                      f"//ul[contains(@class, 'vizard-primary-checkbox')]//li[contains(., '{option_text}')]")
                                    if option:
                                        self.driver.execute_script(
                                            "arguments[0].scrollIntoView({block: 'center'});", option)
                                        time.sleep(0.5)
                                        option.click()
                                        print(f"   ✅ Длительность: {option_text}")
                                        time.sleep(0.5)
                                        return True
                                except:
                                    pass
                    except:
                        continue
            except Exception as e:
                print(f"   ⚠️ Ошибка при поиске по тексту: {e}")

            print("   ⚠️ Не удалось найти Clip length")
            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка выбора длительности: {e}")
            return False

    def _select_template_by_index(self, template_name):
        """Выбор шаблона по индексу"""
        try:
            template_index = self.TEMPLATE_INDEX.get(template_name, 0)
            print(f"   🎯 Выбор шаблона: {template_name} (индекс {template_index})")

            time.sleep(2)
            templates = self.driver.find_elements(By.CSS_SELECTOR, ".template")

            if not templates:
                print("   ⚠️ Шаблоны не найдены")
                return False

            print(f"   📊 Найдено шаблонов: {len(templates)}")

            if template_index >= len(templates):
                template_index = 0

            target_template = templates[template_index]

            if target_template:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_template)
                time.sleep(0.5)
                target_template.click()
                print(f"   ✅ Выбран шаблон: {template_name} (индекс {template_index})")
                time.sleep(1)
                return True

        except Exception as e:
            print(f"   ⚠️ Ошибка выбора шаблона: {e}")
            return False

    def _configure_ai_options(self):
        """Настройка AI опций"""
        try:
            time.sleep(1)

            options = [
                ("Add emojis", self.config.ENABLE_EMOJIS),
                ("Highlight keywords", self.config.ENABLE_KEYWORDS),
                ("Add B-rolls", self.config.ENABLE_B_ROLLS),
                ("Remove silences", self.config.ENABLE_SILENCE_REMOVAL),
                ("Auto-censor", self.config.ENABLE_AUTO_CENSOR)
            ]

            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, ".check-box-item")

            for checkbox in checkboxes:
                try:
                    label = checkbox.find_element(By.CSS_SELECTOR, ".check-box-label")
                    option_name = label.text.strip()

                    for opt_name, opt_value in options:
                        if option_name == opt_name:
                            checkbox_input = checkbox.find_element(By.CSS_SELECTOR, ".el-checkbox__input")
                            is_checked = "is-checked" in checkbox_input.get_attribute("class")

                            if is_checked != opt_value:
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                                time.sleep(0.3)
                                checkbox.click()
                                status = "включена" if opt_value else "выключена"
                                print(f"   ✅ {option_name}: {status}")
                            else:
                                status = "включена" if opt_value else "выключена"
                                print(f"   ℹ️ {option_name}: {status} (уже настроено)")

                            time.sleep(0.3)
                            break

                except Exception as e:
                    continue

            return True

        except Exception as e:
            print(f"   ⚠️ Ошибка настройки AI опций: {e}")
            return False

        # classes/vizard_template_manager.py (исправленный метод _click_get_ai_clips)

    def _click_get_ai_clips(self):
        """Нажатие кнопки Get AI clips - УЛУЧШЕННАЯ ВЕРСИЯ"""
        try:
            print("   🔍 Поиск кнопки Get AI clips...")

            # Даем время на загрузку
            time.sleep(1)

            # Проверяем рекламу перед поиском
            self.browser.close_ad_if_exists()

            # СПОСОБ 1: По точному классу
            try:
                get_ai_btn = self.driver.find_element(By.CSS_SELECTOR, ".submit-clip-button.submit-hover-button")
                if get_ai_btn and get_ai_btn.is_displayed():
                    print("   🎯 Найдена кнопка Get AI clips (по классу)")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", get_ai_btn)
                    time.sleep(0.5)

                    # Пробуем кликнуть разными способами
                    try:
                        get_ai_btn.click()
                        print("   ✅ Кнопка Get AI clips нажата (обычный клик)")
                        time.sleep(1)
                        return True
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", get_ai_btn)
                            print("   ✅ Кнопка Get AI clips нажата (JavaScript)")
                            time.sleep(1)
                            return True
                        except:
                            pass
            except:
                pass

            # СПОСОБ 2: По тексту
            try:
                get_ai_btn = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Get AI clips')]")
                if get_ai_btn and get_ai_btn.is_displayed():
                    print("   🎯 Найдена кнопка Get AI clips (по тексту)")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", get_ai_btn)
                    time.sleep(0.5)

                    try:
                        get_ai_btn.click()
                        print("   ✅ Кнопка Get AI clips нажата")
                        time.sleep(1)
                        return True
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", get_ai_btn)
                            print("   ✅ Кнопка Get AI clips нажата (JavaScript)")
                            time.sleep(1)
                            return True
                        except:
                            pass
            except:
                pass

            # СПОСОБ 3: По span с текстом
            try:
                get_ai_btn = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Get AI clips')]")
                if get_ai_btn and get_ai_btn.is_displayed():
                    print("   🎯 Найдена кнопка Get AI clips (span)")
                    # Находим родительский элемент с классом submit-clip-button
                    parent = get_ai_btn.find_element(By.XPATH,
                                                     "./ancestor::div[contains(@class, 'submit-clip-button')]")
                    if parent:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent)
                        time.sleep(0.5)

                        try:
                            parent.click()
                            print("   ✅ Кнопка Get AI clips нажата (через родителя)")
                            time.sleep(1)
                            return True
                        except:
                            try:
                                self.driver.execute_script("arguments[0].click();", parent)
                                print("   ✅ Кнопка Get AI clips нажата (JavaScript через родителя)")
                                time.sleep(1)
                                return True
                            except:
                                pass
            except:
                pass

            # СПОСОБ 4: Ищем кнопку с текстом "Get AI clips" внутри submit-clip-button
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, ".submit-clip-button")
                for btn in buttons:
                    if btn.is_displayed() and "Get AI clips" in btn.text:
                        print("   🎯 Найдена кнопка Get AI clips (перебор)")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        time.sleep(0.5)
                        btn.click()
                        print("   ✅ Кнопка Get AI clips нажата")
                        time.sleep(1)
                        return True
            except:
                pass

            print("   ⚠️ Не удалось найти кнопку Get AI clips")
            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка при нажатии Get AI clips: {e}")
            return False

    def configure_from_config(self, config_class):
        """Настройка шаблона из переданного класса конфигурации"""
        self.config = config_class()
        self._print_config_info()
        return self.configure_template()