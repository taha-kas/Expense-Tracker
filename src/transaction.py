import datetime


class Transaction:
    def __init__(self, transaction_id, category_id, amount, transaction_type, date=None, description="", created_at=None):
        self.transaction_id = transaction_id
        self.category_id = category_id
        self._amount = float(amount)
        self._type = transaction_type
        self._description = description.strip() if description else ""
        self.created_at = created_at

        if date is None or date == "":
            self.transaction_date = datetime.datetime.now().date()
        elif isinstance(date, datetime.date):
            self.transaction_date = date
        else:
            self.transaction_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        if value <= 0:
            raise ValueError("Amount must be greater than zero.")
        self._amount = float(value)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if value not in ("Deposit", "Withdrawal"):
            raise ValueError("Transaction type must be 'Deposit' or 'Withdrawal'.")
        self._type = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value.strip() if value else ""

    @property
    def signed_amount(self):
        """Returns the amount with sign applied: positive for deposits, negative for withdrawals."""
        return self._amount if self._type == "Deposit" else -self._amount

    def __str__(self):
        sign = "+" if self._type == "Deposit" else "-"
        desc = f" — {self._description}" if self._description else ""
        return f"[{self.transaction_date}] {self._type}: {sign}${self._amount:.2f}{desc}"

    def __lt__(self, other):
        return self.transaction_date < other.transaction_date

    def __gt__(self, other):
        return self.transaction_date > other.transaction_date