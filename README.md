# Expense Manager

A desktop expense tracking application built with Python, Flet, and MySQL. The app allows users to manage their personal finances by tracking income and spending across custom categories, with monthly budgeting and analytics.

## Features

- **Authentication** — secure user registration and login with bcrypt password hashing
- **Two-type category system** — income categories (deposits, no budget) and spending categories (withdrawals, mandatory budget)
- **Transaction management** — log, edit, and delete transactions
- **Month filter** — filter transaction history by month within each category
- **Dashboard** — side-by-side income/spending overview with a monthly usage progress bar
- **Budget tracking** — per-category budget vs. actual spending with color-coded indicators
- **Analytics** — summary cards, top spending categories, and charts rendered with Matplotlib and Seaborn (income vs. spending by month, spending by category)
- **Profile management** — update username, email, birthday, and password

## Project Structure

```
Expense Tracker/
│
├── analytics/
│   ├── __init__.py
│   ├── analysis.py
│   └── charts.py
│   
├── main.py
├── requirements.txt
├── db/
│   ├── __init__.py
│   └── database.py
├── src/
│   ├── __init__.py
│   ├── expense_manager.py
│   ├── transaction.py
│   └── user.py
├── ui/
│   ├── __init__.py
│   ├── login_page.py
│   ├── signup_page.py
│   ├── dashboard_view.py
│   ├── category_detail_view.py
│   ├── profile_view.py
│   └── analytics_view.py
├── .env.example
```

## Prerequisites

- Python 3.10+
- MySQL Server

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/TahaMaftahElKassimy/expense-manager.git
   cd expense-manager
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file at the root of the project and copy the content of the `.env.example` file into it after having replaced the fields with your MySQL server information.

4. Set up the database. Run the following in your MySQL client:
   ```sql
   CREATE DATABASE expense_manager;
   ```
   Then run the application once — the tables are created automatically on first launch.
   ```

## Running the App

```bash
python main.py
```

The window launches maximized. If it does not, click the maximize button in the top-right corner.

## Tech Stack

| Layer | Technology |
|---|---|
| UI framework | Flet 0.80.5 |
| Database | MySQL + mysql-connector-python |
| Data analysis | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Authentication | bcrypt |
| Config | python-dotenv |