import requests
import time
import os
import datetime
import platform
import threading
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import calendar
import logging
import webbrowser
import subprocess

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# === Telegram Bot Setup ===
BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_ACTUAL_CHAT_ID_HERE"


# === Cinema Code Map ===
CINEMA_CODES = {
    "Grand Mall": "389",
    "Palazzo": "388",
    "Grand Galada": "400",
    "SKLS Galaxy Mall": "410",
    "Heritage RSL": "417",
    "Marina Mall": "232",
    "Luxe": "320",
    "Escape": "359",
    "Sathyam": "331",
    "Aerohub": "432",
    "Ampa": "358",
    "VR": "523"
}

# === Screen Names for Each Theatre ===
THEATRE_SCREENS = {
    "Grand Mall": ["AUDI 01", "AUDI 02", "AUDI 03", "AUDI 04", "AUDI 05"],
    "Palazzo": ["AUDI 1", "AUDI 2", "AUDI 3", "AUDI 4", "AUDI 5", "AUDI 6", "AUDI 7", "AUDI 8", "AUDI 9"],
    "Grand Galada": ["AUDI 01", "AUDI 02", "AUDI 03", "AUDI 04", "AUDI 05"],
    "SKLS Galaxy Mall": ["AUDI 01", "AUDI 02", "AUDI 03", "AUDI 04", "AUDI 05"],
    "Heritage RSL": ["AUDI 01", "AUDI 02", "AUDI 03", "AUDI 04", "AUDI 05", "AUDI 06", "AUDI 07", "AUDI 08", "AUDI 09", "AUDI 10"],
    "Marina Mall": ["LASER 4", "SCREEN 1", "SCREEN 2", "SCREEN 3", "SCREEN 5", "SCREEN 6", "SCREEN 7", "SCREEN 8"],
    "Luxe": ["SCREEN 1", "SCREEN 2", "SCREEN 3", "SCREEN 4", "SCREEN 5", "SCREEN 6", "SCREEN 7", "SCREEN 8", "SCREEN 9", "SCREEN 10", "SCREEN 11"],
    "Escape": ["AUDI 1 BLUSH", "AUDI 2 WEAVE", "AUDI 3 SPOT", "AUDI 4 STREAK", "AUDI 5 PLUSH", "AUDI 6 FRAME", "AUDI 7 CARVE", "AUDI 8 KITES"],
    "Sathyam": ["6DEGREES", "SANTHAM", "SATHYAM", "SEASONS", "SERENE", "STUDIO-5"],
    "Aerohub": ["AUDI 01", "AUDI 02", "AUDI 03", "AUDI 04", "AUDI 05"],
    "Ampa": ["AUDI 01", "AUDI 02", "AUDI 03", "AUDI 04", "AUDI 05", "AUDI 06", "AUDI 07"],
    "VR": ["AUDI 01", "AUDI 02", "AUDI 03", "AUDI 04", "AUDI 05", "AUDI 06", "AUDI 07", "AUDI 08", "AUDI 09", "AUDI 10"]
}

# === Global Flags ===
alert_sent_map = {}
monitoring_flag = threading.Event()
CHECK_INTERVAL = 60  # seconds

# === Desktop Notification Setup ===
def setup_notifications():
    os_name = platform.system()
    if os_name == "Windows":
        try:
            import win10toast
            return True
        except ImportError:
            try:
                subprocess.run(['pip', 'install', 'win10toast'], check=True, capture_output=True)
                import win10toast
                return True
            except:
                logging.warning("❗ Could not install win10toast. Desktop notifications disabled on Windows.")
                return False
    elif os_name == "Darwin":
        try:
            subprocess.run(['which', 'osascript'], check=True, capture_output=True)
            return True
        except:
            logging.warning("❗ osascript not found. Desktop notifications disabled on macOS.")
            return False
    elif os_name == "Linux":
        try:
            subprocess.run(['which', 'notify-send'], check=True, capture_output=True)
            return True
        except:
            logging.warning("❗ notify-send not found. Desktop notifications disabled on Linux.")
            return False
    return False

NOTIFICATIONS_AVAILABLE = setup_notifications()

