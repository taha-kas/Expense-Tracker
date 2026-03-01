import pandas as pd
import mysql.connector
import db.database as db
from src.transaction import Transaction

class Category:
    def __init__(self, user_id, name, category_id, budget=0, is_active=True):
        self.user_id = user_id
        self._name = name.capitalize()
        self._budget = float(budget)
        self.category_id = category_id 
        self.is_active = is_active
    @property
    def budget(self):
        return self._budget
    
    @budget.setter
    def budget(self, value):
        if value < 0:
            raise ValueError("Budget cannot be negative.")
        self._budget = value
        db.update_category_budget(self.category_id, self._budget)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Category name cannot be empty.")
        self._name = value.capitalize()    
        db.update_category_name(self.category_id, self._name)

    # def save_to_db(self, cursor, db):
    #     if self.category_id is None:
    #         query = """
    #             INSERT INTO Category (user_id, category_name, budget)
    #             VALUES (%s, %s, %s)
    #         """
    #         cursor.execute(query, (self.user_id, self.name, self.budget))
    #         db.commit()
    #         self.category_id = cursor.lastrowid
    #     else:
    #         query = """
    #             UPDATE Category
    #             SET budget = %s
    #             WHERE category_id = %s
    #         """
    #         cursor.execute(query, (self.budget, self.category_id))
    #         db.commit()

    def soft_delete_category(self):
        self.is_active = False
        db.soft_delete_category_db(self.category_id)

    def restore_category(self):
        self.is_active = True
        db.restore_category_db(self.category_id)

    def update_budget(self, transaction_amount):
        self._budget += transaction_amount

    def __str__(self):
        return f"Category: {self.name}, Budget: {self._budget}"

    def __lt__(self, other):
        return self._budget < other._budget
    
    def __gt__(self, other):
        return self._budget > other._budget