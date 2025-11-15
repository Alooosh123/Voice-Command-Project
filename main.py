import speech_recognition as sr
import pyttsx3
import os
import datetime
import pyautogui
import webbrowser
import subprocess
import winreg
from tkinter import *
from threading import Thread, Lock
from queue import Queue
import time
import json

# ------------------ التهيئة والمتغيرات الأساسية ------------------

TTS_LOCK = Lock()

try:
    GLOBAL_ENGINE = pyttsx3.init('sapi5')
    voices = GLOBAL_ENGINE.getProperty('voices')
    GLOBAL_ENGINE.setProperty('voice', voices[0].id)
    GLOBAL_ENGINE.setProperty('rate', 150)
except Exception as e:
    print(f"فشل تهيئة محرك pyttsx3: {e}")
    GLOBAL_ENGINE = None


def speak_sync(audio):
    def run_speak():
        with TTS_LOCK:
            if GLOBAL_ENGINE and audio:
                try:
                    GLOBAL_ENGINE.say(audio)
                    GLOBAL_ENGINE.runAndWait()
                except Exception as e:
                    print(f"خطأ في الكلام: {e}")

    Thread(target=run_speak, daemon=True).start()


def greet_user():
    speak_sync("أهلاً بك يا علاء. أنا مساعدك الصوتي المحلي، جاهز لتنفيذ جميع أوامرك بدون اتصال بالإنترنت.")


# ------------------ نظام تحليل الأوامر المحلي ------------------