def send_desktop_notification(title, message, urgent=True):
    if not NOTIFICATIONS_AVAILABLE:
        return
    def _send_notification():
        try:
            os_name = platform.system()
            if os_name == "Windows":
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(title, message, duration=10, icon_path=None, threaded=True)
            elif os_name == "Darwin":
                script = f'display notification "{message}" with title "{title}" sound name "Glass"'
                subprocess.run(['osascript', '-e', script], check=True)
            elif os_name == "Linux":
                urgency = "critical" if urgent else "normal"
                subprocess.run([
                    'notify-send', '--urgency', urgency, '--app-name', 'PVR Monitor',
                    '--icon', 'dialog-information', '--expire-time', '10000', title, message
                ], check=True)
        except Exception as e:
            logging.error(f"❌ Desktop notification error: {e}")
    threading.Thread(target=_send_notification, daemon=True).start()

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        if res.status_code == 200:
            logging.info("📲 Telegram alert sent!")
        else:
            logging.warning(f"❌ Telegram failed: {res.text}")
    except Exception as e:
        logging.error(f"❌ Telegram error: {e}")

def play_alert_sound():
    def _play():
        os_name = platform.system()
        try:
            if os_name == "Darwin":
                for _ in range(5):
                    os.system("afplay /System/Library/Sounds/Glass.aiff")
                    time.sleep(1)
            elif os_name == "Windows":
                try:
                    import winsound
                    for _ in range(5):
                        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
                        time.sleep(1)
                except:
                    for _ in range(5):
                        print('\a')
                        time.sleep(1)
            elif os_name == "Linux":
                try:
                    for _ in range(5):
                        os.system("aplay /usr/share/sounds/alsa/Front_Center.wav 2>/dev/null")
                        time.sleep(1)
                except:
                    for _ in range(5):
                        print('\a')
                        time.sleep(1)
            else:
                for _ in range(5):
                    print('\a')
                    time.sleep(1)
        except Exception as e:
            logging.error(f"❌ Error playing sound: {e}")
    threading.Thread(target=_play, daemon=True).start()

def check_booking(cinema_id, selected_date):
    url = "https://api3.pvrcinemas.com/api/v1/booking/content/csessions"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer",
        "chain": "PVR",
        "city": "Chennai",
        "country": "INDIA",
        "appVersion": "1.0",
        "platform": "WEBSITE",
        "Origin": "https://www.pvrcinemas.com",
    }
    payload = {
        "city": "Chennai",
        "cid": cinema_id,
        "lat": "12.883208",
        "lng": "80.3613280",
        "dated": selected_date,
        "qr": "YES",
        "cineType": "",
        "cineTypeQR": ""
    }
    for _ in range(3):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            data = res.json()
            return data.get("output", {}).get("cinemaMovieSessions", [])
        except Exception as e:
            logging.warning(f"Retry due to API error: {e}")
            time.sleep(2)
    return []

def parse_time_12h(timestr):
    return datetime.datetime.strptime(timestr, "%I:%M %p").time()

def is_time_in_range(show_time, from_time, to_time):
    if from_time <= to_time:
        return from_time <= show_time <= to_time
    else:
        return show_time >= from_time or show_time <= to_time

