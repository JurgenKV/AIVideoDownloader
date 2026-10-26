# main.py
"""
Точка входа. Запускает UI.
Сборка EXE:
pyinstaller --onefile --windowed ^
  --hidden-import selenium.webdriver.chrome.webdriver ^
  --hidden-import selenium.webdriver.chrome.service ^
  --hidden-import webdriver_manager ^
  --collect-all tkinter ^
  main.py
"""
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.path.join(BASE_DIR, "classes") not in sys.path:
    sys.path.insert(0, os.path.join(BASE_DIR, "classes"))


def main():
    try:
        from classes.ui import App
        App().mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\n❌ Ошибка запуска UI: {e}")
        if getattr(sys, "frozen", False):
            input("\n📌 Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()