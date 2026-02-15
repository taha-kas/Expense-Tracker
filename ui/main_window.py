# import sys
# from PyQt5.QtWidgets import QMainWindow, QLabel
# from PyQt5.QtGui import QIcon, QFont

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Expense Manager")
#         self.setGeometry(700, 300, 500, 500)

#         label = QLabel("Hello", self)
#         label.setGeometry(250, 100, 250, 250)
#         label.setFont(QFont("Arial", 12))


from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDoubleSpinBox,
    QDateEdit, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QDate

from src.expense_manager import Category

from src.transaction import Transaction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.categories = {
            "Food": Category("Food", 500),
            "Transport": Category("Transport", 300),
            "Rent": Category("Rent", 1000),
            "Entertainment": Category("Entertainment", 200)
        }

        self.setWindowTitle("Expense Manager")
        self.setMinimumSize(800, 600)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # --------------------------
        # 1️⃣ FORM SECTION
        # --------------------------

        form_layout = QFormLayout()

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(1000000)
        self.amount_input.setPrefix("$ ")

        self.category_input = QComboBox()
        self.category_input.addItems(["Food", "Transport", "Rent", "Entertainment"])

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.description_input = QLineEdit()

        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)

        form_layout.addRow("Amount:", self.amount_input)
        form_layout.addRow("Category:", self.category_input)
        form_layout.addRow("Date:", self.date_input)
        form_layout.addRow("Description:", self.description_input)
        form_layout.addRow(self.add_button)

        main_layout.addLayout(form_layout)

        # --------------------------
        # 2️⃣ TABLE SECTION
        # --------------------------

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Date", "Category", "Amount", "Description"]
        )

        main_layout.addWidget(self.table)

        # --------------------------
        # 3️⃣ SUMMARY SECTION
        # --------------------------

        summary_layout = QHBoxLayout()

        self.total_label = QLabel("Total Spent: $0.00")

        summary_layout.addWidget(self.total_label)

        main_layout.addLayout(summary_layout)

    # --------------------------
    # LOGIC CONNECTION METHODS
    # --------------------------

    def add_transaction(self):
        amount = self.amount_input.value()
        category = self.category_input.currentText()
        date = self.date_input.date().toString("yyyy-MM-dd")
        description = self.description_input.text()

        t = Transaction(amount, category, "Withdrawal", date, description)
        selected_category_name = self.category_input.currentText()
        self.category_object = self.categories[selected_category_name]

        self.category_object.add_transaction(t)
        print(self.category_object.name) #Remove this later

        self.refresh_table()
        self.update_summary()
        self.clear_inputs()

    def refresh_table(self):
        self.table.setRowCount(0)

        for transaction in self.category_object.transactions:

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(transaction["date"]))
            self.table.setItem(row_position, 1, QTableWidgetItem(transaction["category"]))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{transaction['amount']:.2f}"))
            self.table.setItem(row_position, 3, QTableWidgetItem(transaction["description"]))


    def update_summary(self):
        total = self.category_object._budget
        self.total_label.setText(f"Current budget ({self.category_object.name}): ${total:.2f}")

    def clear_inputs(self):
        self.amount_input.setValue(0)
        self.description_input.clear()
