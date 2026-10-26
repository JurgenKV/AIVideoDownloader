# classes/ui.py
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Делаем корень доступным и для dev, и для frozen
if getattr(sys, 'frozen', False):
    _BASE = sys._MEIPASS            # распакованный бандл
else:
    _BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from ai_config import AIConfig
from utils.pause_controller import PauseController, StopRequested


TEMPLATE_NAMES = ["Default", "Modern", "Bouncy", "Mr. Beast",
                  "Business", "Blur", "Fit video", "Tech"]
DEFAULT_DOMAIN = "deepmails.org"


# ================================================================
# УТИЛИТЫ
# ================================================================
def mark_video_as_finished(video_path):
    try:
        folder = os.path.dirname(video_path)
        filename = os.path.basename(video_path)
        name, ext = os.path.splitext(filename)
        new_path = os.path.join(folder, f"{name}_(finished){ext}")
        os.rename(video_path, new_path)
        return new_path
    except Exception:
        return video_path


def get_videos_to_process(video_loader):
    return [
        v for v in video_loader.get_video_files()
        if "_(finished)" not in os.path.basename(v)
    ]


# ================================================================
# ПАРТИЯ
# ================================================================
def process_video_batch(browser, video_batch, batch_index, total_batches,
                        config, pause_ctrl, log_cb, email_cb):
    from classes.email_manager import EmailManager
    from classes.vizard_registrator import VizardRegistrator
    from classes.email_confirmer import EmailConfirmer
    from classes.vizard_manager import VizardManager
    from classes.vizard_uploader import VizardUploader
    from classes.vizard_downloader import VizardDownloader

    log_cb(f"\n{'=' * 50}")
    log_cb(f"🔥 ПАРТИЯ {batch_index}/{total_batches}  ({len(video_batch)} видео)")
    log_cb(f"{'=' * 50}")

    # --- 1. Временная почта на нужном домене ---
    em = EmailManager(browser, target_domain=config.TEMP_MAIL_DOMAIN)
    if not em.get_email():
        log_cb("⚠️ Не удалось получить временный email")
        return False

    email = em.get_email_address()
    config.TEMP_EMAIL = email
    AIConfig.save()
    email_cb(email)
    log_cb(f"📧 Используется email: {email}")

    pause_ctrl.check_point()

    # --- 2. Регистрация ---
    if not VizardRegistrator(browser).register(email):
        log_cb("⚠️ Проблемы с регистрацией")
        return False
    pause_ctrl.check_point()

    # --- 3. Подтверждение ---
    EmailConfirmer(browser).confirm_email()
    pause_ctrl.check_point()

    # --- 4. Refresh ---
    VizardManager(browser).refresh_vizard_page()
    pause_ctrl.check_point()

    # --- 5. Загрузка ---
    uploader = VizardUploader(browser, config=config)
    if not uploader.upload_videos(video_batch):
        log_cb("⚠️ Проблемы с загрузкой видео")
        return False
    pause_ctrl.check_point()

    # --- 6. Скачивание ---
    if not VizardDownloader(browser).download_all_videos():
        log_cb("⚠️ Проблемы со скачиванием")
        return False

    # --- 7. Пометить как обработанные ---
    for v in video_batch:
        mark_video_as_finished(v)

    log_cb(f"✅ Партия {batch_index} обработана")
    return True


