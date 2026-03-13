import db.database as db


class Category:
    def __init__(self, user_id, name, category_id, category_type, budget=None, is_active=True):
        self.user_id = user_id
        self._name = name.capitalize()
        self.category_id = category_id
        self.category_type = category_type  # 'income' or 'spending'
        self._budget = float(budget) if budget is not None else None
        self.is_active = is_active

    @property
    def budget(self):
        return self._budget

    @budget.setter
    def budget(self, value):
        if value is not None and value <= 0:
            raise ValueError("Budget must be greater than zero.")
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

    def soft_delete_category(self):
        self.is_active = False
        db.soft_delete_category_db(self.category_id)

    def restore_category(self):
        self.is_active = True
        db.restore_category_db(self.category_id)

    def is_income(self):
        return self.category_type == 'income'

    def is_spending(self):
        return self.category_type == 'spending'

    def __str__(self):
        budget_str = f"${self._budget:.2f}" if self._budget is not None else "N/A"
        return f"Category: {self.name} ({self.category_type}), Budget: {budget_str}"

    def __lt__(self, other):
        return (self._budget or 0) < (other._budget or 0)

    def __gt__(self, other):
        return (self._budget or 0) > (other._budget or 0)