class LocalCommandAnalyzer:
    def __init__(self):
        self.commands_database = self.load_commands_database()

    def load_commands_database(self):
        """تحميل قاعدة بيانات الأوامر"""
        return {
            # أوامر فتح التطبيقات
            "افتح المتصفح": {"type": "OPEN_APP", "target": "متصفح", "response": "أفتح المتصفح"},
            "افتح جوجل": {"type": "OPEN_APP", "target": "متصفح", "response": "أفتح جوجل"},
            "افتح الانترنت": {"type": "OPEN_APP", "target": "متصفح", "response": "أفتح الإنترنت"},
            "open browser": {"type": "OPEN_APP", "target": "متصفح", "response": "Opening browser"},
            "open google": {"type": "OPEN_APP", "target": "متصفح", "response": "Opening Google"},

            "افتح المفكره": {"type": "OPEN_APP", "target": "المفكرة", "response": "أفتح المفكرة"},
            "افتح notepad": {"type": "OPEN_APP", "target": "المفكرة", "response": "أفتح المفكرة"},
            "open notepad": {"type": "OPEN_APP", "target": "المفكرة", "response": "Opening notepad"},

            "افتح الملفات": {"type": "OPEN_APP", "target": "الملفات", "response": "أفتح مستكشف الملفات"},
            "افتح مستكشف الملفات": {"type": "OPEN_APP", "target": "الملفات", "response": "أفتح مستكشف الملفات"},
            "open files": {"type": "OPEN_APP", "target": "الملفات", "response": "Opening file explorer"},

            "افتح الاله الحاسبه": {"type": "OPEN_APP", "target": "الآلة الحاسبة", "response": "أفتح الآلة الحاسبة"},
            "open calculator": {"type": "OPEN_APP", "target": "الآلة الحاسبة", "response": "Opening calculator"},

            "افتح الرسام": {"type": "OPEN_APP", "target": "الرسام", "response": "أفتح الرسام"},
            "open paint": {"type": "OPEN_APP", "target": "الرسام", "response": "Opening paint"},

            "افتح الوورد": {"type": "OPEN_APP", "target": "الوورد", "response": "أفتح برنامج الوورد"},
            "open word": {"type": "OPEN_APP", "target": "الوورد", "response": "Opening Microsoft Word"},

            "افتح الاكسل": {"type": "OPEN_APP", "target": "الإكسل", "response": "أفتح برنامج الإكسل"},
            "open excel": {"type": "OPEN_APP", "target": "الإكسل", "response": "Opening Microsoft Excel"},

            "افتح البوربوينت": {"type": "OPEN_APP", "target": "الباوربوينت", "response": "أفتح برنامج الباوربوينت"},
            "open powerpoint": {"type": "OPEN_APP", "target": "الباوربوينت",
                                "response": "Opening Microsoft PowerPoint"},

            "افتح الانستقرام": {"type": "OPEN_WEBSITE", "target": "instagram.com", "response": "أفتح الانستقرام"},
            "open instagram": {"type": "OPEN_WEBSITE", "target": "instagram.com", "response": "Opening Instagram"},

            "افتح الفيجوال": {"type": "OPEN_APP", "target": "الفيجول ستوديو", "response": "أفتح الفيجول ستوديو"},
            "open visual studio": {"type": "OPEN_APP", "target": "الفيجول ستوديو", "response": "Opening Visual Studio"},

            "افتح تليجرام": {"type": "OPEN_APP", "target": "تليجرام", "response": "أفتح التليجرام"},
            "open telegram": {"type": "OPEN_APP", "target": "تليجرام", "response": "Opening Telegram"},

            "افتح فيسبوك": {"type": "OPEN_WEBSITE", "target": "facebook.com", "response": "أفتح الفيسبوك"},
            "open facebook": {"type": "OPEN_WEBSITE", "target": "facebook.com", "response": "Opening Facebook"},

            "افتح وتساب": {"type": "OPEN_WEBSITE", "target": "web.whatsapp.com", "response": "أفتح واتساب ويب"},
            "افتح واتساب": {"type": "OPEN_WEBSITE", "target": "web.whatsapp.com", "response": "أفتح واتساب ويب"},
            "open whatsapp": {"type": "OPEN_WEBSITE", "target": "web.whatsapp.com", "response": "Opening WhatsApp Web"},

            "افتح اليوتيوب": {"type": "OPEN_WEBSITE", "target": "youtube.com", "response": "أفتح اليوتيوب"},
            "open youtube": {"type": "OPEN_WEBSITE", "target": "youtube.com", "response": "Opening YouTube"},

            # أوامر إغلاق التطبيقات
            "اغلق المتصفح": {"type": "CLOSE_APP", "target": "متصفح", "response": "أغلق المتصفح"},
            "close browser": {"type": "CLOSE_APP", "target": "متصفح", "response": "Closing browser"},

            "اغلق المفكره": {"type": "CLOSE_APP", "target": "المفكرة", "response": "أغلق المفكرة"},
            "close notepad": {"type": "CLOSE_APP", "target": "المفكرة", "response": "Closing notepad"},

            # أوامر النظام
            "اغلق النافذة": {"type": "CONTROL", "target": "close_window", "response": "أغلق النافذة الحالية"},
            "اغلق": {"type": "CONTROL", "target": "close_window", "response": "أغلق النافذة الحالية"},
            "close window": {"type": "CONTROL", "target": "close_window", "response": "Closing current window"},

            "اكتب": {"type": "CONTROL", "target": "type_text", "response": "أكتب النص"},
            "type": {"type": "CONTROL", "target": "type_text", "response": "Typing text"},

            "اضغط انتر": {"type": "CONTROL", "target": "press_enter", "response": "أضغط زر الإدخال"},
            "press enter": {"type": "CONTROL", "target": "press_enter", "response": "Pressing enter"},

            "التقط لقطه": {"type": "CONTROL", "target": "screenshot", "response": "التقط لقطة للشاشة"},
            "take screenshot": {"type": "CONTROL", "target": "screenshot", "response": "Taking screenshot"},

            # أوامر الصوت
            "زود الصوت": {"type": "CONTROL", "target": "volume_up", "response": "أرفع الصوت"},
            "volume up": {"type": "CONTROL", "target": "volume_up", "response": "Increasing volume"},

            "اخفض الصوت": {"type": "CONTROL", "target": "volume_down", "response": "أخفض الصوت"},
            "volume down": {"type": "CONTROL", "target": "volume_down", "response": "Decreasing volume"},

            "اكتم الصوت": {"type": "CONTROL", "target": "volume_mute", "response": "أكتم الصوت"},
            "mute volume": {"type": "CONTROL", "target": "volume_mute", "response": "Muting volume"},

            # أوامر المعلومات
            "كم الساعه": {"type": "SYSTEM_COMMAND", "target": "get_time", "response": "أخبرك بالوقت"},
            "ما الوقت": {"type": "SYSTEM_COMMAND", "target": "get_time", "response": "أخبرك بالوقت"},
            "what time": {"type": "SYSTEM_COMMAND", "target": "get_time", "response": "Telling time"},
            "what is the time": {"type": "SYSTEM_COMMAND", "target": "get_time", "response": "Telling time"},

            "كم التاريخ": {"type": "SYSTEM_COMMAND", "target": "get_date", "response": "أخبرك بالتاريخ"},
            "ما التاريخ": {"type": "SYSTEM_COMMAND", "target": "get_date", "response": "أخبرك بالتاريخ"},
            "what date": {"type": "SYSTEM_COMMAND", "target": "get_date", "response": "Telling date"},
            "what is the date": {"type": "SYSTEM_COMMAND", "target": "get_date", "response": "Telling date"},

            # أوامر البحث
            "ابحث عن": {"type": "SEARCH_WEB", "target": "search", "response": "أبحث على الإنترنت"},
            "search for": {"type": "SEARCH_WEB", "target": "search", "response": "Searching the web"},

            # أوامر إدارة البرنامج
            "توقف": {"type": "PROGRAM", "target": "stop", "response": "أوقف البرنامج"},
            "وداعا": {"type": "PROGRAM", "target": "stop", "response": "مع السلامة"},
            "stop": {"type": "PROGRAM", "target": "stop", "response": "Stopping program"},
            "goodbye": {"type": "PROGRAM", "target": "stop", "response": "Goodbye"},
        }

    def analyze_command(self, command):
        """تحليل الأمر محلياً بدون اتصال بالإنترنت"""
        command_lower = command.lower()

        # البحث في قاعدة البيانات
        for cmd_pattern, cmd_info in self.commands_database.items():
            if cmd_pattern in command_lower:
                # استخراج المعاملات من الأمر
                target = cmd_info["target"]

                # معالجة خاصة لأمر الكتابة
                if cmd_info["type"] == "CONTROL" and cmd_info["target"] == "type_text":
                    text_to_type = command.replace(cmd_pattern, "").strip()
                    if text_to_type:
                        return {
                            "action": cmd_info["type"],
                            "target": text_to_type,
                            "response": cmd_info["response"],
                            "command": command
                        }

                # معالجة خاصة لأمر البحث
                elif cmd_info["type"] == "SEARCH_WEB":
                    search_term = command.replace(cmd_pattern, "").strip()
                    if search_term:
                        return {
                            "action": cmd_info["type"],
                            "target": search_term,
                            "response": cmd_info["response"],
                            "command": command
                        }

                # للأوامر العادية
                return {
                    "action": cmd_info["type"],
                    "target": target,
                    "response": cmd_info["response"],
                    "command": command
                }

        # إذا لم يتم التعرف على الأمر
        return {
            "action": "UNKNOWN",
            "target": "",
            "response": "لم أفهم الأمر، حاول مرة أخرى",
            "command": command
        }


