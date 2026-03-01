import flet as ft
import datetime
from db.database import (
    get_transactions_by_category,
    create_transaction,
    update_transaction_amount,
    update_transaction_description,
    update_transaction_date,
    delete_transaction,
)


class CategoryDetailView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.category = page.client_storage.get("selected_category") if False else getattr(page, "selected_category", None)
        self.transactions = []

        # --- New transaction form fields ---
        self.amount_field = ft.TextField(label="Amount", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.type_dropdown = ft.Dropdown(
            label="Type",
            width=150,
            options=[
                ft.dropdown.Option("Deposit"),
                ft.dropdown.Option("Withdrawal"),
            ],
            value="Deposit",
        )
        self.date_field = ft.TextField(label="Date (YYYY-MM-DD)", width=250, hint_text="Leave blank for today")
        self.description_field = ft.TextField(label="Description (optional)", width=300)
        self.form_message = ft.Text("", color="red", size=12)

        # --- Transaction list ---
        self.transaction_list = ft.Column(spacing=8)

        # --- Summary texts ---
        self.budget_text = ft.Text("", size=14)
        self.summary_text = ft.Text("", size=13, color="grey")

    def build(self):
        self.load_transactions()

        return ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.TextButton("← Back to Dashboard", on_click=self.go_back),
                        ft.ElevatedButton("Logout", on_click=self.logout),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(self.category.name, size=24, weight=ft.FontWeight.BOLD),
                self.budget_text,
                self.summary_text,
                ft.Divider(),

                # Add transaction form
                ft.Text("Log a Transaction", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [self.amount_field, self.type_dropdown],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [self.date_field, self.description_field],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self.form_message,
                ft.ElevatedButton("Add Transaction", on_click=self.handle_add_transaction),
                ft.Divider(),

                # Transaction list
                ft.Text("Transaction History", size=16, weight=ft.FontWeight.BOLD),
                self.transaction_list,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def load_transactions(self):
        self.transactions = get_transactions_by_category(self.category.category_id)
        self.refresh_transaction_list()
        self.refresh_summary()

    def refresh_summary(self):
        total_deposits = sum(t.amount for t in self.transactions if t.type == "Deposit")
        total_withdrawals = sum(t.amount for t in self.transactions if t.type == "Withdrawal")
        balance = total_deposits - total_withdrawals
        self.budget_text.value = f"Budget: ${self.category.budget:.2f}"
        self.summary_text.value = (
            f"Total Deposits: ${total_deposits:.2f}   |   "
            f"Total Withdrawals: ${total_withdrawals:.2f}   |   "
            f"Balance: ${balance:.2f}"
        )
        self.page.update()

    def refresh_transaction_list(self):
        self.transaction_list.controls.clear()

        if not self.transactions:
            self.transaction_list.controls.append(
                ft.Text("No transactions yet. Log one above!", italic=True, color="grey")
            )
        else:
            for t in self.transactions:
                self.transaction_list.controls.append(self.build_transaction_card(t))

        self.page.update()

    def build_transaction_card(self, transaction):
        is_deposit = transaction.type == "Deposit"
        amount_color = "green" if is_deposit else "red"
        sign = "+" if is_deposit else "-"

        edit_amount_field = ft.TextField(value=str(transaction.amount), width=130, visible=False, keyboard_type=ft.KeyboardType.NUMBER)
        edit_date_field = ft.TextField(value=str(transaction.transaction_date), width=160, visible=False)
        edit_description_field = ft.TextField(value=transaction.description, width=180, visible=False)
        edit_message = ft.Text("", color="red", size=11)
        edit_row = ft.Row([edit_amount_field, edit_date_field, edit_description_field], visible=False)
        save_btn = ft.ElevatedButton("Save", visible=False)

        def save_edit(e):
            new_amount_str = edit_amount_field.value.strip()
            new_date_str = edit_date_field.value.strip()
            new_desc = edit_description_field.value.strip()

            try:
                new_amount = float(new_amount_str)
                if new_amount <= 0:
                    raise ValueError
            except ValueError:
                edit_message.value = "Amount must be a positive number."
                self.page.update()
                return

            try:
                datetime.datetime.strptime(new_date_str, "%Y-%m-%d")
            except ValueError:
                edit_message.value = "Invalid date format. Use YYYY-MM-DD."
                self.page.update()
                return

            err1 = update_transaction_amount(transaction.transaction_id, new_amount)
            err2 = update_transaction_date(transaction.transaction_id, new_date_str)
            err3 = update_transaction_description(transaction.transaction_id, new_desc)

            if err1 or err2 or err3:
                edit_message.value = err1 or err2 or err3
                self.page.update()
                return

            # Adjust category budget by the difference in amount
            old_amount = float(transaction.amount)
            diff = new_amount - old_amount
            signed_diff = diff if transaction.type == "Deposit" else -diff
            self.category.budget = float(self.category.budget) + signed_diff

            # Update the transaction object in memory
            transaction._amount = new_amount

            edit_message.value = ""
            edit_row.visible = False
            save_btn.visible = False
            self.load_transactions()

        save_btn.on_click = save_edit

        def toggle_edit(e):
            edit_row.visible = not edit_row.visible
            edit_amount_field.visible = edit_row.visible
            edit_date_field.visible = edit_row.visible
            edit_description_field.visible = edit_row.visible
            save_btn.visible = edit_row.visible
            self.page.update()

        def handle_delete(e):
            error = delete_transaction(transaction.transaction_id)
            if error:
                edit_message.value = error
                self.page.update()
            else:
                # Reverse the transaction's effect on the budget
                signed = float(transaction.amount) if transaction.type == "Deposit" else -float(transaction.amount)
                self.category.budget = float(self.category.budget) - signed
                self.load_transactions()

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            f"{sign}${transaction.amount:.2f}",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=amount_color,
                                        ),
                                        ft.Text(transaction.type, size=12, color="grey"),
                                        ft.Text(str(transaction.transaction_date), size=12),
                                        ft.Text(transaction.description, size=12, italic=True) if transaction.description else ft.Text(""),
                                    ],
                                    expand=True,
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton("Edit", on_click=toggle_edit),
                                        ft.TextButton(
                                            "Delete",
                                            on_click=handle_delete,
                                            style=ft.ButtonStyle(color={"": "red"})
                                        ),
                                    ]
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        edit_row,
                        edit_message,
                        save_btn,
                    ],
                    spacing=6,
                ),
                padding=12,
                width=500,
            ),
            width=520,
        )

    def handle_add_transaction(self, e):
        amount_str = self.amount_field.value.strip()
        transaction_type = self.type_dropdown.value
        date_str = self.date_field.value.strip()
        description = self.description_field.value.strip()

        if not amount_str:
            self.form_message.value = "Amount cannot be empty."
            self.page.update()
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.form_message.value = "Amount must be a positive number."
            self.page.update()
            return

        if date_str:
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                self.form_message.value = "Invalid date format. Use YYYY-MM-DD."
                self.page.update()
                return
        else:
            date_str = None

        transaction, error = create_transaction(
            self.category.category_id, amount, transaction_type, date_str, description
        )

        if error:
            self.form_message.value = error
            self.page.update()
            return

        self.form_message.value = ""
        self.amount_field.value = ""
        self.date_field.value = ""
        self.description_field.value = ""
        self.type_dropdown.value = "Deposit"
        self.transactions.insert(0, transaction)

        # Update the category budget: deposits add, withdrawals subtract
        signed = amount if transaction_type == "Deposit" else -amount
        self.category.budget = float(self.category.budget) + float(signed)

        self.refresh_transaction_list()
        self.refresh_summary()

    def go_back(self, e):
        self.page.go("/dashboard")

    def logout(self, e):
        self.page.data = None
        self.page.selected_category = None
        self.page.go("/")