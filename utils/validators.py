

def get_transaction_data():
    amount = float(input("Enter the amount: ").strip())
    category = input("Enter the category: ")
    desc = input("Enter a description (Optional): ")
    date = input("Enter a date (Leave empty for today): ")


    type = input("Enter the type of transaction (Deposit/Withdrawal): ").capitalize()
    while type not in ("Withdraw", "Deposit"):
        print("Invalid transfer type.")
        type = input("Please enter a valid type (Deposit/Withdrawal): ")


    return amount, category, desc, date, type

def get_category_data():
    name = input("Enter new category name: ")
    budget = input("Enter category budget: ").strip()
    if not budget:
        budget = 0
    else:
        budget = float(budget)
    
    return name, budget