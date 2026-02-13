import datetime
import json
import csv

class Transaction:

    def __init__(self, amount, category, type, date = None, description = ""):
        self._amount = amount
        self.category = category.capitalize()
        self.description = description 
        self.date = date if date else datetime.datetime.now()
        self.type = type


        self.date = self.date.strftime("%Y-%m-%d")

    @property
    def amount(self):
        return  f"${self._amount:.2f}"
    
    @amount.setter
    def amount(self, new_amount):
        self._amount = new_amount

    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "type": self.type, 
            "description": self.description
        }