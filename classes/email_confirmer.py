# classes/email_confirmer.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class EmailConfirmer:
    """Класс для подтверждения email"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait
        self.max_links_to_open = 2  # Открываем только 2 ссылки

    def confirm_email(self):
        """Подтверждение email через временную почту"""
        print("\n" + "=" * 50)
        print("ШАГ 5: Подтверждение email")
        print("=" * 50)

        try:
            # Переключаемся на вкладку с почтой
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
                print("📬 Переключились на вкладку с почтой")
            except:
                print("⚠️ Не удалось переключиться на вкладку с почтой")
                return True

            # Проверяем рекламу
            self.browser.close_ad_if_exists()

            # 1) Обновляем почту
            print("\n📌 1) Обновляем почту...")
            self._refresh_mail()

            # Проверяем рекламу после обновления
            self.browser.close_ad_if_exists()

            # 2) Ищем письмо от Vizard
            print("\n📌 2) Ищем письмо от Vizard...")
            if not self._find_vizard_email():
                print("   ⚠️ Письмо не найдено, продолжаем...")
                return True

            # Проверяем рекламу в письме
            self.browser.close_ad_if_exists()

            # 3) Ждем загрузки письма и переключаемся в iframe
            print("\n📌 3) Ожидание загрузки письма...")
            time.sleep(1)

            # Переключаемся в iframe с письмом
            if not self._switch_to_email_iframe():
                print("   ⚠️ Не удалось переключиться в iframe письма")
                return True

            # 4) Находим все ссылки из письма
            print("\n📌 4) Поиск ссылок в письме...")
            link_urls = self._get_all_links_from_iframe()

            # 5) Открываем только первые 2 ссылки
            if link_urls:
                links_to_open = link_urls[:self.max_links_to_open]
                print(
                    f"\n📌 5) Открываем {len(links_to_open)} ссылок из {len(link_urls)} (максимум {self.max_links_to_open})...")
                self._open_links(links_to_open)
            else:
                print("   ⚠️ Не найдено ссылок в письме")

            # 6) Возвращаемся в основной контент
            self.driver.switch_to.default_content()
            print("   ✅ Возврат в основной контент")

            print("\n✅ Email подтвержден!")
            return True

        except Exception as e:
            print(f"❌ Ошибка подтверждения email: {e}")
            return True

    def _refresh_mail(self):
        """Обновление почты"""
        try:
            refresh_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, "refresh-btn"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", refresh_btn)
            self.browser.wait_short()
            refresh_btn.click()
            print("   ✅ Кнопка Check emails нажата")
            print(f"   ⏳ Ожидание обновления ({self.browser.long_wait} сек)...")
            self.browser.wait_long()
        except:
            try:
                refresh_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Check emails')]")
                refresh_btn.click()
                print("   ✅ Кнопка Check emails нажата (альтернативный способ)")
                self.browser.wait_long()
            except:
                print("   ⚠️ Не удалось обновить почту")

    def _find_vizard_email(self):
        """Поиск письма от Vizard"""
        try:
            self.browser.wait_short()

            # Ищем все строки в списке писем
            emails = self.driver.find_elements(By.CSS_SELECTOR, "tbody#message-list tr")

            for email_row in emails:
                try:
                    if "Vizard" in email_row.text:
                        print(f"   📧 Найдено письмо от Vizard")
                        # Ищем ссылку внутри письма
                        links = email_row.find_elements(By.TAG_NAME, "a")
                        if links:
                            links[0].click()
                            print("   ✅ Открыто письмо от Vizard")
                            self.browser.wait_medium()
                            return True
                except:
                    continue

            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка при поиске письма: {e}")
            return False

    def _switch_to_email_iframe(self):
        """Переключение в iframe с письмом"""
        try:
            # Ищем iframe с письмом по ID
            iframes = self.driver.find_elements(By.ID, "email-iframe")

            if iframes:
                print(f"   🎯 Найден iframe с письмом (email-iframe)")
                self.driver.switch_to.frame(iframes[0])
                print("   ✅ Переключились в iframe письма")
                return True

            # Если не нашли по ID, ищем по классу
            iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[class*='email']")
            if iframes:
                print(f"   🎯 Найден iframe с письмом (class=email)")
                self.driver.switch_to.frame(iframes[0])
                print("   ✅ Переключились в iframe письма")
                return True

            print("   ⚠️ Не удалось найти iframe с письмом")
            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка при переключении в iframe: {e}")
            return False

    def _get_all_links_from_iframe(self):
        """Получение всех ссылок из iframe письма"""
        try:
            self.browser.wait_short()

            # Ждем загрузки контента в iframe
            time.sleep(1)

            # Находим все ссылки в iframe
            links = self.driver.find_elements(By.TAG_NAME, "a")

            print(f"   🔗 Найдено ссылок в письме: {len(links)}")

            # Список для хранения URL ссылок
            link_urls = []

            for i, link in enumerate(links, 1):
                try:
                    href = link.get_attribute("href")
                    if href and href.startswith("http"):
                        print(f"   🔗 Ссылка {i}: {href[:80]}...")
                        link_urls.append(href)
                except:
                    continue

            return link_urls

        except Exception as e:
            print(f"   ⚠️ Ошибка при получении ссылок: {e}")
            return []

    def _open_links(self, link_urls):
        """Открытие ссылок и закрытие вкладок"""
        try:
            # Получаем текущее количество вкладок
            initial_handles = len(self.driver.window_handles)

            # Открываем ссылки
            for url in link_urls:
                try:
                    self.driver.execute_script("window.open(arguments[0]);", url)
                    self.browser.wait_short()
                except Exception as e:
                    print(f"   ⚠️ Ошибка при открытии ссылки: {e}")

            # Ждем загрузки
            self.browser.wait_medium()

            # Получаем все вкладки
            all_handles = self.driver.window_handles

            # Закрываем все новые вкладки (кроме первой)
            self.driver.switch_to.window(all_handles[0])

            for handle in all_handles[1:]:
                try:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                    print(f"   ✅ Вкладка закрыта")
                except:
                    pass

            # Возвращаемся на первую вкладку
            self.driver.switch_to.window(all_handles[0])
            print(f"   ✅ Все новые вкладки закрыты, возврат на почту")

        except Exception as e:
            print(f"   ⚠️ Ошибка при открытии/закрытии вкладок: {e}")