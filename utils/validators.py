

def get_transaction_data(cats):
    amount = float(input("Enter the amount: ").strip())
    category = input("Enter the category: ").capitalize()
    while category not in cats:
        print("The category name that you selected isn't valid. Please select one of the following or create a new category: ")
        for cat in cats.keys():
            print(cat, end = " - ")
    desc = input("Enter a description (Optional): ").strip()
    date = input("Enter a date (\"YYYY-MM-DD\" or leave empty for today): ").strip()


    type = input("Enter the type of transaction (Deposit/Withdrawal): ").strip().capitalize()
    while type not in ("Withdrawal", "Deposit"):
        print("Invalid transfer type.")
        type = input("Please enter a valid type (Deposit/Withdrawal): ").strip().capitalize()


    return amount, category, type, date, desc  

def get_category_data():
    name = input("Enter new category name: ").strip()
    budget = input("Enter category budget: ").strip()
    if not budget:
        budget = 0
    else:
        budget = float(budget)
    
    return name, budget