import flet as ft
import datetime
import base64
from db.database import (
    get_transactions_by_category,
    create_transaction,
    update_transaction_amount,
    update_transaction_description,
    update_transaction_date,
    delete_transaction,
)
from analytics.analysis import load_transactions, load_categories, budget_vs_spending
from analytics.charts import chart_budget_vs_spending


class CategoryDetailView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.category = getattr(page, "selected_category", None)
        self.transactions = []
        self.selected_month = None  # None means show all

        self.transaction_type = "Deposit" if self.category.is_income() else "Withdrawal"

        # Form fields
        self.amount_field = ft.TextField(label="Amount ($)", width=150, keyboard_type=ft.KeyboardType.NUMBER)
        self.date_display = ft.Text("Date: Today", size=13, color="grey")
        self.selected_date = None  # stores datetime.date object
        self.description_field = ft.TextField(label="Description (optional)", width=280)
        self.form_message = ft.Text("", color="red", size=12)

        # Date picker
        self.date_picker = ft.DatePicker(
            first_date=datetime.datetime(2000, 1, 1),
            last_date=datetime.datetime(2100, 12, 31),
            on_change=self.handle_date_picked,
        )
        page.overlay.append(self.date_picker)

        # Month filter
        self.month_filter = ft.Dropdown(
            label="Filter by month",
            width=200,
            options=[ft.dropdown.Option("All")],
            value="All",
        )
        self.month_filter.on_change = self.handle_month_filter

        self.transaction_list = ft.Column(spacing=8)
        self.summary_text = ft.Text("", size=13, color="grey")

        placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        self.budget_chart = ft.Image(src=placeholder, visible=False, width=700)

    def build(self):
        self.load_transactions()

        is_income = self.category.is_income()
        type_color = "green" if is_income else "red"
        type_label = "Income" if is_income else "Spending"
        action_label = "Log Deposit" if is_income else "Log Withdrawal"

        budget_row = ft.Text(
            f"Monthly Budget: ${self.category.budget:,.2f}",
            size=14, color="grey"
        ) if not is_income and self.category.budget is not None else ft.Text("")

        chart_section = ft.Column(
            [
                ft.Divider(),
                ft.Text("Budget vs Spending", size=16, weight=ft.FontWeight.BOLD),
                self.budget_chart,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ) if not is_income else ft.Column([])

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.TextButton("← Back to Dashboard", on_click=self.go_back),
                        ft.ElevatedButton("Logout", on_click=self.logout),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row([
                    ft.Text(self.category.name, size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"[{type_label}]", size=14, color=type_color),
                ], spacing=10),
                budget_row,
                self.summary_text,
                ft.Divider(),

                ft.Text(action_label, size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [self.amount_field, self.description_field],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    [
                        self.date_display,
                        ft.TextButton(
                            "Pick date",
                            on_click=self.open_date_picker,
                        ),
                        ft.TextButton("Clear (use today)", on_click=self.clear_date),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self.form_message,
                ft.ElevatedButton(action_label, on_click=self.handle_add_transaction),
                ft.Divider(),

                ft.Row(
                    [
                        ft.Text("Transaction History", size=16, weight=ft.FontWeight.BOLD),
                        self.month_filter,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=600,
                ),
                self.transaction_list,
                chart_section,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def open_date_picker(self, e):
        self.date_picker.open = True
        self.page.update()

    def _open_picker(self, picker):
        picker.open = True
        self.page.update()

    def handle_date_picked(self, e):
        v = e.control.value
        self.selected_date = datetime.date(v.year, v.month, v.day)
        self.date_display.value = f"Date: {self.selected_date.strftime('%Y-%m-%d')}"
        self.page.update()

    def clear_date(self, e):
        self.selected_date = None
        self.date_display.value = "Date: Today"
        self.page.update()

    def _transaction_month(self, t):
        d = t.transaction_date
        if hasattr(d, "strftime"):
            return d.strftime("%Y-%m")
        return str(d)[:7]

    def populate_month_filter(self):
        months = sorted(set(self._transaction_month(t) for t in self.transactions), reverse=True)
        current = self.month_filter.value
        self.month_filter.options = [ft.dropdown.Option("All")] + [
            ft.dropdown.Option(m) for m in months
        ]
        # Preserve selection if still valid, else reset to All
        valid = [o.key for o in self.month_filter.options]
        self.month_filter.value = current if current in valid else "All"

    def handle_month_filter(self, e):
        val = e.control.value
        self.selected_month = None if val == "All" else val
        self.refresh_transaction_list()

    def load_transactions(self):
        self.transactions = get_transactions_by_category(self.category.category_id)
        self.populate_month_filter()
        self.refresh_transaction_list()
        self.refresh_summary()
        if self.category.is_spending():
            self.refresh_budget_chart()

    def refresh_summary(self):
        total = sum(t.amount for t in self.transactions)
        if self.category.is_income():
            self.summary_text.value = f"Total deposited: ${total:,.2f}"
        else:
            self.summary_text.value = f"Total withdrawn: ${total:,.2f}"
        self.page.update()

    def refresh_budget_chart(self):
        try:
            user_id = self.page.data.user_id
            df = load_transactions(user_id)
            categories_df = load_categories(user_id)

            df_cat = df[df["category_id"] == self.category.category_id]
            cat_row = categories_df[categories_df["category_id"] == self.category.category_id]

            if df_cat.empty or cat_row.empty:
                self.budget_chart.visible = False
                self.page.update()
                return

            df_budget = budget_vs_spending(df_cat, cat_row)
            chart_bytes = chart_budget_vs_spending(df_budget)

            if chart_bytes:
                self.budget_chart.src = base64.b64encode(chart_bytes).decode("utf-8")
                self.budget_chart.visible = True
            else:
                self.budget_chart.visible = False

            self.page.update()
        except Exception as ex:
            print(f"Chart error: {ex}")
            self.budget_chart.visible = False

    def refresh_transaction_list(self):
        self.transaction_list.controls.clear()

        filtered = self.transactions
        if self.selected_month:
            filtered = [t for t in self.transactions if self._transaction_month(t) == self.selected_month]

        if not filtered:
            self.transaction_list.controls.append(
                ft.Text("No transactions found.", italic=True, color="grey")
            )
        else:
            for t in filtered:
                self.transaction_list.controls.append(self.build_transaction_card(t))

        self.page.update()

    def build_transaction_card(self, transaction):
        is_income = self.category.is_income()
        amount_color = "green" if is_income else "red"
        sign = "+" if is_income else "-"

        edit_amount_field = ft.TextField(value=str(transaction.amount), width=130, visible=False, keyboard_type=ft.KeyboardType.NUMBER)
        edit_description_field = ft.TextField(value=transaction.description, width=200, visible=False)
        edit_message = ft.Text("", color="red", size=11)

        # Date picker for edit
        edit_selected_date = {"value": None}
        edit_date_display = ft.Text(str(transaction.transaction_date), size=12, color="grey")

        edit_date_picker = ft.DatePicker(
            first_date=datetime.datetime(2000, 1, 1),
            last_date=datetime.datetime(2100, 12, 31),
        )
        self.page.overlay.append(edit_date_picker)

        def on_edit_date_picked(e):
            v = e.control.value
            edit_selected_date["value"] = datetime.date(v.year, v.month, v.day)
            edit_date_display.value = str(edit_selected_date["value"])
            self.page.update()

        edit_date_picker.on_change = on_edit_date_picked

        edit_row = ft.Row([
            edit_amount_field,
            edit_description_field,
        ], visible=False)

        edit_date_row = ft.Row([
            edit_date_display,
            ft.TextButton("Change date", on_click=lambda e: self._open_picker(edit_date_picker)),
        ], visible=False)

        save_btn = ft.ElevatedButton("Save", visible=False)

        def save_edit(e):
            new_amount_str = edit_amount_field.value.strip()
            new_desc = edit_description_field.value.strip()
            new_date = edit_selected_date["value"] or transaction.transaction_date

            try:
                new_amount = float(new_amount_str)
                if new_amount <= 0:
                    raise ValueError
            except ValueError:
                edit_message.value = "Amount must be a positive number."
                self.page.update()
                return

            err1 = update_transaction_amount(transaction.transaction_id, new_amount)
            err2 = update_transaction_date(transaction.transaction_id, str(new_date))
            err3 = update_transaction_description(transaction.transaction_id, new_desc)

            if err1 or err2 or err3:
                edit_message.value = err1 or err2 or err3
                self.page.update()
                return

            transaction._amount = new_amount
            edit_message.value = ""
            edit_row.visible = False
            edit_date_row.visible = False
            save_btn.visible = False
            self.load_transactions()

        save_btn.on_click = save_edit

        def toggle_edit(e):
            visible = not edit_row.visible
            edit_row.visible = visible
            edit_date_row.visible = visible
            save_btn.visible = visible
            self.page.update()

        def handle_delete(e):
            def confirm_delete(e):
                confirm_dialog.open = False
                self.page.update()
                error = delete_transaction(transaction.transaction_id)
                if error:
                    edit_message.value = error
                    self.page.update()
                else:
                    self.load_transactions()

            def cancel_delete(e):
                confirm_dialog.open = False
                self.page.update()

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Delete Transaction"),
                content=ft.Text("Are you sure you want to delete this transaction? This cannot be undone."),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton(
                        "Delete",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(color={"": "red"})
                    ),
                ],
            )
            self.page.dialog = confirm_dialog
            confirm_dialog.open = True
            self.page.update()

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
                                        ft.Text(str(transaction.transaction_date), size=12),
                                        ft.Text(transaction.description, size=12, italic=True) if transaction.description else ft.Text(""),
                                    ],
                                    expand=True,
                                ),
                                ft.Row([
                                    ft.TextButton("Edit", on_click=toggle_edit),
                                    ft.TextButton(
                                        "Delete",
                                        on_click=handle_delete,
                                        style=ft.ButtonStyle(color={"": "red"})
                                    ),
                                ]),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        ),
                        edit_row,
                        edit_date_row,
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

        date_str = str(self.selected_date) if self.selected_date else None

        transaction, error = create_transaction(
            self.category.category_id, amount, self.transaction_type, date_str, description
        )

        if error:
            self.form_message.value = error
            self.page.update()
            return

        self.form_message.value = ""
        self.amount_field.value = ""
        self.description_field.value = ""
        self.selected_date = None
        self.date_display.value = "Date: Today"
        self.transactions.insert(0, transaction)
        self.populate_month_filter()
        self.load_transactions()

    def go_back(self, e):
        self.page.go("/dashboard")

    def logout(self, e):
        self.page.data = None
        self.page.selected_category = None
        self.page.go("/")