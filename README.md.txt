# Smart Personal Expense Tracker

## Overview
Smart Personal Expense Tracker is a 100% Python-based application that helps users record their daily expenses, add received money, set weekly or monthly spending goals, and view their remaining balance. The goal of the project is to build a simple and beginner-friendly finance tool that runs locally without any complex sign-up or password system.

The project is implemented using Python and Streamlit for the interface, and SQLite for persistent storage of transactions and goals.

---

## Features
- Simple username input (no password or email)
- Add expenses with amount, category, date, and notes
- Add received money (income) to increase balance
- Automatic balance update after each transaction
- Set **monthly** and **weekly** spending goals
- View:
  - Total expenses
  - Total income
  - Current balance
  - Goal amount, amount spent, and remaining amount
- Warning messages when spending is close to or exceeds the set limit
- Transaction history table with filters by date and type

---

## Tech Stack
- **Language:** Python
- **Frontend / UI:** Streamlit (Python-based web UI)
- **Database:** SQLite (via `sqlite3` library)
- **Libraries:**
  - `streamlit`
  - `pandas` (for display convenience, optional)
  - `sqlite3` (standard library)
  - `datetime` (standard library)

---

## Project Structure
```text
smart-expense-tracker/
│
├─ app.py          # Main Streamlit application
├─ database.py     # Database initialization and helper functions
├─ requirements.txt
├─ README.md
├─ statement.md
└─ expenses.db     # SQLite database (auto-created)
