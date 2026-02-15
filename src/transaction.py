import datetime
import json
import csv

class Transaction:

    def __init__(self, amount, category, type, date = None, description = ""):
        self._amount = amount if type == "Deposit" else -amount
        self.category = category.capitalize()
        self.description = description 
        # self.date = date if date else datetime.datetime.now()
        self.type = type

        if date is None or date == "":
            self.date = datetime.datetime.now()
        else: 
            self.date = datetime.datetime.strptime(date, "%Y-%m-%d")

        self.date = self.date.strftime("%Y-%m-%d")

    @property
    def amount(self):
        return  self._amount
    
    @property
    def formatted_amount(self):
        return f"${self.amount:.2f}"
    
    @amount.setter
    def amount(self, new_amount):
        self._amount = new_amount

    def to_dict(self):
        return {
            "amount": self._amount,
            "category": self.category,
            "date": self.date,
            "type": self.type, 
            "description": self.description
        }