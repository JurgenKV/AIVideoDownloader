# utils/pause_controller.py
import threading
import time


class StopRequested(Exception):
    """Исключение для корректной остановки процесса"""
    pass


class PauseController:
    """
    Управляет паузой и остановкой фонового потока.
    - pause()  — замораживает выполнение в ближайшей check_point()/sleep()
    - resume() — продолжает
    - stop()   — прерывает выполнение с StopRequested
    """

    def __init__(self):
        self._resume_event = threading.Event()
        self._resume_event.set()          # по умолчанию работаем
        self._stop_event = threading.Event()
        self._paused_state = False

    # --- управление из UI ---
    def pause(self):
        if not self._paused_state:
            self._paused_state = True
            self._resume_event.clear()
            print("⏸️  ПАУЗА")

    def resume(self):
        if self._paused_state:
            self._paused_state = False
            self._resume_event.set()
            print("▶️  ПРОДОЛЖЕНИЕ")

    def stop(self):
        print("⛔ Запрошена остановка...")
        self._stop_event.set()
        self._resume_event.set()          # разморозим, чтобы поток увидел stop

    # --- проверки из фонового кода ---
    def is_paused(self) -> bool:
        return self._paused_state

    def is_stopped(self) -> bool:
        return self._stop_event.is_set()

    def check_point(self):
        """Вызывать между шагами. Блокирует на паузе, кидает StopRequested при остановке."""
        while not self._resume_event.wait(timeout=0.2):
            if self._stop_event.is_set():
                raise StopRequested("Остановлено пользователем")
        if self._stop_event.is_set():
            raise StopRequested("Остановлено пользователем")

    def sleep(self, seconds: float):
        """Прерываемый sleep — реагирует на паузу и на стоп."""
        end = time.time() + seconds
        while time.time() < end:
            self.check_point()
            time.sleep(min(0.2, max(0.0, end - time.time())))