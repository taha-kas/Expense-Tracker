import flet as ft
import json
import os
from datetime import datetime

from src.expense_manager import Category
from src.transaction import Transaction


DATA_FILE = "data/transactions.json"


def main_ui(page: ft.Page):
    page.title = "Expense Tracker"
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # -------------------------
    # DATA
    # -------------------------

    categories = {
        "Food": Category("Food", 500),
        "Transport": Category("Transport", 300),
        "Rent": Category("Rent", 1000),
        "Entertainment": Category("Entertainment", 200),
    }

    selected_category = categories["Food"]

    # -------------------------
    # PERSISTENCE
    # -------------------------

    def save_data():
        all_transactions = []
        for cat in categories.values():
            all_transactions.extend(cat.transactions)

        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(all_transactions, f, indent=4)

    def load_data():
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        for item in data:
            cat = categories.get(item["category"])
            if cat:
                # Convert amount to float safely
                amount = float(item["amount"])

                item["amount"] = amount
                cat.transactions.append(item)
                cat.budget += amount


    load_data()

    # -------------------------
    # UI CONTROLS
    # -------------------------

    category_dropdown = ft.Dropdown(
        label="Category",
        value="Food",
        options=[ft.dropdown.Option(c) for c in categories.keys()],
        width=200,
    )

    amount_field = ft.TextField(label="Amount", width=150)

    description_field = ft.TextField(label="Description", width=300)

    date_picker = ft.DatePicker()
    page.overlay.append(date_picker)

    date_field = ft.TextField(
        label="Date",
        width=150,
        read_only=True,
    )

    def open_date_picker(e):
        date_picker.open = True
        page.update()

    date_field.on_click = open_date_picker



    def on_date_change(e):
        if date_picker.value:
            selected_date = date_picker.value

            corrected_date = datetime(selected_date.year, selected_date.month, selected_date.day)

            date_field.value = corrected_date.strftime("%Y-%m-%d")
            page.update()

    date_picker.on_change = on_date_change

    transaction_type = ft.RadioGroup(
        content=ft.Row(
            [
                ft.Radio(value="Deposit", label="Deposit"),
                ft.Radio(value="Withdrawal", label="Withdrawal"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        value="Withdrawal",
    )

    budget_text = ft.Text(size=18, weight=ft.FontWeight.BOLD)

    progress_bar = ft.ProgressBar(width=400)

    month_filter = ft.Dropdown(
        label="Filter by Month",
        width=200,
        options=[
            ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 13)
        ],
    )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Date")),
            ft.DataColumn(ft.Text("Category")),
            ft.DataColumn(ft.Text("Amount")),
            ft.DataColumn(ft.Text("Description")),
            ft.DataColumn(ft.Text("Delete")),
        ],
        rows=[],
    )


    # -------------------------
    # FUNCTIONS
    # -------------------------

    def refresh_ui():
        current_category = categories[category_dropdown.value]

        budget_text.value = f"Remaining budget: ${current_category.budget:.2f}"

        initial_budget = {
            "Food": 500,
            "Transport": 300,
            "Rent": 1000,
            "Entertainment": 200,
        }[current_category.name]

        progress = current_category.budget / initial_budget
        progress_bar.value = max(0, min(progress, 1))

        table.rows.clear()

        for index, t in enumerate(current_category.transactions):

            if month_filter.value:
                transaction_month = datetime.strptime(t["date"], "%Y-%m-%d").strftime("%m")
                if transaction_month != month_filter.value:
                    continue

            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(t["date"])),
                        ft.DataCell(ft.Text(t["category"])),
                        ft.DataCell(ft.Text(f"${t['amount']:.2f}")),
                        ft.DataCell(ft.Text(t["description"])),
                        ft.DataCell(
                            ft.IconButton(
                                ft.Icons.DELETE,
                                on_click=lambda e, i=index: delete_transaction(i),
                            )
                        ),
                    ]
                )
            )

        page.update()

    def delete_transaction(index):
        amount = selected_category.transactions[index]["amount"]
        selected_category._budget -= amount
        selected_category.transactions.pop(index)
        save_data()
        refresh_ui()

    def change_category(e):
        nonlocal selected_category
        selected_category = categories[category_dropdown.value]
        refresh_ui()

    def add_transaction(e):
        current_category = categories[category_dropdown.value] 

        try:
            amount = float(amount_field.value)
        except:
            show_error("Please enter a valid number.")
            return

        if amount <= 0:
            show_error("Amount must be positive.")
            return

        date_value = date_field.value or datetime.now().strftime("%Y-%m-%d")

        transaction = Transaction(
            amount=amount,
            category=category_dropdown.value,
            type=transaction_type.value,
            date=date_value,
            description=description_field.value,
        )

        old_budget = current_category.budget
        current_category.add_transaction(transaction)

        if current_category.budget == old_budget and transaction_type.value == "Withdrawal":
            show_error("Withdrawal exceeds budget.")
            return

        current_category.transactions[-1] = transaction.to_dict()

        amount_field.value = ""
        description_field.value = ""
        date_field.value = ""

        save_data()
        refresh_ui()

    def show_error(message):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    category_dropdown.on_change = change_category
    month_filter.on_change = lambda e: refresh_ui()

    add_button = ft.ElevatedButton("Add Transaction", on_click=add_transaction)

    # -------------------------
    # LAYOUT (Dashboard Style)
    # -------------------------

    page.add(
        ft.Column(
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Expense Dashboard", size=30, weight=ft.FontWeight.BOLD),

                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=ft.Column(
                            controls=[
                                category_dropdown,
                                budget_text,
                                progress_bar,
                            ]
                        ),
                    )
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        amount_field,
                        date_field,
                        description_field,
                    ],
                ),

                transaction_type,
                add_button,
                month_filter,

                ft.Card(
                    content=ft.Container(
                        padding=20,
                        content=table,
                    )
                ),
            ],
        )
    )

    refresh_ui()
