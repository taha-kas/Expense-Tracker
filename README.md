# Expense Manager

A desktop expense management application built with Python and Flet, backed by a MySQL database. Users can sign up, log in, manage spending categories, and track transactions — with full budget tracking across all operations.

---

## Features

### Authentication
- User registration with password validation (minimum 8 characters, must include a letter, number, and special character)
- Secure login with bcrypt password hashing
- Account deactivation support (soft delete)

### Category Management
- Create spending categories with an optional budget
- Edit category name and budget inline
- Soft delete (deactivate) and restore categories
- Toggle visibility of inactive categories

### Transaction Tracking
- Log deposits and withdrawals per category
- Optional date (defaults to today) and description
- Edit transaction amount, date, and description
- Delete transactions
- Budget automatically updates on every create, edit, and delete operation
- Summary bar showing total deposits, total withdrawals, and current balance per category

---

## Project Structure

```
expense_manager/
│
├── db/
│   └── database.py               # All MySQL operations (users, categories, transactions)
│
├── src/
│   ├── expense_manager.py        # Category class
│   ├── transaction.py            # Transaction class
│   └── user.py                   # User class
│
├── ui/
│   ├── login_page.py             # Login screen
│   ├── signup_page.py            # Signup screen
│   ├── dashboard_view.py         # Category overview (main dashboard)
│   └── category_detail_view.py   # Transaction management per category
│
├── main.py                       # App entry point and route management
├── requirements.txt              # Python dependencies
├── .env                          # Local credentials (never pushed to GitHub)
├── .env.example                  # Template for environment variables
└── .gitignore
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| UI Framework | Flet 0.80.5 |
| Database | MySQL |
| DB Driver | mysql-connector-python |
| Password Hashing | bcrypt |
| Environment Variables | python-dotenv |
| Data Analysis (planned) | pandas |
| AI Chatbot (planned) | TBD |

---

## Database Schema

### `user`
| Column | Type | Notes |
|---|---|---|
| user_id | INT | Primary key, auto increment |
| username | VARCHAR | Unique |
| email | VARCHAR | Unique, lowercase |
| psswd_hash | VARCHAR | bcrypt hash |
| bday | DATE | |
| is_active | BOOLEAN | Soft delete flag |

### `category`
| Column | Type | Notes |
|---|---|---|
| category_id | INT | Primary key, auto increment |
| user_id | INT | Foreign key → user |
| category_name | VARCHAR | Unique per user |
| budget | DECIMAL(10,2) | |
| is_active | BOOLEAN | Soft delete flag |

### `Transaction`
| Column | Type | Notes |
|---|---|---|
| transaction_id | INT | Primary key, auto increment |
| category_id | INT | Foreign key → category |
| amount | DECIMAL(10,2) | Always positive |
| type | ENUM | `Deposit` or `Withdrawal` |
| transaction_date | DATE | |
| description | VARCHAR(255) | Optional |
| created_at | TIMESTAMP | Auto set to now() |

---

## Setup

### Prerequisites
- Python 3.10+
- MySQL server running locally
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/expense-manager.git
cd expense-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables — create a `.env` file in the project root using `.env.example` as a template:
```
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=expense_manager
```

4. Set up the database — create a MySQL database named `expense_manager` and run the schema SQL scripts to create the `user`, `category`, and `Transaction` tables.

5. Run the app:
```bash
python main.py
```

---

## Planned Features

- Data analysis with pandas (spending breakdowns, trends)
- Chart visualizations per category and time period
- AI chatbot integration for querying personal finance data in natural language (e.g. *"What percentage of my budget did I spend on food last month?"*)

---

## Notes

- Transactions store amounts as positive values. The `type` field (`Deposit` / `Withdrawal`) determines the sign. A `signed_amount` property is available on the `Transaction` class for calculations.
- Categories use soft delete — deactivated categories and their transactions are preserved in the database and can be restored at any time.
- Transactions use hard delete — once deleted, they are permanently removed from the database.
- Never commit your `.env` file — it contains your local database credentials and is excluded via `.gitignore`.
