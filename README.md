# Xshouyan

> **Privacy-first hand gesture control for Linux & Hyprland.**

#NOTE: Still In development

Xshouyan is an offline background daemon that uses hand gestures to control the Linux desktop. It separates gesture recognition, action mapping, and system execution into independent components.

[![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://www.kernel.org/)
[![Hyprland](https://img.shields.io/badge/Hyprland-58E1FF?style=flat-square&logo=hyprland&logoColor=black)](https://hyprland.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Offline](https://img.shields.io/badge/Offline-Privacy--First-2ea44f?style=flat-square)](#)

---

## Architecture

```text
                           XSHOUYAN
                              │
                              ▼
                    ┌──────────────────┐
                    │     main.py      │
                    │   Orchestrator   │
                    │                  │
                    │ Camera Loop      │
                    │ Debouncing       │
                    │ State Management │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌──────────────────┐          ┌──────────────────┐
     │   gesture.py     │          │    action.py     │
     │                  │          │                  │
     │    ML Engine     │          │   OS Handler     │
     └────────┬─────────┘          └────────┬─────────┘
              │                             │
              ▼                             ▼
     ┌──────────────────┐          ┌──────────────────┐
     │     Webcam       │          │    config.json   │
     │   /dev/video0    │          │   User Mappings  │
     └──────────────────┘          └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  Hyprland / Linux│
                                   │    IPC / Shell   │
                                   └──────────────────┘
````

## Data Flow

```text
Webcam
  │
  ▼
gesture.py
  │
  │ detected gesture
  ▼
main.py
  │
  │ gesture name
  ▼
action.py
  │
  │ lookup mapping
  ▼
config.json
  │
  │ IPC / Bash command
  ▼
Hyprland / Linux
```

---


# `config.json` — User Mappings

Defines what each gesture should do.

```json
{
  "thumb_up": "hyprctl dispatch workspace +1",
  "fist": "hyprctl dispatch workspace -1",
  "peace": "playerctl play-pause"
}
```

This keeps gesture recognition independent from the actions being performed.

---

## Project Structure

```text
xshouyan/
├── main.py          # Application orchestrator
├── gesture.py       # Gesture recognition / ML engine
├── action.py        # OS action handler
├── config.json      # User-defined gesture mappings
└── README.md
```

---

## Design

Xshouyan follows a simple separation of concerns:

```text
┌──────────────────┐
│ Gesture Detection│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Gesture Name   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Action Mapping  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   OS Execution   │
└──────────────────┘
```

The **ML layer detects what the user is doing**.

The **action layer decides what that gesture means**.

The **OS layer executes the result**.

This s# Xshouyan

> **Privacy-first hand gesture control for Linux & Hyprland.**

Xshouyan is an offline background daemon that uses hand gestures to control the Linux desktop. It separates gesture recognition, action mapping, and system execution into independent components.

[![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)](https://www.kernel.org/)
[![Hyprland](https://img.shields.io/badge/Hyprland-58E1FF?style=flat-square&logo=hyprland&logoColor=black)](https://hyprland.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Offline](https://img.shields.io/badge/Offline-Privacy--First-2ea44f?style=flat-square)](#)

---

## Architecture

```text
                           XSHOUYAN
                              │
                              ▼
                    ┌──────────────────┐
                    │     main.py      │
                    │   Orchestrator   │
                    │                  │
                    │ Camera Loop      │
                    │ Debouncing       │
                    │ State Management │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌──────────────────┐          ┌──────────────────┐
     │   gesture.py     │          │    action.py     │
     │                  │          │                  │
     │    ML Engine     │          │   OS Handler     │
     └────────┬─────────┘          └────────┬─────────┘
              │                             │
              ▼                             ▼
     ┌──────────────────┐          ┌──────────────────┐
     │     Webcam       │          │    config.json   │
     │   /dev/video0    │          │   User Mappings  │
     └──────────────────┘          └────────┬─────────┘
                                            │
                                            ▼
                                   ┌──────────────────┐
                                   │  Hyprland / Linux│
                                   │    IPC / Shell   │
                                   └──────────────────┘
````

## Data Flow

```text
Webcam
  │
  ▼
gesture.py
  │
  │ detected gesture
  ▼
main.py
  │
  │ gesture name
  ▼
action.py
  │
  │ lookup mapping
  ▼
config.json
  │
  │ IPC / Bash command
  ▼
Hyprland / Linux
```

---

## `config.json` — User Mappings

Defines what each gesture should do.

```json
{
  "thumb_up": "hyprctl dispatch workspace +1",
  "fist": "hyprctl dispatch workspace -1",
  "peace": "playerctl play-pause"
}
```

This keeps gesture recognition independent from the actions being performed.

---

## Project Structure

```text
xshouyan/
├── main.py          # Application orchestrator
├── gesture.py       # Gesture recognition / ML engine
├── action.py        # OS action handler
├── config.json      # User-defined gesture mappings
└── README.md
```

---

## Design

Xshouyan follows a simple separation of concerns:

```text
┌──────────────────┐
│ Gesture Detection│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Gesture Name   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Action Mapping  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   OS Execution   │
└──────────────────┘
```

The **ML layer detects what the user is doing**.

The **action layer decides what that gesture means**.

The **OS layer executes the result**.

This separation makes each part easier to modify, test, and extend.

```
eparation makes each part easier to modify, test, and extend.

```
