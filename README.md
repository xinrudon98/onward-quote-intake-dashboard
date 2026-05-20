# ONWARD Quote Intake Dashboard

An internal homeowners quote intake and workflow management platform built with Outlook automation, SQL Server, and FastAPI.

---

# Architecture

<p align="center">
  <img src="https://raw.githubusercontent.com/xinrudon98/onward-quote-intake-dashboard/main/assets/architecture.png" width="950">
</p>

---

# Overview

This platform streamlines the homeowners quote intake workflow by automatically parsing Outlook submissions into SQL Server and providing an internal dashboard for inquiry review, status tracking, and operational workflow management.

The system is composed of two major components:

## 1. Intake Automation

Automatically reads incoming homeowners quote submissions from Outlook folders and inserts structured records into SQL Server.

### Workflow

```text
Outlook Email
    ↓
Python Intake Parser
    ↓
SQL Server
```

---

## 2. Workflow Dashboard

A FastAPI-powered dashboard for internal operations teams to:

- Review quote inquiries
- Filter and search submissions
- Track workflow statuses
- Add operational notes
- Monitor intake metrics

### Workflow

```text
SQL Server
    ↓
FastAPI Backend
    ↓
HTML / JavaScript Frontend
    ↓
Internal Workflow Dashboard
```

---

# Features

## Outlook Intake Automation

- Outlook COM integration
- Structured email parsing
- Duplicate prevention
- SQL Server ingestion
- Automated intake workflow

---

## Internal Dashboard

- Inquiry management
- Workflow status tracking
- Search and filtering
- Notes management
- Auto-refresh dashboard
- Workflow metrics
- EXE deployment via PyInstaller

---

# Status Workflow

| Status | Description |
|---|---|
| New | Newly received inquiry |
| In Review | Under active review |
| Responded | Customer has been contacted |
| Closed | Workflow completed |
| Invalid | Invalid submission |
| Duplicate | Duplicate inquiry |

---

# Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Database | SQL Server |
| Intake Automation | Outlook COM + Python |
| Frontend | HTML / CSS / JavaScript |
| Connectivity | pyodbc |
| Packaging | PyInstaller |

---

# Local Development

## Dashboard

```bash
cd dashboard
python main.py
```

The dashboard launches automatically in the browser.

---

## Build EXE

```bash
pyinstaller --onefile --noconsole --name OnwardQuote main.py
```

Output:

```text
dist/OnwardQuote.exe
```

---

# Project Structure

```text
onward-quote-intake-dashboard
│
├── intake/
│   └── onward_quote_intake.py
│
├── dashboard/
│   └── main.py
│
├── assets/
│   └── architecture.png
│
├── requirements.txt
└── README.md
```

---

# Notes

This project is designed for Windows-based internal operational environments with:

- Outlook Desktop
- SQL Server access
- ODBC Driver 17
- Windows authentication

---
