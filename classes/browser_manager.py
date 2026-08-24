# classes/browser_manager.py
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Добавляем импорт утилит
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.path_utils import get_base_dir, get_videos_output_path


class BrowserManager:
    """Класс для управления браузером"""

    def __init__(self, speed="slow", download_dir=None):
        self.driver = None
        self.wait = None
        self.speed = speed
        self.base_dir = get_base_dir()

        # Настройка папки для скачиваний
        if download_dir is None:
            self.download_dir = get_videos_output_path()
        else:
            self.download_dir = download_dir

        # Создаем папку если её нет
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"📁 Создана папка для скачиваний: {self.download_dir}")

        self.set_speed_parameters()

    def set_speed_parameters(self):
        """Настройка временных параметров в зависимости от скорости"""
        if self.speed == "fast":
            self.short_wait = 0.5
            self.medium_wait = 1
            self.long_wait = 2
            self.timeout = 10
            print("⚡ Режим: БЫСТРЫЙ")
        elif self.speed == "medium":
            self.short_wait = 1
            self.medium_wait = 3
            self.long_wait = 5
            self.timeout = 20
            print("⏱️ Режим: СРЕДНИЙ")
        else:  # slow
            self.short_wait = 2
            self.medium_wait = 5
            self.long_wait = 8
            self.timeout = 30
            print("🐢 Режим: МЕДЛЕННЫЙ")

        print(f"📂 Папка для скачиваний: {self.download_dir}")

    def wait_short(self):
        time.sleep(self.short_wait)

    def wait_medium(self):
        time.sleep(self.medium_wait)

    def wait_long(self):
        time.sleep(self.long_wait)

    def _get_chromedriver_path(self):
        """
        Ищет ChromeDriver в папке с проектом.
        Сначала проверяет папку drivers/, затем корневую папку проекта.
        """
        # Список возможных имен файлов ChromeDriver
        driver_names = [
            "chromedriver.exe",  # Windows
            "chromedriver",  # Linux/Mac
            "chromedriver_win32.exe",
            "chromedriver_linux64",
            "chromedriver_mac64"
        ]

        # Проверяем папку drivers/
        drivers_folder = os.path.join(self.base_dir, "drivers")
        if os.path.exists(drivers_folder):
            for name in driver_names:
                driver_path = os.path.join(drivers_folder, name)
                if os.path.exists(driver_path):
                    print(f"   ✅ Найден ChromeDriver: {driver_path}")
                    return driver_path

        # Проверяем корневую папку
        for name in driver_names:
            driver_path = os.path.join(self.base_dir, name)
            if os.path.exists(driver_path):
                print(f"   ✅ Найден ChromeDriver: {driver_path}")
                return driver_path

        # Если не найден - возвращаем None (будет использован webdriver-manager)
        print("   ⚠️ ChromeDriver не найден в папке проекта, будет загружен автоматически...")
        return None

    # classes/browser_manager.py (исправленный метод init_browser)

    def init_browser(self):
        """Запуск браузера в режиме инкогнито - исправленная версия"""
        print("\n" + "=" * 50)
        print("ШАГ 2: Инициализация ChromeDriver (инкогнито)")
        print("=" * 50)

        try:
            # Проверяем, что Chrome действительно существует
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]

            chrome_found = False
            for path in chrome_paths:
                if os.path.exists(path):
                    print(f"   ✅ Chrome найден: {path}")
                    chrome_found = True
                    break

            if not chrome_found:
                print("   ❌ Chrome не найден в системе!")
                print("   📥 Установите Google Chrome:")
                print("   https://www.google.com/chrome/")
                return False

            chrome_options = Options()

            # ОСНОВНЫЕ АРГУМЕНТЫ ДЛЯ СТАБИЛЬНОСТИ
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")

            # ДОПОЛНИТЕЛЬНЫЕ АРГУМЕНТЫ ДЛЯ СТАБИЛЬНОСТИ
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--silent")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=ChromeWhatsNewUI")
            chrome_options.add_argument("--disable-session-crashed-bubble")
            chrome_options.add_argument("--disable-infobars")

            # Указываем путь к Chrome (важно для .exe!)
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_options.binary_location = path
                    print(f"   🎯 Используется Chrome: {path}")
                    break

            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values": {
                    "notifications": 2,
                    "popups": 2,
                    "automatic_downloads": 1
                },
                "download.default_directory": self.download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "plugins.always_open_pdf_externally": True
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Ищем ChromeDriver в корне проекта или в drivers
            chromedriver_path = self._get_chromedriver_path()

            if chromedriver_path and os.path.exists(chromedriver_path):
                print(f"🔄 Использование ChromeDriver: {chromedriver_path}")
                service = Service(executable_path=chromedriver_path)
            else:
                print("🔄 Использование webdriver-manager...")
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())

            # Создаем драйвер с дополнительными опциями
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.wait = WebDriverWait(self.driver, self.timeout)

            print(f"✅ Браузер успешно запущен в режиме инкогнито")
            print(f"📂 Скачивания будут сохраняться в: {self.download_dir}")
            return True

        except Exception as e:
            print(f"❌ Ошибка запуска браузера: {e}")

            # Проверяем наличие Chrome
            import subprocess
            try:
                result = subprocess.run(['where', 'chrome'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"   🔍 Chrome найден в PATH: {result.stdout.strip()}")
                else:
                    print("   🔍 Chrome не найден в PATH")
            except:
                pass

            import traceback
            traceback.print_exc()

            print("\n💡 Возможные решения:")
            print("   1. Установите Google Chrome с официального сайта:")
            print("      https://www.google.com/chrome/")
            print("   2. Проверьте, что ChromeDriver соответствует версии Chrome")
            print("   3. Попробуйте запустить .exe от имени администратора")
            print("   4. Перезагрузите компьютер")
            return False

    def get_download_dir(self):
        """Возвращает путь к папке скачиваний"""
        return self.download_dir

    def close_ad_if_exists(self):
        """
        Закрытие рекламного баннера путем удаления ad_position_box из DOM
        """
        try:
            time.sleep(0.3)

            try:
                ad_box = self.driver.find_element(By.ID, "ad_position_box")
                if ad_box and ad_box.is_displayed():
                    print("   🎯 Найден рекламный блок ad_position_box")
                    self.driver.execute_script("""
                        var adBox = document.getElementById('ad_position_box');
                        if (adBox) {
                            adBox.remove();
                            return true;
                        }
                        return false;
                    """)
                    print("   ✅ Рекламный блок удален из DOM")
                    time.sleep(0.5)
                    return True
            except:
                pass

            try:
                ad_containers = self.driver.find_elements(By.CLASS_NAME, "close-button-outer")
                if ad_containers:
                    print(f"   🎯 Найдено {len(ad_containers)} элементов close-button-outer")
                    for el in ad_containers:
                        try:
                            self.driver.execute_script("""
                                var el = arguments[0];
                                var parent = el.closest('#ad_position_box');
                                if (parent) {
                                    parent.remove();
                                } else {
                                    el.remove();
                                }
                            """, el)
                        except:
                            pass
                    print("   ✅ Рекламные контейнеры удалены")
                    time.sleep(0.5)
                    return True
            except:
                pass

            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                ad_iframes = []
                for iframe in iframes:
                    try:
                        src = iframe.get_attribute("src") or ""
                        if "google" in src or "doubleclick" in src or "ad" in src.lower():
                            ad_iframes.append(iframe)
                    except:
                        pass

                if ad_iframes:
                    print(f"   🎯 Найдено {len(ad_iframes)} рекламных iframe")
                    for iframe in ad_iframes:
                        try:
                            self.driver.execute_script("arguments[0].remove();", iframe)
                        except:
                            pass
                    print("   ✅ Рекламные iframe удалены")
                    time.sleep(0.5)
                    return True
            except:
                pass

            try:
                self.driver.execute_script("""
                    var adBox = document.getElementById('ad_position_box');
                    if (adBox) {
                        adBox.remove();
                    }

                    var adSelectors = [
                        '.google-ads',
                        '.adsbygoogle',
                        '.ad-container',
                        '.ad-banner',
                        '[aria-label="Close ad"]',
                        '.close-button-outer'
                    ];

                    adSelectors.forEach(function(selector) {
                        try {
                            var elements = document.querySelectorAll(selector);
                            elements.forEach(function(el) {
                                el.remove();
                            });
                        } catch(e) {}
                    });

                    var iframes = document.querySelectorAll('iframe');
                    iframes.forEach(function(iframe) {
                        try {
                            var src = iframe.getAttribute('src') || '';
                            if (src.includes('google') || src.includes('doubleclick') || src.includes('ad')) {
                                iframe.remove();
                            }
                        } catch(e) {}
                    });

                    return true;
                """)
                print("   ✅ Все рекламные элементы удалены")
                time.sleep(0.5)
                return True
            except:
                pass

            return False

        except Exception as e:
            print(f"   ⚠️ Ошибка при закрытии рекламы: {e}")
            return False

    def close_ad_with_retry(self, max_attempts=3):
        """Закрытие рекламы с повторными попытками"""
        for attempt in range(max_attempts):
            print(f"   🔄 Попытка удаления рекламы {attempt + 1}/{max_attempts}")

            if self.close_ad_if_exists():
                return True

            if attempt < max_attempts - 1:
                print(f"   ⏳ Ожидание {self.medium_wait} сек перед повторной попыткой...")
                self.wait_medium()

        print("   ⚠️ Не удалось удалить рекламу после всех попыток")
        return False

    def handle_alert(self, accept=True):
        """Обработка alert"""
        try:
            alert = self.wait.until(EC.alert_is_present())
            alert_text = alert.text
            print(f"   📬 Alert: {alert_text}")

            if accept:
                alert.accept()
                print("   ✅ Alert принят")
            else:
                alert.dismiss()
                print("   ❌ Alert отклонен")

            self.wait_short()
            return True
        except:
            return False

    def close(self):
        """Закрытие браузера"""
        if self.driver:
            print("\n🔄 Закрытие браузера...")
            try:
                self.driver.quit()
                print("✅ Браузер закрыт")
            except:
                print("⚠️ Браузер уже закрыт")