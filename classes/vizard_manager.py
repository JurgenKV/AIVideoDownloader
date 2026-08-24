# classes/vizard_manager.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class VizardManager:
    """Класс для управления Vizard после регистрации"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait

    def refresh_vizard_page(self):
        """Обновление страницы Vizard после подтверждения email"""
        print("\n" + "=" * 50)
        print("ШАГ 6: Обновление страницы Vizard")
        print("=" * 50)

        try:
            # 1) Переключаемся на вкладку Vizard
            print("📌 1) Переключаемся на вкладку Vizard...")
            if not self._switch_to_vizard_tab():
                print("   ⚠️ Не удалось переключиться на Vizard")
                return False

            # 2) Проверяем, нужна ли кнопка Refresh
            print("📌 2) Проверяем состояние страницы...")
            if self._check_needs_refresh():
                print("   🔄 Страница требует обновления")
                if self._click_refresh_button():
                    print("   ✅ Кнопка Refresh нажата")
                else:
                    print("   ⚠️ Кнопка Refresh не найдена, обновляем страницу принудительно")
                    self.driver.refresh()
                    print("   ✅ Страница обновлена принудительно")
            else:
                print("   ✅ Страница уже готова к работе")

            # 3) Ждем загрузки
            print("📌 3) Ожидание загрузки страницы...")
            self.browser.wait_medium()

            print("\n✅ Vizard успешно обновлен!")
            return True

        except Exception as e:
            print(f"❌ Ошибка при обновлении Vizard: {e}")
            return False

    def _switch_to_vizard_tab(self):
        """Переключение на вкладку Vizard"""
        try:
            # Получаем все вкладки
            handles = self.driver.window_handles

            for handle in handles:
                self.driver.switch_to.window(handle)
                current_url = self.driver.current_url.lower()

                # Проверяем, что это Vizard
                if "vizard" in current_url:
                    print(f"   ✅ Найдена вкладка Vizard: {current_url}")
                    return True

            # Если не нашли - пробуем открыть новую
            print("   ⚠️ Вкладка Vizard не найдена, открываем новую...")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get("https://vizard.ai/upload?from=home_upload")
            self.browser.wait_medium()
            return True

        except Exception as e:
            print(f"   ❌ Ошибка переключения на Vizard: {e}")
            return False

    def _check_needs_refresh(self):
        """Проверка, нужна ли кнопка Refresh"""
        try:
            # Ищем кнопку Refresh
            refresh_btn = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'refresh-btn')]")
            if refresh_btn and refresh_btn[0].is_displayed():
                return True

            # Ищем текст "Refresh page to continue"
            refresh_text = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'Refresh page to continue')]")
            if refresh_text and refresh_text[0].is_displayed():
                return True

            return False
        except:
            return False

    def _click_refresh_button(self):
        """Поиск и нажатие кнопки Refresh"""
        try:
            # Небольшая пауза для загрузки кнопки
            self.browser.wait_short()

            # Проверяем рекламу перед поиском
            self.browser.close_ad_if_exists()

            # СПОСОБ 1: Поиск по точному XPath
            try:
                refresh_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'refresh-btn')]"))
                )
                if refresh_btn and refresh_btn.is_displayed():
                    print("   🎯 Найдена кнопка Refresh (class=refresh-btn)")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", refresh_btn)
                    self.browser.wait_short()
                    self.driver.execute_script("arguments[0].click();", refresh_btn)
                    return True
            except:
                pass

            # СПОСОБ 2: Поиск по тексту
            try:
                refresh_btn = self.driver.find_element(
                    By.XPATH, "//span[contains(text(), 'Refresh page to continue')]"
                )
                if refresh_btn and refresh_btn.is_displayed():
                    print("   🎯 Найдена кнопка Refresh (по тексту)")
                    parent = refresh_btn.find_element(By.XPATH, "./ancestor::div[contains(@class, 'refresh-btn')]")
                    if parent and parent.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parent)
                        self.browser.wait_short()
                        self.driver.execute_script("arguments[0].click();", parent)
                        return True
            except:
                pass

            # СПОСОБ 3: Поиск по data-v атрибуту
            try:
                refresh_btn = self.driver.find_element(
                    By.CSS_SELECTOR, "div[data-v-17a3293c][class*='refresh-btn']"
                )
                if refresh_btn and refresh_btn.is_displayed():
                    print("   🎯 Найдена кнопка Refresh (data-v атрибут)")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", refresh_btn)
                    self.browser.wait_short()
                    self.driver.execute_script("arguments[0].click();", refresh_btn)
                    return True
            except:
                pass

            # СПОСОБ 4: Поиск по иконке ThinRight
            try:
                refresh_btn = self.driver.find_element(
                    By.XPATH,
                    "//iconpark-icon[contains(@name, 'ThinRight')]/ancestor::div[contains(@class, 'refresh-btn')]"
                )
                if refresh_btn and refresh_btn.is_displayed():
                    print("   🎯 Найдена кнопка Refresh (по иконке)")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", refresh_btn)
                    self.browser.wait_short()
                    self.driver.execute_script("arguments[0].click();", refresh_btn)
                    return True
            except:
                pass

            # СПОСОБ 5: Поиск по всем div с refresh-btn
            try:
                refresh_btns = self.driver.find_elements(By.CLASS_NAME, "refresh-btn")
                for btn in refresh_btns:
                    if btn and btn.is_displayed():
                        print("   🎯 Найдена кнопка Refresh (перебор)")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                        self.browser.wait_short()
                        self.driver.execute_script("arguments[0].click();", btn)
                        return True
            except:
                pass

            print("   ❌ Не удалось найти кнопку Refresh ни одним способом")
            return False

        except Exception as e:
            print(f"   ❌ Ошибка при поиске кнопки Refresh: {e}")
            return False

    def wait_for_page_load(self, timeout=30):
        """Ожидание загрузки страницы Vizard"""
        try:
            print("   ⏳ Ожидание загрузки страницы...")

            # Ждем, пока страница загрузится
            self.wait.until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Дополнительная пауза для загрузки динамического контента
            self.browser.wait_medium()
            print("   ✅ Страница загружена")
            return True

        except Exception as e:
            print(f"   ⚠️ Ошибка ожидания загрузки: {e}")
            return False

    def get_vizard_status(self):
        """Получение текущего статуса Vizard"""
        try:
            # Проверяем, есть ли кнопка загрузки видео
            upload_btn = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Upload')]")

            if upload_btn and upload_btn[0].is_displayed():
                return "ready"
            else:
                return "unknown"
        except:
            return "unknown"