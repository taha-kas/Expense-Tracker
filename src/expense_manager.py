import src.transaction
import json
import pandas as pd



# class Category:
#     def __init__(self, name):
#         self.name = name
#         self.budget = 0
#         self.ledger = []

#     def deposit(self, amount, description = ""):
#         self.budget += amount
#         transaction = {
#             'amount': amount,
#             'description': description
#         }
#         self.ledger.append(transaction)

#     def withdraw(self, amount, description = ""):
#         if self.check_funds(amount):
#             new_amount = -amount
#             self.deposit(new_amount, description)
#             return True
#         return False

#     def get_balance(self):
#         return self.budget

#     def transfer(self, amount, category):
#         if self.check_funds(amount):
#             self.withdraw(amount, f"Transfer to {category.name}")
#             category.deposit(amount, f"Transfer from {self.name}")
#             return True
#         return False

#     def __str__(self):
#         Total = 0
#         text = self.name.center(30, "*") + "\n"
         
#         for transaction in self.ledger:
#             amount = transaction.get("amount")
#             desc = transaction.get("description")

#             text += f"{desc[:23]:<23}{amount:>7.2f}\n"
#             Total += amount

#         text += f"Total: {Total:.2f}" 
#         return text
        
#     def check_funds(self, amount):
#         return amount <= self.get_balance()
    

class Category:

    def __init__(self, name, budget, transactions = []):
        self.name = name
        self.budget = budget
        self.transactions = transactions

    @property
    def budget(self):
        return self._budget

    @property
    def formatted_budget(self):
        return f"${self._budget:.2f}"
    
    @budget.setter
    def budget(self, new_budget):
        if new_budget >= 0:
            self._budget = new_budget
        else:
            print("Budget must be greater than or equal to zero.")
        

    def add_transaction(self, transaction):
        if transaction.type == "Withdrawal":
            # Check if withdraw amount is less than category budget:
            if abs(transaction._amount) <= self._budget:
                self.transactions.append(transaction.to_dict())
                self._budget += transaction._amount
            else:
                print(f"Transaction amount of {transaction.amount} exceeds budget ({self.budget}).\nTransaction has been cancelled...")
                # while abs(transaction.amount) > self.budget:
                #     transaction.amount = float(input("Please enter a valid amount: ").strip())
         
        elif transaction.type == "Deposit":
            self.transactions.append(transaction.to_dict())
            self._budget += transaction._amount

        else:
            print("Invalid Transaction Type.\nTransaction has been cancelled...")

    def to_json(self):
        with open("C:\\Users\\Taha\\OneDrive\\Bureau\\Expense Tracker\\data\\transactions.json", "w") as file:
            json.dump(self.transactions, file, indent = 4)
            print("transactions.json has been updated successfully!")

    def to_csv(self):
        df = pd.DataFrame(self.transactions)
        df.to_csv("C:\\Users\\Taha\\OneDrive\\Bureau\\Expense Tracker\\data\\transactions.csv", index=False)
        print("transactions.csv has been updated successfully!")