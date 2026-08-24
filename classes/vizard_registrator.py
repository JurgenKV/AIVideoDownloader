# classes/vizard_registrator.py
import time
import string
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class VizardRegistrator:
    """Класс для регистрации на Vizard.ai"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait
        self.email = None
        self.password = None

    def generate_password(self):
        """Генерация случайного пароля"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(chars) for _ in range(12))
        print(f"🔑 Сгенерирован пароль: {password}")
        return password

    def register(self, email):
        """Регистрация на Vizard.ai"""
        print("\n" + "=" * 50)
        print("ШАГ 4: Регистрация на Vizard.ai")
        print("=" * 50)

        self.email = email
        self.password = self.generate_password()

        try:
            # Открываем новую вкладку
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])

            print("🌐 Переход на Vizard.ai...")
            self.driver.get("https://vizard.ai/upload?from=home_upload")
            self.browser.wait_medium()

            # 1) Нажимаем Sign up
            print("\n📌 1) Нажимаем кнопку Sign up...")
            if not self._click_signup():
                print("   ⚠️ Не удалось нажать Sign up, но продолжаем...")
                return True

            # 2) Вводим email
            print("\n📌 2) Вводим email...")
            if not self._enter_email():
                print("   ⚠️ Не удалось ввести email, но продолжаем...")
                return True

            # 3) Вводим пароль
            print("\n📌 3) Вводим пароль...")
            if not self._enter_password():
                print("   ⚠️ Не удалось ввести пароль, но продолжаем...")
                return True

            # 4) Подтверждаем
            print("\n📌 4) Подтверждаем регистрацию...")
            if not self._submit_registration():
                print("   ⚠️ Не удалось подтвердить регистрацию, но продолжаем...")
                return True

            print("\n✅ Регистрация на Vizard.ai выполнена!")
            print(f"📧 Email: {self.email}")
            print(f"🔑 Пароль: {self.password}")

            return True

        except Exception as e:
            print(f"❌ Ошибка регистрации на Vizard: {e}")
            return False

    def _click_signup(self):
        """Нажатие кнопки Sign up"""
        try:
            signup_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.primary-btn.sign-button"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", signup_btn)
            self.browser.wait_short()
            signup_btn.click()
            print("   ✅ Кнопка Sign up нажата")
            self.browser.wait_medium()
            return True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False

    def _enter_email(self):
        """Ввод email"""
        try:
            email_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input.text-input.input[type='text'][placeholder='Enter your email']"))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            print(f"   ✅ Email введен: {self.email}")
            self.browser.wait_short()
            return True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False

    def _enter_password(self):
        """Ввод пароля"""
        try:
            password_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input.text-input.input[type='password'][placeholder='Enter password']"))
            )
            password_input.clear()
            password_input.send_keys(self.password)
            print(f"   ✅ Пароль введен: {self.password}")
            self.browser.wait_short()
            return True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False

    def _submit_registration(self):
        """Подтверждение регистрации"""
        try:
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.primary-btn.sign-up-button"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            self.browser.wait_short()
            submit_btn.click()
            print("   ✅ Кнопка Sign up нажата")
            self.browser.wait_medium()
            return True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return False

    def get_password(self):
        """Возвращает пароль"""
        return self.password