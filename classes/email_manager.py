# classes/email_manager.py
from selenium.webdriver.common.by import By


class EmailManager:
    """Класс для работы с временной почтой"""

    def __init__(self, browser_manager, target_domain="deepmails.org"):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait
        self.email = None

        # Нормализуем домен (убираем @ и пробелы)
        self.target_domain = (target_domain or "deepmails.org").strip().lstrip("@").lower()

        self.max_attempts = 20
        self.retry_delay = 8

    # ------------------------------------------------------------------
    def get_email(self):
        """Получение email с temporary-mail.net на нужном домене"""
        print("\n" + "=" * 50)
        print("ШАГ 3: Работа с временной почтой")
        print("=" * 50)
        print(f"🎯 Домен: @{self.target_domain}")

        try:
            print("🌐 Переход на temporary-mail.net...")
            self.driver.get("https://www.temporary-mail.net/")
            self.browser.wait_medium()

            print("   🔍 Проверка и удаление рекламы...")
            self.browser.close_ad_with_retry(max_attempts=3)

            print("\n📌 1) Нажимаем кнопку Activate...")
            self._click_activate()
            self.browser.wait_short()

            print("\n📌 2) Нажимаем кнопку change...")
            self._click_change()
            self.browser.wait_short()

            print(f"\n📌 3) Выбираем домен @{self.target_domain}...")
            if not self._select_domain(self.target_domain):
                print(f"   ⚠️ Не удалось выбрать @{self.target_domain}")
                print(f"   ℹ️ Будет использован домен по умолчанию (если сгенерируется)")
            self.browser.wait_medium()

            print("\n📌 4) Получение email...")
            if not self._extract_email_with_retry():
                print("   ❌ Не удалось получить email")
                return False

            # Проверка, что домен совпадает
            if "@" in (self.email or ""):
                actual_domain = self.email.split("@", 1)[1]
                if actual_domain.lower() != self.target_domain:
                    print(f"   ⚠️ Получен домен @{actual_domain}, "
                          f"а запрашивали @{self.target_domain}")

            return True

        except Exception as e:
            print(f"❌ Ошибка работы с временной почтой: {e}")
            return False

    # ------------------------------------------------------------------
    def _extract_email_with_retry(self):
        print(f"   🔄 Максимум попыток: {self.max_attempts}, задержка: {self.retry_delay} сек")

        for attempt in range(1, self.max_attempts + 1):
            try:
                self.browser.check_pause()
                self.browser.close_ad_if_exists()

                methods = [
                    (By.ID, "active-mail"),
                    (By.CSS_SELECTOR, "input#active-mail"),
                    (By.XPATH, "//input[@id='active-mail']"),
                    (By.CSS_SELECTOR, "input[type='text'][readonly]"),
                ]

                for by, value in methods:
                    try:
                        email_input = self.driver.find_element(by, value)
                        if email_input:
                            email = email_input.get_attribute("value")
                            if email and "@" in email and email != "Loading...":
                                self.email = email
                                print(f"\n{'=' * 50}")
                                print("✅ EMAIL УСПЕШНО ПОЛУЧЕН!")
                                print(f"📧 Email: {self.email}")
                                print(f"   ⏱️ Попытка: {attempt}/{self.max_attempts}")
                                print(f"{'=' * 50}\n")
                                return True
                    except:
                        continue

                if attempt < self.max_attempts:
                    print(f"   ⏳ Email не получен, повтор "
                          f"{attempt + 1}/{self.max_attempts} через {self.retry_delay} сек...")
                    try:
                        refresh_btn = self.driver.find_element(By.ID, "refresh-btn")
                        if refresh_btn and refresh_btn.is_displayed():
                            refresh_btn.click()
                            print("   🔄 Кнопка Check emails нажата")
                    except:
                        try:
                            refresh_btn = self.driver.find_element(
                                By.XPATH, "//button[contains(text(), 'Check emails')]"
                            )
                            if refresh_btn and refresh_btn.is_displayed():
                                refresh_btn.click()
                                print("   🔄 Кнопка Check emails нажата (альтернативный способ)")
                        except:
                            pass

                    self.browser._sleep(self.retry_delay)

            except Exception as e:
                print(f"   ⚠️ Ошибка при попытке {attempt}: {e}")
                if attempt < self.max_attempts:
                    self.browser._sleep(self.retry_delay)
                continue

        print(f"\n❌ НЕ УДАЛОСЬ ПОЛУЧИТЬ EMAIL ПОСЛЕ {self.max_attempts} ПОПЫТОК!")
        return False

    # ------------------------------------------------------------------
    def _click_activate(self):
        try:
            self.browser.close_ad_if_exists()
            methods = [
                lambda: self.driver.find_element(By.CSS_SELECTOR, "a.btn.btn-warning.activeBtn"),
                lambda: self.driver.find_element(By.XPATH, "//a[contains(text(), 'Activate')]"),
                lambda: self.driver.find_element(
                    By.XPATH, "//a[contains(@class, 'btn-warning') and contains(@class, 'activeBtn')]"),
                lambda: self.driver.find_element(By.XPATH, "//a[.//i[contains(@class, 'fa-sign-in')]]"),
                lambda: self.driver.find_element(
                    By.XPATH, "//a[@href='javascript:;' and contains(@class, 'btn-warning')]"),
            ]
            for i, method in enumerate(methods, 1):
                try:
                    button = method()
                    if button and button.is_displayed():
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", button)
                        self.browser.wait_short()
                        try:
                            button.click()
                            print(f"   ✅ Кнопка Activate нажата (способ {i})")
                            self.browser.wait_short()
                            return True
                        except:
                            try:
                                self.driver.execute_script("arguments[0].click();", button)
                                print(f"   ✅ Кнопка Activate нажата (способ {i}, JS)")
                                self.browser.wait_short()
                                return True
                            except:
                                continue
                except:
                    continue
            print("   ⚠️ Не удалось нажать Activate")
            return False
        except Exception as e:
            print(f"   ⚠️ Ошибка при нажатии Activate: {e}")
            return False

    def _click_change(self):
        try:
            self.browser.close_ad_if_exists()
            methods = [
                (By.ID, "text-change"),
                (By.XPATH, "//span[@id='text-change']"),
                (By.XPATH, "//span[contains(text(), 'change')]"),
                (By.XPATH, "//*[@data-translate='change']"),
            ]
            for by, value in methods:
                try:
                    change_btn = self.driver.find_element(by, value)
                    if change_btn and change_btn.is_displayed():
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", change_btn)
                        self.browser.wait_short()
                        try:
                            change_btn.click()
                            print("   ✅ Кнопка change нажата")
                            self.browser.wait_short()
                            return True
                        except:
                            self.driver.execute_script("arguments[0].click();", change_btn)
                            print("   ✅ Кнопка change нажата (JavaScript)")
                            self.browser.wait_short()
                            return True
                except:
                    continue
            print("   ⚠️ Не удалось нажать change")
            return False
        except Exception as e:
            print(f"   ⚠️ Ошибка при нажатии change: {e}")
            return False

    def _select_domain(self, domain):
        """Выбор домена (например 'deepmails.org')."""
        if not domain:
            domain = "deepmails.org"
        domain = domain.strip().lstrip("@").lower()

        print(f"   🔍 Поиск пункта @{domain}...")

        try:
            self.browser.close_ad_if_exists()

            methods = [
                (By.XPATH, f"//a[contains(text(), '@{domain}')]"),
                (By.XPATH, f"//a[@onclick and contains(@onclick, '{domain}')]"),
                (By.XPATH, f"//li//a[contains(text(), '@{domain}')]"),
                (By.XPATH, f"//a[contains(text(), '{domain}')]"),
            ]

            for by, value in methods:
                try:
                    domain_item = self.driver.find_element(by, value)
                    if domain_item and domain_item.is_displayed():
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});", domain_item)
                        self.browser.wait_short()
                        try:
                            domain_item.click()
                            self.browser.wait_short()
                            self.browser.handle_alert(accept=True, timeout=2)
                            print(f"   ✅ Домен @{domain} выбран")
                            return True
                        except:
                            self.driver.execute_script("arguments[0].click();", domain_item)
                            self.browser.wait_short()
                            self.browser.handle_alert(accept=True, timeout=2)
                            print(f"   ✅ Домен @{domain} выбран (JavaScript)")
                            return True
                except:
                    continue

            # JS-фолбэк: перебор всех ссылок
            try:
                clicked = self.driver.execute_script(f"""
                    var links = document.querySelectorAll('a');
                    for (var i = 0; i < links.length; i++) {{
                        var t = (links[i].textContent || '').toLowerCase();
                        if (t.indexOf('@{domain}') !== -1) {{
                            links[i].click();
                            return true;
                        }}
                    }}
                    return false;
                """)
                if clicked:
                    self.browser.wait_short()
                    self.browser.handle_alert(accept=True, timeout=2)
                    print(f"   ✅ Домен @{domain} выбран (JS fallback)")
                    return True
            except:
                pass

            print(f"   ⚠️ Не удалось найти домен @{domain} в списке")
            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка при выборе домена: {e}")
            return False

    # ------------------------------------------------------------------
    def get_email_address(self):
        return self.email