def monitor_cinema(cinema_name, cinema_id, selected_date, film_name_filter, screen_name_filters, time_from, time_to):
    while not alert_sent_map.get(cinema_name) and not monitoring_flag.is_set():
        log(f"⏳ Checking {cinema_name}...")
        sessions = check_booking(cinema_id, selected_date)
        found = False
        show_details = []
        for session in sessions:
            movie = session.get("movieRe", {})
            film_name = movie.get("filmName", "")
            if film_name_filter and film_name_filter.lower() not in film_name.lower():
                continue
            for exp in session.get("experienceSessions", []):
                for show in exp.get("shows", []):
                    screen_name = show.get("screenName", "")
                    show_time_str = show.get("showTime", "")
                    subtitle = show.get("subtitle", False)
                    if screen_name_filters and screen_name not in screen_name_filters:
                        continue
                    if time_from and time_to and show_time_str:
                        try:
                            show_time = parse_time_12h(show_time_str)
                            if not is_time_in_range(show_time, time_from, time_to):
                                continue
                        except Exception:
                            continue
                    show_details.append({
                        "movie": film_name,
                        "screen": screen_name,
                        "time": show_time_str,
                        "subtitle": "Yes" if subtitle else "No"
                    })
                    found = True
        if found and show_details:
            show_lines = []
            for show in show_details:
                show_lines.append(
                    f"🎬 *{show['movie']}*\n"
                    f"• 🎥 Screen: {show['screen']}\n"
                    f"• 🕒 Time: {show['time']}\n"
                    f"• 💬 Subtitles: {show['subtitle']}\n"
                )
            show_details_msg = "\n".join(show_lines)
            telegram_msg = (
                f"🎉 *Booking is OPEN!* 🎟️\n\n"
                f"🗓️ *{selected_date}*\n"
                f"📍 *PVR: {cinema_name}, Chennai*\n"
            )
            if film_name_filter:
                telegram_msg += f"\n🎬 *Filtered Film:* {film_name_filter}"
            if screen_name_filters:
                telegram_msg += f"\n *Screens:* {', '.join(screen_name_filters)}"
            if time_from and time_to:
                telegram_msg += f"\n🕒 *Show Time:* {time_from.strftime('%I:%M %p')} - {time_to.strftime('%I:%M %p')}"
            telegram_msg += f"\n\n*Matching Shows:*\n{show_details_msg}"
            telegram_msg += f"\n🔗 [Book Now](https://www.pvrcinemas.com/cinemasessions/Chennai/qr/{cinema_id})"
            desktop_title = f"🎟️ PVR Booking Open!"
            desktop_msg = f"📍 {cinema_name} - {selected_date}\n🎬 {len(show_details)} matching shows\n\nClick to book now!"
            send_telegram(telegram_msg)
            send_desktop_notification(desktop_title, desktop_msg, urgent=True)
            play_alert_sound()
            alert_sent_map[cinema_name] = True
            log(f"✅ Booking is open for {cinema_name}!")
            log(f"🖥️ Desktop notification sent!")
            return
        else:
            log(f"🚫 No matching shows at {cinema_name}.")
        time.sleep(CHECK_INTERVAL)

# === GUI Setup ===
app = tb.Window(themename="darkly")
app.title("🍿 PVR Booking Monitor")
app.geometry("1100x850")
app.resizable(True, True)

style = tb.Style()
style.configure("Header.TLabel", font=("Segoe UI", 26, "bold"))
style.configure("SubHeader.TLabel", font=("Segoe UI", 16))
style.configure("Info.TLabel", font=("Segoe UI", 12))
style.configure("Status.TLabel", font=("Segoe UI", 13, "bold"))

cinema_vars = {cinema: tk.BooleanVar() for cinema in CINEMA_CODES.keys()}

def log(msg):
    log_box.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M:%S')} - {msg}\n")
    log_box.see(tk.END)
    logging.info(msg)

# === Custom Filter Variables ===
film_name_var = tk.StringVar()
show_time_from_var = tk.StringVar()
show_time_to_var = tk.StringVar()

