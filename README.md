# 🎓 College Helper Bot

A modern, asynchronous Telegram bot designed for educational institutions. It streamlines communication between teachers and students, manages schedules, homework, and group notifications.

Built with **Python**, **Aiogram 3**, and **SQLAlchemy**.

## 🔥 Key Features

### 👨‍🏫 For Teachers
* **Group Management:** Create study groups and bind them to specific Telegram chats.
* **Smart Binding:** Use `/add_group <Name>` directly inside a group chat to instantly link it.
* **📰 News Broadcasting:** Send announcements (text + media) to a specific group or broadcast to the entire college.
* **📝 Homework:** Easily add homework assignments for specific groups.
* **🖼 Schedule:** Upload and update schedule images for each group.
* **🧑‍✈️ Duty Assignment:** Randomly select a "Duty Student" from the group members for daily tasks.

### 🎓 For Students
* **📚 Homework Tracker:** View the latest assignments for your group.
* **🗓 Schedule:** Instant access to the current schedule image.

## 🛠 Tech Stack

* **Language:** [Python 3.10+](https://www.python.org/)
* **Framework:** [Aiogram 3.x](https://docs.aiogram.dev/) (Asynchronous)
* **Database ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
* **Database:** SQLite (via `aiosqlite`)
* **Architecture:** FSM (Finite State Machine), Middlewares, Modular Handlers.

## 📂 Project Structure

```text
NewsCollegeBot/
├── app/
│   ├── handlers.py      # Main logic & command handlers
│   ├── models.py        # Database tables (SQLAlchemy)
│   ├── keyboards.py     # Inline & Reply keyboards
│   ├── middlewares.py   # Role-based access control
│   ├── states.py        # FSM States
│   └── config.py        # Environment configuration
├── main.py              # Entry point
├── .env                 # Secrets (Token)
└── requirements.txt     # Dependencies