# 🎬 PVR Booking Monitor – Chennai 🍿

**Never miss your perfect show again.**
Monitor PVR Chennai cinema bookings effortlessly and get **real-time alerts** via Telegram, desktop notifications, and sound — now with **hyper-specific filters**.

---

## ✨ Features

* ✅ **Multi-Cinema Selection** – Choose one or more PVR cinemas in Chennai to monitor.
* 🎞️ **Movie Name Filter** – Get alerts only for your selected film.
* 🏟️ **Screen Type Filter** – Filter by IMAX, PXL, Big Pix, or Sathyam Main screen.
* ⏰ **Show Time Filter** – Monitor only shows within your preferred time window (e.g., 4–7 PM).
* 💬 **Subtitle Info in Alerts** – See if subtitles are available, right inside your notifications.
* 📅 **Date Picker** – Easily select a specific booking date.
* 📲 **Telegram Alerts** – Instant messages when bookings open.
* 💻 **Desktop Notifications** – Cross-platform pop-up alerts (Windows/macOS/Linux).
* 🔔 **Sound Alerts** – Audible notification when availability is detected.
* 🔁 **Auto-Retry** – Automatically retries if API fails.
* 🧾 **Activity Logs** – Real-time log display inside the app.
* 💡 **Keeps System Awake** – Prevents your system from sleeping.
* 🖥️ **Cross-Platform Support** – Works on **Windows, macOS, and Linux**.

---

## ⚙️ Prerequisites

Ensure the following are installed:

* ✅ **Python 3.x** (Download from [python.org](https://www.python.org/downloads/))

---

## 🤖 Telegram Bot Setup (Crucial!)

To receive alerts on Telegram:

### 1️⃣ Create Your Bot

1. Open Telegram, search for **@BotFather**.
2. Start a chat and type `/newbot`.
3. Follow prompts:

   * Choose a name: e.g., `PVR Monitor Bot`
   * Choose a unique username: e.g., `PVRMonitor_YourName_bot`
4. Copy the **BOT\_TOKEN** you receive.

---

### 2️⃣ Get Your Chat ID

1. Search Telegram for **@userinfobot**.
2. Type `/start`.
3. Copy your **Chat ID** (e.g., `1234567890`).

---

### 3️⃣ Update the Script

Open `main.py` and find:

```python
BOT_TOKEN = "YOUR_ACTUAL_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_ACTUAL_CHAT_ID_HERE"
```

Replace the placeholders with your actual bot token and chat ID.

✅ Example:

```python
BOT_TOKEN = "1234567890:ABCdefGHIJKLmnopQRSTuvWXyz"
CHAT_ID = "987654321"
```

---

## 🚀 Installation & Setup

### 1. Download the Script

Save the Python file as `main.py`.

### 2. Open Terminal / Command Prompt

* **Windows**: Open Command Prompt or PowerShell
* **macOS/Linux**: Open Terminal

### 3. Navigate to Script Directory

```bash
cd path/to/PVRMonitor
```

### 4. Create & Activate Virtual Environment (Recommended)

```bash
python -m venv venv
```

#### Activate:

* **Windows**:

  ```bash
  .\venv\Scripts\activate
  ```
* **macOS/Linux**:

  ```bash
  source venv/bin/activate
  ```

### 5. Install Dependencies

```bash
pip install requests ttkbootstrap win10toast
```

🔔 `win10toast` is for Windows notifications. It may not work on macOS/Linux (that’s okay).

---

## ▶️ How to Run

With the virtual environment activated:

```bash
python main.py
```

The GUI app will launch. You're ready to go! ✅

---

## 📝 Usage Instructions

* **🎥 Select Cinemas** – Choose one or more PVR cinemas from the checklist.
* **🎞️ Enter Movie Name** – (Optional) Filter for a specific film.
* **🏟️ Choose Screen Types** – Select preferred formats like IMAX, PXL, etc.
* **⏰ Set Show Time Range** – Monitor shows only in your preferred window.
* **📅 Pick Date** – Select "Today", "Tomorrow", or use the date picker.
* **▶️ Start Monitoring** – Begins checking availability.
* **🧪 Test Notification** – Verify sound, desktop, and Telegram alerts.
* **⏹️ Stop Monitoring** – Halts the process anytime.

All activity will be logged in the **Activity Logs** panel.

---

## ⚠️ Important Notes

* Keep the application **open and running** for continuous monitoring.
* **Internet connection** is required.
* **API changes** by PVR may affect the script.
* Telegram bots need to receive at least **one message from you** before they can reply.

---

## 🐛 Troubleshooting

| Issue                    | Solution                                                                       |
| ------------------------ | ------------------------------------------------------------------------------ |
| `ModuleNotFoundError`    | Run `pip install requests ttkbootstrap win10toast` in your virtual environment |
| No Telegram Alerts       | Check `BOT_TOKEN`, `CHAT_ID`, and make sure you started a chat with the bot    |
| No Desktop Notifications | Your OS might lack support or need permission                                  |
| App Not Responding       | Restart the app and check logs                                                 |

---

## 🧑‍💻 Developer

Built with ❤️ by **Suresh**

Contributions, feature suggestions, and feedback are welcome!