# ================================================================
# ГЛАВНЫЙ ПАЙПЛАЙН
# ================================================================
def run_pipeline(config, pause_ctrl: PauseController, log_cb, email_cb):
    browser = None
    try:
        from classes.browser_manager import BrowserManager
        from classes.video_loader import VideoLoader

        video_loader = VideoLoader("videos_input")
        if not video_loader.load_videos():
            log_cb("❌ В папке videos_input нет видео")
            return

        all_videos = get_videos_to_process(video_loader)
        if not all_videos:
            log_cb("✅ Все видео уже обработаны")
            return
        log_cb(f"📊 Осталось обработать: {len(all_videos)}")

        pause_ctrl.check_point()

        per_acc = getattr(config, "MAX_VIDEOS", 3)
        batches = [all_videos[i:i + per_acc]
                   for i in range(0, len(all_videos), per_acc)]
        total = len(batches)
        log_cb(f"📦 Партий: {total} (по {per_acc} видео)")
        log_cb(f"📮 Домен временной почты: @{config.TEMP_MAIL_DOMAIN}")

        for idx, batch in enumerate(batches, 1):
            pause_ctrl.check_point()

            browser = BrowserManager(
                speed=config.SPEED,
                pause_controller=pause_ctrl,
            )
            if not browser.init_browser():
                log_cb("❌ Не удалось запустить браузер")
                continue

            try:
                process_video_batch(
                    browser, batch, idx, total,
                    config, pause_ctrl, log_cb, email_cb,
                )
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
                browser = None

            if idx < total:
                log_cb("🔄 Следующая партия — новый email на том же домене")
                log_cb("⏳ Пауза 10 сек между партиями...")
                pause_ctrl.sleep(10)

        log_cb("\n🎉 ВСЕ ПАРТИИ ЗАВЕРШЕНЫ")

    except StopRequested:
        log_cb("⛔ Процесс остановлен пользователем")
    except Exception as e:
        import traceback
        log_cb(f"❌ Ошибка: {e}\n{traceback.format_exc()}")
    finally:
        try:
            if browser:
                browser.close()
        except Exception:
            pass