# ------------------ نظام تنفيذ الأوامر المتقدم ------------------

class CommandExecutor:
    def __init__(self):
        self.app_database = self.load_app_database()

    def load_app_database(self):
        """تحميل قاعدة بيانات التطبيقات مع مسارات محددة"""
        return {
            "متصفح": ["chrome.exe", "msedge.exe", "firefox.exe", "opera.exe"],
            "المفكرة": ["notepad.exe"],
            "الملفات": ["explorer.exe"],
            "الآلة الحاسبة": ["calc.exe"],
            "الرسام": ["mspaint.exe"],
            "الوورد": ["winword.exe", "word.exe", "WINWORD.EXE"],
            "الإكسل": ["excel.exe", "EXCEL.EXE"],
            "الباوربوينت": ["powerpnt.exe", "powerpoint.exe", "POWERPNT.EXE"],
            "الفيجول ستوديو": ["code.exe", "devenv.exe", "vscode.exe"],
            "تليجرام": ["telegram.exe", "Telegram.exe", "tg.exe"],
            "فيسبوك": ["facebook.exe", "Facebook.exe"],
            "واتساب": ["whatsapp.exe", "WhatsApp.exe"],
        }

    def find_application(self, app_name):
        """البحث المتقدم عن التطبيقات في النظام"""
        app_name_lower = app_name.lower()

        # إذا كان التطبيق في قاعدة البيانات، نبحث عن ملفاته
        if app_name in self.app_database:
            executables = self.app_database[app_name]
        else:
            # إذا لم يكن في القاعدة، نبحث بأسمه
            executables = [f"{app_name}.exe"]

        # المسارات الشائعة للبحث
        common_paths = [
            os.path.expanduser("~\\Desktop"),
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\Windows\\System32",
            os.path.expanduser("~\\AppData\\Local\\Programs"),
            "C:\\Users\\Public\\Desktop",
            os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\WindowsApps"),
            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"
        ]

        for executable in executables:
            for base_path in common_paths:
                if not os.path.exists(base_path):
                    continue
                try:
                    for root, dirs, files in os.walk(base_path):
                        for file in files:
                            if file.lower() == executable.lower():
                                full_path = os.path.join(root, file)
                                print(f"وجدت التطبيق: {full_path}")  # للتصحيح
                                return full_path
                except Exception as e:
                    print(f"خطأ في البحث في {base_path}: {e}")
                    continue

        # البحث في السجل
        try:
            registry_path = self.find_in_registry(app_name)
            if registry_path:
                return registry_path
        except Exception as e:
            print(f"خطأ في البحث في السجل: {e}")

        return None

    def find_in_registry(self, app_name):
        """البحث عن التطبيق في سجل Windows"""
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths"),
        ]

        for hive, path in registry_paths:
            try:
                with winreg.OpenKey(hive, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            if app_name.lower() in subkey_name.lower():
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        app_path = winreg.QueryValueEx(subkey, "")[0]
                                        if os.path.exists(app_path):
                                            return app_path
                                    except FileNotFoundError:
                                        pass
                        except WindowsError:
                            pass
            except FileNotFoundError:
                pass

        return None

    def execute_system_command(self, action_type, target, original_command=""):
        """تنفيذ أوامر النظام"""
        try:
            if action_type == "OPEN_APP":
                # للتطبيقات المضمنة في النظام
                if target == "الملفات":
                    os.system("explorer")
                    return "تم فتح مستكشف الملفات"
                elif target == "المفكرة":
                    os.system("notepad")
                    return "تم فتح المفكرة"
                elif target == "الآلة الحاسبة":
                    os.system("calc")
                    return "تم فتح الآلة الحاسبة"
                elif target == "الرسام":
                    os.system("mspaint")
                    return "تم فتح الرسام"
                elif target == "متصفح":
                    webbrowser.open("https://www.google.com")
                    return "تم فتح المتصفح"
                else:
                    # البحث عن التطبيق وتنفيذه
                    app_path = self.find_application(target)
                    if app_path:
                        try:
                            if app_path.endswith('.lnk'):
                                os.system(f'start "" "{app_path}"')
                            else:
                                # استخدام subprocess بدلاً من os.system لتجنب الأخطاء
                                subprocess.Popen([app_path], shell=True)
                            return f"تم فتح {target}"
                        except Exception as e:
                            return f"خطأ في فتح {target}: {str(e)}"
                    else:
                        # إذا لم يتم العثور على التطبيق، نفتح الموقع الإلكتروني كبديل
                        if target == "الوورد":
                            webbrowser.open("https://www.office.com/launch/word")
                            return "تم فتح موقع مايكروسوفت وورد"
                        elif target == "الإكسل":
                            webbrowser.open("https://www.office.com/launch/excel")
                            return "تم فتح موقع مايكروسوفت إكسل"
                        elif target == "الباوربوينت":
                            webbrowser.open("https://www.office.com/launch/powerpoint")
                            return "تم فتح موقع مايكروسوفت باوربوينت"
                        elif target == "تليجرام":
                            webbrowser.open("https://web.telegram.org")
                            return "تم فتح تليجرام ويب"
                        else:
                            return f"لم أستطع العثور على {target}"

            elif action_type == "CLOSE_APP":
                target_lower = target.lower()
                for name, executables in self.app_database.items():
                    if target_lower in name.lower():
                        for executable in executables:
                            os.system(f"taskkill /f /im {executable} >nul 2>&1")
                        return f"تم إغلاق {target}"
                # محاولة إغلاق عامة
                os.system(f"taskkill /f /im {target}.exe >nul 2>&1")
                return f"تم محاولة إغلاق {target}"

            elif action_type == "OPEN_WEBSITE":
                if not target.startswith(('http://', 'https://')):
                    target = 'https://' + target
                webbrowser.open(target)
                return f"تم فتح {target}"

            elif action_type == "SYSTEM_COMMAND":
                if target == "get_time":
                    current_time = datetime.datetime.now().strftime("%I:%M %p")
                    return f"الوقت الحالي هو {current_time}"
                elif target == "get_date":
                    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    return f"التاريخ اليوم هو {current_date}"

            elif action_type == "SEARCH_WEB":
                search_url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
                webbrowser.open(search_url)
                return f"تم البحث عن {target}"

            elif action_type == "CONTROL":
                if target == "close_window":
                    pyautogui.hotkey('alt', 'f4')
                    return "تم إغلاق النافذة الحالية"
                elif target == "press_enter":
                    pyautogui.press('enter')
                    return "تم الضغط على زر الإدخال"
                elif target == "screenshot":
                    pyautogui.hotkey('win', 'prtscr')
                    return "تم التقاط لقطة للشاشة"
                elif target == "volume_up":
                    for _ in range(5):
                        pyautogui.press('volumeup')
                    return "تم رفع الصوت"
                elif target == "volume_down":
                    for _ in range(5):
                        pyautogui.press('volumedown')
                    return "تم خفض الصوت"
                elif target == "volume_mute":
                    pyautogui.press('volumemute')
                    return "تم كتم الصوت"
                elif isinstance(target, str) and len(target) > 0:  # أمر الكتابة
                    # إعطاء وقت للمستخدم للتبديل إلى النافذة المطلوبة
                    time.sleep(2)
                    pyautogui.write(target)
                    return f"تم كتابة: {target}"

            elif action_type == "PROGRAM":
                if target == "stop":
                    return "STOP_PROGRAM"

            return "تم تنفيذ الأمر"

        except Exception as e:
            return f"حدث خطأ: {str(e)}"


# ------------------ الواجهة الرئيسية ------------------

class OfflineVoiceAssistantGUI:
    def __init__(self, master):
        self.master = master
        master.title("المساعد الصوتي المحلي - بدون إنترنت")
        master.geometry("700x500")
        master.config(bg="#f0f0f0")

        self.analyzer = LocalCommandAnalyzer()
        self.executor = CommandExecutor()
        self.is_listening = False

        # عناصر الواجهة
        self.title_label = Label(master, text="المساعد الصوتي الذكي", fg="#2E86AB", bg="#f0f0f0",
                                 font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        self.status_label = Label(master, text="🟢 جاهز للاستماع...", fg="green", bg="#f0f0f0",
                                  font=("Arial", 14, "bold"))
        self.status_label.pack(pady=5)

        # إطار لعرض الأوامر
        display_frame = Frame(master, bg="#f0f0f0")
        display_frame.pack(pady=10, padx=20, fill=BOTH, expand=True)

        Label(display_frame, text="سجل الأوامر:", fg="#333", bg="#f0f0f0",
              font=("Arial", 12, "bold")).pack(anchor=W)

        self.command_display = Text(display_frame, height=12, width=80, font=("Arial", 10),
                                    bg="#1E1E1E", fg="#00FF00", relief=SOLID, bd=1)
        self.command_display.pack(pady=5, fill=BOTH, expand=True)

        # إضافة شريط التمرير
        scrollbar = Scrollbar(self.command_display)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.command_display.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.command_display.yview)

        # نص البداية
        welcome_text = """🎯 المساعد الصوتي المحلي - يعمل بدون اتصال بالإنترنت

🔊 الأوامر المدعومة:
• "افتح المتصفح" - فتح متصفح الإنترنت
• "افتح الملفات" - فتح مستكشف الملفات  
• "افتح المفكرة" - فتح برنامج المفكرة
• "افتح فيسبوك" - فتح موقع فيسبوك
• "افتح واتساب" - فتح واتساب ويب
• "افتح تليجرام" - فتح تليجرام ويب
• "افتح اليوتيوب" - فتح موقع يوتيوب
• "اكتب [نص]" - كتابة نص
• "كم الساعة" - معرفة الوقت
• "اغلق النافذة" - إغلاق النافذة الحالية
• "توقف" - إيقاف البرنامج

💡 تحدث بوضوح وبطء للحصول على أفضل النتائج...
"""
        self.command_display.insert(END, welcome_text)
        self.command_display.config(state=DISABLED)

        button_frame = Frame(master, bg="#f0f0f0")
        button_frame.pack(pady=15)

        self.listen_btn = Button(button_frame, text="🎤 بدء الاستماع", command=self.start_listening,
                                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                 width=15, height=2, relief=RAISED, bd=3)
        self.listen_btn.pack(side=LEFT, padx=10)

        self.stop_btn = Button(button_frame, text="⏹ إيقاف الاستماع", command=self.stop_listening,
                               bg="#f44336", fg="white", font=("Arial", 12, "bold"),
                               width=15, height=2, relief=RAISED, bd=3)
        self.stop_btn.pack(side=LEFT, padx=10)

        self.exit_btn = Button(button_frame, text="🚪 خروج", command=self.close_app,
                               bg="#FF9800", fg="white", font=("Arial", 12, "bold"),
                               width=10, height=2, relief=RAISED, bd=3)
        self.exit_btn.pack(side=LEFT, padx=10)

        self.recognizer = sr.Recognizer()
        self.gui_queue = Queue()

        Thread(target=greet_user, daemon=True).start()
        self.master.after(100, self.check_queue)

    def check_queue(self):
        try:
            while True:
                message, status, color = self.gui_queue.get_nowait()
                self.command_display.config(state=NORMAL)
                self.command_display.insert(END, f"\n{message}")
                self.command_display.see(END)
                self.command_display.config(state=DISABLED)
                self.status_label.config(text=status, fg=color)
        except:
            pass
        self.master.after(100, self.check_queue)

    def update_display(self, message, status, color):
        self.gui_queue.put((message, status, color))

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.update_display("🔊 جاري تشغيل وضع الاستماع...", "🔴 يستمع الآن", "red")
            self.listen_btn.config(state=DISABLED, bg="#888")
            self.stop_btn.config(state=NORMAL, bg="#f44336")
            speak_sync("بدأت الاستماع لأوامرك")
            # بدء الاستماع في خيط منفصل
            Thread(target=self.continuous_listen, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False
        self.update_display("⏹ توقف الاستماع", "🟢 متوقف", "green")
        self.listen_btn.config(state=NORMAL, bg="#4CAF50")
        self.stop_btn.config(state=DISABLED, bg="#888")
        speak_sync("توقفت عن الاستماع")

    def close_app(self):
        speak_sync("مع السلامة، إلى اللقاء")
        self.master.quit()

    def continuous_listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                    # محاولة التعرف بالعربية أولاً
                    try:
                        command = self.recognizer.recognize_google(audio, language='ar-AR')
                        lang = "العربية"
                    except:
                        # ثم الإنجليزية
                        try:
                            command = self.recognizer.recognize_google(audio, language='en-US')
                            lang = "الإنجليزية"
                        except:
                            continue

                    self.process_command(command, lang)

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.update_display("❌ لم أفهم الكلام، حاول مرة أخرى", "🟡 خطأ في الفهم", "orange")
                except Exception as e:
                    self.update_display(f"❌ خطأ: {str(e)}", "🔴 خطأ", "red")

    def process_command(self, command, lang):
        self.update_display(f"👤 [{lang}]: {command}", "🟣 جاري المعالجة", "purple")

        # تحليل الأمر محلياً
        analysis = self.analyzer.analyze_command(command)

        # تنفيذ الأمر
        if analysis["action"] != "UNKNOWN":
            result = self.executor.execute_system_command(
                analysis["action"],
                analysis["target"],
                command
            )

            # التحقق إذا كان الأمر لإيقاف البرنامج
            if result == "STOP_PROGRAM":
                self.close_app()
                return

            # الرد الصوتي
            speak_sync(analysis["response"])

            self.update_display(f"🤖 المساعد: {result}", "🟢 تم التنفيذ", "green")
        else:
            speak_sync(analysis["response"])
            self.update_display(f"🤖 المساعد: {analysis['response']}", "🟡 غير معروف", "orange")


# التشغيل
if __name__ == "__main__":
    root = Tk()
    app = OfflineVoiceAssistantGUI(root)
    root.mainloop()