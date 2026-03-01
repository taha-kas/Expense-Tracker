import mysql.connector
from src.expense_manager import Category
from src.user import User
import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    passwd=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

mycursor = db.cursor()


######################### Database Operations for Category #########################

def create_category(user_id, name, budget):
    query = """
        INSERT INTO category (user_id, category_name, budget)
        VALUES (%s, %s, %s)
    """
    try:
        mycursor.execute(query, (user_id, name, budget))
        db.commit()
        return Category(user_id, name, mycursor.lastrowid, budget), None
    except mysql.connector.Error as err:
        if err.errno == 1062:
            return None, "A category with this name already exists."
        else:
            return None, f"Database error: {err}"

def update_category_budget(category_id, new_budget):
    query = """
        UPDATE category
        SET budget = %s
        WHERE category_id = %s
    """
    try:
        mycursor.execute(query, (new_budget, category_id))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def update_category_name(category_id, new_name):
    query = """
        UPDATE Category
        SET category_name = %s
        WHERE category_id = %s
    """
    try:
        mycursor.execute(query, (new_name, category_id))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def soft_delete_category_db(category_id):
    query = """
        UPDATE category
        SET is_active = FALSE
        WHERE category_id = %s
    """
    try:
        mycursor.execute(query, (category_id,))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def restore_category_db(category_id):
    query = """
        UPDATE category
        SET is_active = TRUE
        WHERE category_id = %s
    """
    try:
        mycursor.execute(query, (category_id,))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def get_categories_by_user(user_id):
    query = """
        SELECT category_id, category_name, budget, is_active
        FROM category
        WHERE user_id = %s
    """
    mycursor.execute(query, (user_id,))
    categories = mycursor.fetchall()
    return [Category(user_id, name, cat_id, budget, is_active) for cat_id, name, budget, is_active in categories]

################################## End of Database Operations for Category #########################

################################## Database Operations for User ##################################

def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char.isalpha() for char in password):
        return "Password must contain at least one letter."
    if not any(char in set("!@#$%^&*()-_=+[]{|};:'\",.<>?/") for char in password):
        return "Password must contain at least one special character."
    return None

def create_user(username, email, password, birthday):
    email = email.lower().strip()
    username = username.strip()

    error = validate_password(password)
    if error:
        return None, error

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    query = """
        INSERT INTO user (username, email, psswd_hash, bday)
        VALUES (%s, %s, %s, %s)
    """
    try:
        mycursor.execute(query, (username, email, password_hash, birthday))
        db.commit()
        return User(mycursor.lastrowid, username, email, password_hash, birthday), None
    except mysql.connector.Error as err:
        if err.errno == 1062:
            return None, "Username or email already exists. Please choose a different one."
        else:
            return None, f"Database error: {err}"

def get_user_by_email(email):
    query = """
        SELECT user_id, username, email, psswd_hash, bday, is_active
        FROM user
        WHERE email = %s
    """
    mycursor.execute(query, (email,))
    result = mycursor.fetchone()
    if result:
        user_id, username, email, password_hash, birthday, is_active = result
        return User(user_id, username, email, password_hash, birthday, is_active)
    return None

def get_user_by_name(username):
    query = """
        SELECT user_id, username, email, psswd_hash, bday, is_active
        FROM user
        WHERE username = %s
    """
    mycursor.execute(query, (username,))
    result = mycursor.fetchone()
    if result:
        user_id, username, email, password_hash, birthday, is_active = result
        return User(user_id, username, email, password_hash, birthday, is_active)
    return None

def update_user_email(user_id, new_email):
    new_email = new_email.lower().strip()
    query = """
        UPDATE user
        SET email = %s
        WHERE user_id = %s
    """
    try:
        mycursor.execute(query, (new_email, user_id))
        db.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062:
            print("Email already exists.")
        else:
            print(f"Error: {err}")

def update_username(user_id, new_username):
    new_username = new_username.strip()
    query = """
        UPDATE user
        SET username = %s
        WHERE user_id = %s
    """
    try:
        mycursor.execute(query, (new_username, user_id))
        db.commit()
    except mysql.connector.Error as err:
        if err.errno == 1062:
            print("Username already exists.")
        else:
            print(f"Error: {err}")

def update_user_password(user_id, new_password):
    error = validate_password(new_password)
    if error:
        return error

    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    query = """
        UPDATE user
        SET psswd_hash = %s
        WHERE user_id = %s
    """
    try:
        mycursor.execute(query, (new_password_hash, user_id))
        db.commit()
        return None
    except mysql.connector.Error as err:
        return f"Database error: {err}"

def soft_delete_user(user_id):
    query = """
        UPDATE user
        SET is_active = FALSE
        WHERE user_id = %s
    """
    try:
        mycursor.execute(query, (user_id,))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

################################## End of Database Operations for User ##################################


################################## Database Operations for Transaction ##################################

from src.transaction import Transaction

def create_transaction(category_id, amount, transaction_type, date=None, description=""):
    query = """
        INSERT INTO `Transaction` (category_id, amount, type, transaction_date, description)
        VALUES (%s, %s, %s, %s, %s)
    """
    import datetime
    transaction_date = date if date else datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        mycursor.execute(query, (category_id, amount, transaction_type, transaction_date, description))
        db.commit()
        return Transaction(mycursor.lastrowid, category_id, amount, transaction_type, transaction_date, description), None
    except mysql.connector.Error as err:
        return None, f"Database error: {err}"

def get_transactions_by_category(category_id):
    query = """
        SELECT transaction_id, category_id, amount, type, transaction_date, description, created_at
        FROM `Transaction`
        WHERE category_id = %s
        ORDER BY transaction_date DESC
    """
    mycursor.execute(query, (category_id,))
    rows = mycursor.fetchall()
    return [
        Transaction(tid, cat_id, amount, ttype, date, desc or "", created_at)
        for tid, cat_id, amount, ttype, date, desc, created_at in rows
    ]

def update_transaction_amount(transaction_id, new_amount):
    if new_amount <= 0:
        return "Amount must be greater than zero."
    query = """
        UPDATE `Transaction`
        SET amount = %s
        WHERE transaction_id = %s
    """
    try:
        mycursor.execute(query, (new_amount, transaction_id))
        db.commit()
        return None
    except mysql.connector.Error as err:
        return f"Database error: {err}"

def update_transaction_description(transaction_id, new_description):
    query = """
        UPDATE `Transaction`
        SET description = %s
        WHERE transaction_id = %s
    """
    try:
        mycursor.execute(query, (new_description.strip(), transaction_id))
        db.commit()
        return None
    except mysql.connector.Error as err:
        return f"Database error: {err}"

def update_transaction_date(transaction_id, new_date):
    query = """
        UPDATE `Transaction`
        SET transaction_date = %s
        WHERE transaction_id = %s
    """
    try:
        mycursor.execute(query, (new_date, transaction_id))
        db.commit()
        return None
    except mysql.connector.Error as err:
        return f"Database error: {err}"

def delete_transaction(transaction_id):
    query = """
        DELETE FROM `Transaction`
        WHERE transaction_id = %s
    """
    try:
        mycursor.execute(query, (transaction_id,))
        db.commit()
        return None
    except mysql.connector.Error as err:
        return f"Database error: {err}"

################################## End of Database Operations for Transaction ##################################