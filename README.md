# Xshouyan

> **Privacy-first hand gesture control for Linux & Hyprland.**

> ⚠️ **Development Status: Early Alpha**
> *Xshouyan is currently in active development. While the feature set is still growing, the core application is designed to be entirely offline and privacy-respecting. It processes everything locally on your machine, making it completely safe and secure to test.*

Xshouyan is an offline background daemon that uses hand gestures and speech-to-text dictation to control the Linux desktop. It separates gesture recognition, audio processing, action mapping, and system execution into independent components, ensuring a fast, modular, and privacy-first user experience.

## 🚀 Getting Started

### Prerequisites

Ensure you have **Python 3** and **Git** installed on your system.

### Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/mahoraga777/XShouyin.git
   cd XShouyin
   ```

2. **Create and activate a virtual environment (Recommended):**
   Keeps the project dependencies isolated from your system.

   ```bash
   python3 -m venv venv
   ```

   * **macOS/Linux (Bash/Zsh):** `source venv/bin/activate`
   * **macOS/Linux (Fish):** `source venv/bin/activate.fish`

3. **Install Dependencies:**
   With your virtual environment active, install the required packages using the requirements file:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Run the Project:**

   ```bash
   python main.py
   ```

## ⚙️ Configuration

**`config.json` — User Mappings**

This file defines what each detected gesture should do. By keeping this separate, recognition remains independent from the OS actions being performed.

```json
{
  "thumb_up": "hyprctl dispatch workspace +1",
  "fist": "hyprctl dispatch workspace -1",
  "peace": "playerctl play-pause"
}
```

## 🏗️ Architecture

Xshouyan follows a strict separation of concerns, making each part easier to modify, test, and extend.

* The **ML layers** (Vision & Audio) detect what the user is doing or saying.
* The **Action layer** routes those inputs (either updating the mouse or running commands).
* The **OS layer** executes the resulting command.

### Component Map

```text
                                XSHOUYAN
                                   │
                                   ▼
                         ┌──────────────────┐
                         │     main.py      │
                         │   Orchestrator   │
                         │                  │
                         │ AV Sync & Loop   │
                         │ State Management │
                         └────────┬─────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │    gesture.py    │   │   dictation.py   │   │    action.py     │
  │                  │   │                  │   │                  │
  │ Vision ML Engine │   │ Speech-to-Text   │   │ Command Routing  │
  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
           │                      │                      │
           ▼                      ▼                      │
  ┌──────────────────┐   ┌──────────────────┐            ▼
  │      Webcam      │   │    Microphone    │   ┌──────────────────┐
  │   /dev/video0    │   │   Audio Stream   │   │     mouse.py     │
  └──────────────────┘   └──────────────────┘   │  Cursor Control  │
                                                └────────┬─────────┘
                                                         │
                                                ┌────────▼─────────┐
                                                │   config.json    │
                                                │  User Mappings   │
                                                └────────┬─────────┘
                                                         │
                                                         ▼
                                                ┌──────────────────┐
                                                │  Hyprland/Linux  │
                                                │   IPC / Shell    │
                                                └──────────────────┘
```

### Data Flow

```text
Webcam / Microphone
  │
  ▼
gesture.py / dictation.py  ──────> (detects gesture / parses audio)
  │
  ▼
main.py                    ──────> (reads state & syncs events)
  │
  ▼
action.py                  ──────> (routes logic)
  │
  ├──► mouse.py            ──────> (moves cursor / clicks)
  │
  └──► config.json         ──────> (returns IPC / Bash command)
         │
         ▼
       Hyprland / Linux
```

## 📁 Project Structure

```text
XShouyin/
├── main.py          # Application orchestrator handling the main event loop
├── gesture.py       # Vision ML engine / Hand gesture detection
├── dictation.py     # Speech-to-text / Audio processing (Triggered by gestures)
├── action.py        # OS action handler and routing
├── mouse.py         # Precision mouse movement and coordinate mapping
├── config.json      # User-defined gesture mappings
├── requirements.txt # Project dependencies list
├── .gitignore       # Git ignore rules
├── LICENSE          # BSD 3-Clause License
└── README.md        # Project documentation
```
