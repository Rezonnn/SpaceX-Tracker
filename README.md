# 🚀 SpaceX Launch Tracker (CLI)

A **Python** command-line app that uses the **SpaceX public REST API** to show **live launch data**.

- **Language:** Python 3
- **Type:** Interactive **terminal / CLI** application
- **Focus:** API consumption, data parsing, and rich terminal UI

---

## ✨ Features

- Fetches **live launch data** from `https://api.spacexdata.com/v5`
- View **upcoming launches** (soonest first)
- View **recent launches** with mission, date, rocket, and success status
- **Search** past launches by mission name
- Pretty **tables** and **panels** using the `rich` library
- Handles API and network errors gracefully

---

## 🧱 Tech Stack

- **Python 3.9+**
- [`requests`](https://pypi.org/project/requests/) for HTTP
- [`rich`](https://pypi.org/project/rich/) for colorful terminal output

---

## 📦 Installation

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the app with:

```bash
python main.py
```

You will see a menu like:

```text
SpaceX Launch Tracker
Live data from api.spacexdata.com

1. View upcoming launches
2. View recent launches
3. Search recent launches by mission name
4. Refresh all data
0. Exit
```

Use the number keys to select an option.  
Once a table of launches appears, you can:

- Enter a **row number** to see full details of that mission
- Press **Enter** to go back to the menu

---

## 🌐 API Info

This uses the official SpaceX public API:

- Base URL: `https://api.spacexdata.com/v5`
- Endpoints used:
  - `/launches/upcoming`
  - `/launches/past`
  - `/rockets`
  - `/launchpads`

No API key is required.

---

Enjoy exploring space data from your terminal! ✨