# ================================================================
# UI
# ================================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vizard Auto Generator")
        self.geometry("820x900")
        self.minsize(640, 680)

        self.pause_ctrl = PauseController()
        self.worker = None

        AIConfig.load()
        self._build_ui()
        self._load_from_config()

    # ---------- построение интерфейса ----------
    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        # ============================================================
        # Блок: временная почта
        # ============================================================
        f1 = ttk.LabelFrame(self, text="Временная почта (temporary-mail.net)")
        f1.pack(fill="x", **pad)

        # -- строка домена --
        row_domain = ttk.Frame(f1)
        row_domain.pack(fill="x", padx=8, pady=(6, 2))

        ttk.Label(row_domain, text="Домен:", width=9).pack(side="left")
        ttk.Label(row_domain, text="@", font=("Consolas", 12)).pack(side="left")
        self.domain_var = tk.StringVar()
        ttk.Entry(row_domain, textvariable=self.domain_var,
                  font=("Consolas", 12)).pack(side="left", fill="x",
                                              expand=True, padx=(2, 6))
        ttk.Button(row_domain, text="🔄 Сбросить",
                   command=self.on_reset_domain).pack(side="left")

        # -- строка текущего email --
        row_email = ttk.Frame(f1)
        row_email.pack(fill="x", padx=8, pady=(2, 6))

        ttk.Label(row_email, text="Email сессии:", width=9).pack(side="left")
        self.current_email_var = tk.StringVar()
        email_entry = ttk.Entry(row_email, textvariable=self.current_email_var,
                                state="readonly", font=("Consolas", 12),
                                foreground="#1a4d1a")
        email_entry.pack(side="left", fill="x", expand=True, padx=(2, 6))
        ttk.Button(row_email, text="📋 Копировать",
                   command=self.on_copy_email).pack(side="left")

        # -- hint --
        hint = ttk.Label(
            f1,
            text=("Домен можно менять — при старте приложение выберет его в "
                  "temporary-mail.net.\n"
                  "Email сессии генерируется автоматически и обновляется "
                  "каждую партию (записывается в config.json)."),
            foreground="#666",
            justify="left",
        )
        hint.pack(anchor="w", padx=8, pady=(0, 6))

        # ============================================================
        # AI параметры
        # ============================================================
        f2 = ttk.LabelFrame(self, text="AI параметры")
        f2.pack(fill="x", **pad)

        def add_row(row, label, widget):
            ttk.Label(f2, text=label).grid(row=row, column=0, sticky="w",
                                           padx=6, pady=4)
            widget.grid(row=row, column=1, sticky="ew", padx=6)

        self.template_var = tk.StringVar()
        add_row(0, "Шаблон:",
                ttk.Combobox(f2, textvariable=self.template_var,
                             state="readonly", values=TEMPLATE_NAMES))

        self.length_var = tk.StringVar()
        add_row(1, "Длина клипа:",
                ttk.Combobox(f2, textvariable=self.length_var,
                             state="readonly",
                             values=["Any length", "<30s", "30s-60s",
                                     "60s-90s", "90s-3mins", ">3mins"]))

        self.language_var = tk.StringVar()
        add_row(2, "Язык:", ttk.Entry(f2, textvariable=self.language_var))

        self.model_var = tk.StringVar()
        add_row(3, "Модель:", ttk.Entry(f2, textvariable=self.model_var))

        self.speed_var = tk.StringVar()
        add_row(4, "Скорость:",
                ttk.Combobox(f2, textvariable=self.speed_var,
                             state="readonly",
                             values=["slow", "medium", "fast"]))

        self.max_videos_var = tk.IntVar()
        add_row(5, "Видео на аккаунт:",
                ttk.Spinbox(f2, from_=1, to=20,
                            textvariable=self.max_videos_var))

        self.upload_wait_var = tk.IntVar()
        add_row(6, "Ожидание загрузки (сек):",
                ttk.Spinbox(f2, from_=30, to=600, increment=30,
                            textvariable=self.upload_wait_var))

        f2.columnconfigure(1, weight=1)

        # ============================================================
        # Опции
        # ============================================================
        f3 = ttk.LabelFrame(self, text="Опции AI")
        f3.pack(fill="x", **pad)

        self.emoji_var = tk.BooleanVar()
        self.kw_var = tk.BooleanVar()
        self.broll_var = tk.BooleanVar()
        self.silence_var = tk.BooleanVar()
        self.censor_var = tk.BooleanVar()
        for text, var in [
            ("Add emojis", self.emoji_var),
            ("Highlight keywords", self.kw_var),
            ("Add B-rolls", self.broll_var),
            ("Remove silences", self.silence_var),
            ("Auto-censor", self.censor_var),
        ]:
            ttk.Checkbutton(f3, text=text, variable=var).pack(anchor="w", padx=8)

        # ============================================================
        # Кнопки
        # ============================================================
        f4 = ttk.Frame(self)
        f4.pack(fill="x", **pad)

        self.btn_start = ttk.Button(f4, text="▶ Старт", command=self.on_start)
        self.btn_pause = ttk.Button(f4, text="⏸ Пауза",
                                    command=self.on_pause, state="disabled")
        self.btn_resume = ttk.Button(f4, text="▶ Продолжить",
                                     command=self.on_resume, state="disabled")
        self.btn_stop = ttk.Button(f4, text="⛔ Стоп",
                                   command=self.on_stop, state="disabled")
        self.btn_save = ttk.Button(f4, text="💾 Сохранить настройки",
                                   command=self.on_save)

        self.btn_start.pack(side="left", padx=4)
        self.btn_pause.pack(side="left", padx=4)
        self.btn_resume.pack(side="left", padx=4)
        self.btn_stop.pack(side="left", padx=4)
        self.btn_save.pack(side="right", padx=4)

        # ============================================================
        # Лог
        # ============================================================
        f5 = ttk.LabelFrame(self, text="Лог")
        f5.pack(fill="both", expand=True, **pad)
        self.log_widget = scrolledtext.ScrolledText(
            f5, height=14, wrap="word", font=("Consolas", 9))
        self.log_widget.pack(fill="both", expand=True, padx=4, pady=4)

    # ---------- синхронизация UI <-> AIConfig ----------
    def _load_from_config(self):
        # домен: сохраняется в config, дефолт — deepmails.org
        self.domain_var.set(AIConfig.TEMP_MAIL_DOMAIN or DEFAULT_DOMAIN)
        # email сессии: последний сгенерированный (может быть пустой)
        self.current_email_var.set(AIConfig.TEMP_EMAIL or "")

        self.template_var.set(AIConfig.TEMPLATE_NAME)
        length_names = {0: "Any length", 1: "<30s", 2: "30s-60s",
                        3: "60s-90s", 4: "90s-3mins", 5: ">3mins"}
        self.length_var.set(length_names.get(AIConfig.CLIP_LENGTH, "30s-60s"))
        self.language_var.set(AIConfig.LANGUAGE)
        self.model_var.set(AIConfig.MODEL)
        self.speed_var.set(AIConfig.SPEED)
        self.max_videos_var.set(AIConfig.MAX_VIDEOS)
        self.upload_wait_var.set(AIConfig.UPLOAD_WAIT_TIME)
        self.emoji_var.set(AIConfig.ENABLE_EMOJIS)
        self.kw_var.set(AIConfig.ENABLE_KEYWORDS)
        self.broll_var.set(AIConfig.ENABLE_B_ROLLS)
        self.silence_var.set(AIConfig.ENABLE_SILENCE_REMOVAL)
        self.censor_var.set(AIConfig.ENABLE_AUTO_CENSOR)

    def _apply_to_config(self):
        # домен нормализуем: убираем @ и пробелы
        domain = self.domain_var.get().strip().lstrip("@").lower()
        if not domain:
            domain = DEFAULT_DOMAIN
            self.domain_var.set(domain)
        AIConfig.TEMP_MAIL_DOMAIN = domain

        # TEMP_EMAIL не трогаем — это runtime-значение, управляется из pipeline

        AIConfig.TEMPLATE_NAME = self.template_var.get()
        length_rev = {"Any length": 0, "<30s": 1, "30s-60s": 2,
                      "60s-90s": 3, "90s-3mins": 4, ">3mins": 5}
        AIConfig.CLIP_LENGTH = length_rev.get(self.length_var.get(), 2)
        AIConfig.LANGUAGE = self.language_var.get()
        AIConfig.MODEL = self.model_var.get()
        AIConfig.SPEED = self.speed_var.get()
        AIConfig.MAX_VIDEOS = int(self.max_videos_var.get())
        AIConfig.UPLOAD_WAIT_TIME = int(self.upload_wait_var.get())
        AIConfig.ENABLE_EMOJIS = self.emoji_var.get()
        AIConfig.ENABLE_KEYWORDS = self.kw_var.get()
        AIConfig.ENABLE_B_ROLLS = self.broll_var.get()
        AIConfig.ENABLE_SILENCE_REMOVAL = self.silence_var.get()
        AIConfig.ENABLE_AUTO_CENSOR = self.censor_var.get()

    def log(self, text: str):
        def _write():
            self.log_widget.insert("end", text + "\n")
            self.log_widget.see("end")
        self.after(0, _write)

    def update_email_field(self, email: str):
        """Из фонового потока: обновляет readonly-поле «Email сессии»."""
        def _update():
            self.current_email_var.set(email or "")
        self.after(0, _update)

    # ---------- обработчики кнопок ----------
    def on_reset_domain(self):
        self.domain_var.set(DEFAULT_DOMAIN)
        AIConfig.TEMP_MAIL_DOMAIN = DEFAULT_DOMAIN
        AIConfig.save()
        self.log(f"🔄 Домен сброшен на @{DEFAULT_DOMAIN}")

    def on_copy_email(self):
        email = self.current_email_var.get().strip()
        if email:
            self.clipboard_clear()
            self.clipboard_append(email)
            self.log(f"📋 Скопировано: {email}")

    def on_save(self):
        self._apply_to_config()
        AIConfig.save()
        messagebox.showinfo("Сохранено", "Настройки сохранены в config.json")

    def on_start(self):
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Уже запущено",
                                   "Дождитесь окончания или нажмите Стоп")
            return

        self._apply_to_config()

        self.pause_ctrl = PauseController()
        self.log("=" * 40)
        self.log("🚀 СТАРТ")
        self.log(f"📮 Домен: @{AIConfig.TEMP_MAIL_DOMAIN}")

        self.worker = threading.Thread(
            target=run_pipeline,
            args=(AIConfig, self.pause_ctrl, self.log, self.update_email_field),
            daemon=True,
        )
        self.worker.start()

        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.btn_resume.config(state="disabled")
        self.btn_stop.config(state="normal")

        self.after(500, self._poll_worker)

    def _poll_worker(self):
        if self.worker and not self.worker.is_alive():
            self.btn_start.config(state="normal")
            self.btn_pause.config(state="disabled")
            self.btn_resume.config(state="disabled")
            self.btn_stop.config(state="disabled")
            self.log("— поток завершён —")
        elif self.worker and self.worker.is_alive():
            self.after(500, self._poll_worker)

    def on_pause(self):
        self.pause_ctrl.pause()
        self.log("⏸️ Пауза")
        self.btn_pause.config(state="disabled")
        self.btn_resume.config(state="normal")

    def on_resume(self):
        self.pause_ctrl.resume()
        self.log("▶️ Продолжение")
        self.btn_pause.config(state="normal")
        self.btn_resume.config(state="disabled")

    def on_stop(self):
        if messagebox.askyesno("Остановка", "Прервать выполнение?"):
            self.pause_ctrl.stop()
            self.log("⛔ Запрошена остановка…")
            self.btn_pause.config(state="disabled")
            self.btn_resume.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()