def open_date_picker():
    date_picker_window = tb.Toplevel(app)
    date_picker_window.title("📅 Select Date")
    date_picker_window.geometry("450x400")
    date_picker_window.resizable(False, False)
    date_picker_window.transient(app)
    date_picker_window.grab_set()

    date_picker_window.update_idletasks()
    x = (date_picker_window.winfo_screenwidth() // 2) - (date_picker_window.winfo_width() // 2)
    y = (date_picker_window.winfo_screenheight() // 2) - (date_picker_window.winfo_height() // 2)
    date_picker_window.geometry(f"+{x}+{y}")

    today = datetime.date.today()
    current_month = today.month
    current_year = today.year

    header_frame = tb.Frame(date_picker_window)
    header_frame.pack(fill="x", padx=20, pady=20)
    nav_frame = tb.Frame(header_frame)
    nav_frame.pack(fill="x")
    month_var = tk.StringVar(value=f"{calendar.month_name[current_month]} {current_year}")
    month_label = tb.Label(nav_frame, textvariable=month_var, font=("Segoe UI", 14, "bold"))
    month_label.pack()
    nav_buttons_frame = tb.Frame(nav_frame)
    nav_buttons_frame.pack(pady=(10, 0))

    def prev_month():
        nonlocal current_month, current_year
        current_month -= 1
        if current_month < 1:
            current_month = 12
            current_year -= 1
        month_var.set(f"{calendar.month_name[current_month]} {current_year}")
        update_calendar()

    def next_month():
        nonlocal current_month, current_year
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
        month_var.set(f"{calendar.month_name[current_month]} {current_year}")
        update_calendar()

    tb.Button(nav_buttons_frame, text="◀ Previous", command=prev_month, bootstyle="outline-secondary").pack(side="left", padx=(0, 10))
    tb.Button(nav_buttons_frame, text="Next ▶", command=next_month, bootstyle="outline-secondary").pack(side="left")

    cal_frame = tb.Frame(date_picker_window)
    cal_frame.pack(fill="both", expand=True, padx=20, pady=10)
    days_header = tb.Frame(cal_frame)
    days_header.pack(fill="x", pady=(0, 10))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day in days:
        tb.Label(days_header, text=day, font=("Segoe UI", 10, "bold"), width=6).pack(side="left", padx=1)
    calendar_container = tb.Frame(cal_frame)
    calendar_container.pack(fill="both", expand=True)
    calendar_frame = tb.Frame(calendar_container)
    calendar_frame.pack(fill="both", expand=True)
    selected_date = tk.StringVar()
    date_buttons = []

    def update_calendar():
        for btn in date_buttons:
            btn.destroy()
        date_buttons.clear()
        cal = calendar.monthcalendar(current_year, current_month)
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    btn = tb.Frame(calendar_frame, width=50, height=35)
                    btn.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                else:
                    date_obj = datetime.date(current_year, current_month, day)
                    is_past = date_obj < today
                    is_today = date_obj == today
                    if is_past:
                        btn = tb.Button(calendar_frame, text=str(day), width=6, bootstyle="secondary", state="disabled")
                    else:
                        def make_date_handler(date_str):
                            return lambda: select_date(date_str)
                        date_str = f"{current_year}-{current_month:02d}-{day:02d}"
                        btn = tb.Button(calendar_frame, text=str(day), width=6, command=make_date_handler(date_str),
                                        bootstyle="success" if is_today else "primary")
                btn.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                date_buttons.append(btn)
        for i in range(7):
            calendar_frame.columnconfigure(i, weight=1)
        for i in range(len(cal)):
            calendar_frame.rowconfigure(i, weight=1)

    def select_date(date_str):
        selected_date.set(date_str)
        date_var.set(date_str)
        log(f"📅 Date selected: {date_str}")
        date_picker_window.destroy()

    update_calendar()
    btn_frame = tb.Frame(date_picker_window)
    btn_frame.pack(fill="x", padx=20, pady=20)

    def select_today():
        today_str = today.strftime("%Y-%m-%d")
        date_var.set(today_str)
        log(f"📅 Today selected: {today_str}")
        date_picker_window.destroy()

    def select_tomorrow():
        tomorrow = today + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        date_var.set(tomorrow_str)
        log(f"📅 Tomorrow selected: {tomorrow_str}")
        date_picker_window.destroy()

    tb.Button(btn_frame, text="Today", command=select_today, bootstyle="outline-success").pack(side="left", padx=(0, 5))
    tb.Button(btn_frame, text="Tomorrow", command=select_tomorrow, bootstyle="outline-success").pack(side="left", padx=(0, 5))
    tb.Button(btn_frame, text="Cancel", command=date_picker_window.destroy, bootstyle="outline-danger").pack(side="right")

# === Screen Name Checkboxes (multi-select with theatre name) ===
screen_vars = {}
screen_checkbuttons = []

def update_screen_checkboxes(*args):
    for cb in screen_checkbuttons:
        cb.destroy()
    screen_checkbuttons.clear()
    screen_vars.clear()
    selected_cinemas = [cinema for cinema, var in cinema_vars.items() if var.get()]
    screens = []
    for cinema in selected_cinemas:
        for screen in THEATRE_SCREENS.get(cinema, []):
            label = f"{cinema} - {screen}"
            screens.append((cinema, screen, label))
    for cinema, screen, label in sorted(screens, key=lambda x: (x[0], x[1])):
        var = tk.BooleanVar()
        cb = tb.Checkbutton(screen_scrollable_frame, text=label, variable=var, bootstyle="round-toggle")
        cb.pack(anchor="w", padx=5, pady=1)
        screen_vars[(cinema, screen)] = var
        screen_checkbuttons.append(cb)

def select_all_screens_cb():
    for var in screen_vars.values():
        var.set(True)

def clear_all_screens_cb():
    for var in screen_vars.values():
        var.set(False)

def get_selected_screens_cb():
    return [screen for (cinema, screen), var in screen_vars.items() if var.get()]

def start_monitoring():
    monitoring_flag.clear()
    alert_sent_map.clear()
    selected_cinemas = [cinema for cinema, var in cinema_vars.items() if var.get()]
    selected_date = date_var.get().strip()
    try:
        datetime.datetime.strptime(selected_date, "%Y-%m-%d")
    except ValueError:
        Messagebox.show_error("Invalid Date", "Please select a valid date using the date picker.")
        return
    if not selected_cinemas:
        Messagebox.show_error("No Selection", "Please select at least one cinema.")
        return
    film_name_filter = film_name_var.get().strip()
    screen_name_filters = get_selected_screens_cb()
    if not screen_name_filters:
        screen_name_filters = []
    time_from = time_to = None
    if show_time_from_var.get() and show_time_to_var.get():
        try:
            time_from = parse_time_12h(show_time_from_var.get())
            time_to = parse_time_12h(show_time_to_var.get())
        except Exception:
            Messagebox.show_error("Invalid Time", "Please enter valid show times (e.g., 04:00 PM).")
            return
    log(f"✅ Monitoring {', '.join(selected_cinemas)} on {selected_date} every {CHECK_INTERVAL} seconds...")
    send_telegram(f"🔍 *Monitoring started!*\n\n🎬 *Theatres:* {', '.join(selected_cinemas)}\n📅 *Date:* {selected_date}")
    send_desktop_notification(
        "🔍 PVR Monitor Started",
        f"Monitoring {len(selected_cinemas)} cinemas for {selected_date}\nYou'll be alerted when bookings open!",
        urgent=False
    )
    status_label.config(text="🟢 MONITORING ACTIVE", bootstyle="success")
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")
    for cinema in selected_cinemas:
        cinema_id = CINEMA_CODES[cinema]
        alert_sent_map[cinema] = False
        threading.Thread(
            target=monitor_cinema,
            args=(cinema, cinema_id, selected_date, film_name_filter, screen_name_filters, time_from, time_to),
            daemon=True
        ).start()

def stop_monitoring():
    monitoring_flag.set()
    log("🛑 Monitoring stopped.")
    send_telegram("🛑 *Monitoring stopped manually.*")
    send_desktop_notification("🛑 PVR Monitor Stopped", "Monitoring has been stopped manually.", urgent=False)
    status_label.config(text="🔴 MONITORING STOPPED", bootstyle="danger")
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")

def select_all_cinemas():
    for var in cinema_vars.values():
        var.set(True)
    update_screen_checkboxes()

def clear_selection():
    for var in cinema_vars.values():
        var.set(False)
    update_screen_checkboxes()

def clear_logs():
    log_box.delete(1.0, tk.END)

def test_notifications():
    send_desktop_notification(
        "🎟️ PVR Monitor Test",
        "Desktop notifications are working!\nYou'll receive alerts like this when bookings open.",
        urgent=False
    )
    telegram_test_msg = "🧪 *Test Notification* 🧪\n\n✅ Telegram alerts are working!\n\nYou'll receive booking alerts like this when shows become available.\n\n🎬 *PVR Booking Monitor* - Ready to go!"
    send_telegram(telegram_test_msg)
    log("🧪 Test notifications sent to both desktop and Telegram!")
    log("📲 Check your Telegram chat for the test message!")

def open_github():
    webbrowser.open("https://github.com/sureshpk36")

main_container = tb.Frame(app)
main_container.pack(fill="both", expand=True, padx=20, pady=20)

header_frame = tb.Frame(main_container)
header_frame.pack(fill="x", pady=(0, 20))
title_label = tb.Label(header_frame, text="🍿 PVR Booking Monitor", style="Header.TLabel")
title_label.pack()
subtitle_label = tb.Label(header_frame, text="Never miss a movie booking in Chennai!", style="SubHeader.TLabel")
subtitle_label.pack(pady=(5, 0))

content_frame = tb.Frame(main_container)
content_frame.pack(fill="both", expand=True)

# --- LEFT PANEL ---
left_panel = tb.Frame(content_frame)
left_panel.pack(side="left", fill="y", padx=(0, 20), pady=(0, 0), anchor="n")

# Cinema Selection
cinema_group = tb.LabelFrame(left_panel, text="🎬 Cinemas", padding=15)
cinema_group.pack(fill="x", pady=(0, 18))
cinema_scroll_frame = tb.Frame(cinema_group)
cinema_scroll_frame.pack(fill="both", expand=True)
canvas = tk.Canvas(cinema_scroll_frame, height=180, bg="#232323", highlightthickness=0)
scrollbar = tb.Scrollbar(cinema_scroll_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tb.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
for cinema in CINEMA_CODES.keys():
    checkbox = tb.Checkbutton(
        scrollable_frame,
        text=cinema,
        variable=cinema_vars[cinema],
        bootstyle="primary-round-toggle",
        command=update_screen_checkboxes
    )
    checkbox.pack(anchor="w", pady=2, padx=5)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
sel_btns = tb.Frame(cinema_group)
sel_btns.pack(fill="x", pady=(8, 0))
tb.Button(sel_btns, text="Select All", command=select_all_cinemas, bootstyle="outline-info").pack(side="left", padx=(0, 5))
tb.Button(sel_btns, text="Clear", command=clear_selection, bootstyle="outline-secondary").pack(side="left")

# Date Selection
date_group = tb.LabelFrame(left_panel, text="📅 Date", padding=15)
date_group.pack(fill="x", pady=(0, 18))
date_var = tk.StringVar()
date_entry = tb.Entry(date_group, textvariable=date_var, font=("Segoe UI", 12), state="readonly", width=16)
date_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
tb.Button(date_group, text="📅 Pick", command=open_date_picker, bootstyle="primary").pack(side="left")

# --- FILTER PANEL ---
filter_group = tb.LabelFrame(left_panel, text="🔍 Filters", padding=15)
filter_group.pack(fill="x", pady=(0, 18))

# Film Name
tb.Label(filter_group, text="Film Name (optional):", style="Info.TLabel").pack(anchor="w", pady=(0, 2))
film_name_entry = tb.Entry(filter_group, textvariable=film_name_var, font=("Segoe UI", 11))
film_name_entry.pack(fill="x", pady=(0, 8))

# Screen Name Checkboxes (multi-select, with theatre name)
tb.Label(filter_group, text="Screen(s) (optional):", style="Info.TLabel").pack(anchor="w", pady=(0, 2))
screen_scroll_canvas = tk.Canvas(filter_group, height=110, bg="#232323", highlightthickness=0)
screen_scrollbar = tb.Scrollbar(filter_group, orient="vertical", command=screen_scroll_canvas.yview)
screen_scrollable_frame = tb.Frame(screen_scroll_canvas)
screen_scrollable_frame.bind(
    "<Configure>",
    lambda e: screen_scroll_canvas.configure(scrollregion=screen_scroll_canvas.bbox("all"))
)
screen_scroll_canvas.create_window((0, 0), window=screen_scrollable_frame, anchor="nw")
screen_scroll_canvas.configure(yscrollcommand=screen_scrollbar.set)
screen_scroll_canvas.pack(side="left", fill="x", expand=True)
screen_scrollbar.pack(side="right", fill="y")
screen_btn_frame = tb.Frame(filter_group)
screen_btn_frame.pack(fill="x", pady=(0, 8))
tb.Button(screen_btn_frame, text="Select All", command=select_all_screens_cb, bootstyle="outline-info").pack(side="left", padx=(0, 5))
tb.Button(screen_btn_frame, text="Clear", command=clear_all_screens_cb, bootstyle="outline-secondary").pack(side="left")

# Show Time Range
show_time_frame = tb.Frame(filter_group)
show_time_frame.pack(fill="x", pady=(0, 5))
tb.Label(show_time_frame, text="Show Time Range (optional):", style="Info.TLabel").pack(anchor="w", pady=(0, 2))
from_label = tb.Label(show_time_frame, text="From:", style="Info.TLabel")
from_label.pack(side="left", padx=(0, 2))
show_time_from_entry = tb.Entry(show_time_frame, textvariable=show_time_from_var, width=10, font=("Segoe UI", 11))
show_time_from_entry.pack(side="left", padx=(0, 8))
to_label = tb.Label(show_time_frame, text="To:", style="Info.TLabel")
to_label.pack(side="left", padx=(0, 2))
show_time_to_entry = tb.Entry(show_time_frame, textvariable=show_time_to_var, width=10, font=("Segoe UI", 11))
show_time_to_entry.pack(side="left", padx=(0, 2))
tb.Label(show_time_frame, text="(e.g., 04:00 PM)", style="Info.TLabel").pack(side="left", padx=(4, 0))

# Control Buttons
control_frame = tb.Frame(left_panel)
control_frame.pack(fill="x", pady=(0, 18))
start_btn = tb.Button(control_frame, text="▶️ Start Monitoring", command=start_monitoring, bootstyle="success", width=18)
start_btn.pack(pady=(0, 10))
stop_btn = tb.Button(control_frame, text="⏹️ Stop Monitoring", command=stop_monitoring, bootstyle="danger", width=18, state="disabled")
stop_btn.pack(pady=(0, 10))
test_btn = tb.Button(control_frame, text="🧪 Test Notification", command=test_notifications, bootstyle="info", width=18)
test_btn.pack()

status_label = tb.Label(left_panel, text="🔴 MONITORING STOPPED", style="Status.TLabel", bootstyle="danger")
status_label.pack(pady=(15, 0))
notif_status = "🖥️ Desktop Notifications: " + ("✅ Enabled" if NOTIFICATIONS_AVAILABLE else "❌ Disabled")
notif_label = tb.Label(left_panel, text=notif_status, style="Info.TLabel")
notif_label.pack(pady=(5, 0))

# --- RIGHT PANEL: LOGS ---
right_panel = tb.LabelFrame(content_frame, text="📋 Activity Logs", padding=20)
right_panel.pack(side="left", fill="both", expand=True, padx=(0, 0), pady=(0, 0))
log_control_frame = tb.Frame(right_panel)
log_control_frame.pack(fill="x", pady=(0, 10))
tb.Button(log_control_frame, text="Clear Logs", command=clear_logs, bootstyle="outline-warning").pack(side="right")
log_box = tk.Text(
    right_panel, 
    height=25, 
    font=("Consolas", 11), 
    bg="#1e1e1e", 
    fg="#00ff00",
    insertbackground="white",
    borderwidth=0,
    highlightthickness=1,
    highlightcolor="#007acc"
)
log_box.pack(fill="both", expand=True)

footer_frame = tb.Frame(main_container)
footer_frame.pack(fill="x", pady=(20, 0))
made_by_frame = tb.Frame(footer_frame)
made_by_frame.pack()
tb.Label(made_by_frame, text="Made by Suresh", font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 10))
github_btn = tb.Button(
    made_by_frame, 
    text="🔗 GitHub Profile", 
    command=open_github, 
    bootstyle="outline-info"
)
github_btn.pack(side="left")

today = datetime.date.today().strftime("%Y-%m-%d")
date_var.set(today)
log("🚀 PVR Booking Monitor initialized successfully!")
if NOTIFICATIONS_AVAILABLE:
    log("🖥️ Desktop notifications enabled for your platform!")
else:
    log("❗ Desktop notifications not available on this system.")
log("📋 Select cinemas, pick a date, set filters, and start monitoring!")

def keep_awake():
    os_name = platform.system()
    if os_name == "Windows":
        import ctypes
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_AWAYMODE_REQUIRED = 0x00000040
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED)
        try:
            while True:
                time.sleep(30)
                ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED)
        except Exception:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    elif os_name == "Darwin":
        proc = subprocess.Popen(["caffeinate"])
        try:
            proc.wait()
        except Exception:
            proc.terminate()
    elif os_name == "Linux":
        proc = subprocess.Popen(["systemd-inhibit", "--what=handle-lid-switch:sleep", "--mode=block", "sleep", "infinity"])
        try:
            proc.wait()
        except Exception:
            proc.terminate()
    else:
        print("Unsupported OS for keep awake feature")

threading.Thread(target=keep_awake, daemon=True).start()

for var in cinema_vars.values():
    var.trace_add("write", update_screen_checkboxes)

app.mainloop()
