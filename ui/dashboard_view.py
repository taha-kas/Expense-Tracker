import flet as ft
import datetime
from db.database import get_categories_by_user, create_category


class DashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = page.data
        self.categories = []
        self.show_inactive = False

        # ── Income category form ──────────────────────────────────────────────
        self.income_name_field = ft.TextField(label="Category Name", width=220)
        self.income_form_message = ft.Text("", color="red", size=12)

        # ── Spending category form ────────────────────────────────────────────
        self.spending_name_field = ft.TextField(label="Category Name", width=220)
        self.spending_budget_field = ft.TextField(
            label="Monthly Budget ($)",
            width=220,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        self.spending_form_message = ft.Text("", color="red", size=12)

        # ── Category lists ────────────────────────────────────────────────────
        self.income_list = ft.Column(spacing=8)
        self.spending_list = ft.Column(spacing=8)

    def build(self):
        self.load_categories()

        self.toggle_btn = ft.TextButton(
            "Show Inactive Categories",
            on_click=self.toggle_inactive
        )

        # ── Monthly income usage bar ──────────────────────────────────────────
        self.usage_text = ft.Text("", size=13, color="grey")
        self.usage_bar = ft.ProgressBar(value=0, width=500, color="green", bgcolor="#3a3a3a")
        self.compute_monthly_usage()

        return ft.Column(
            [
                # Header
                ft.Row(
                    [
                        ft.Text(f"Welcome, {self.user.username}!", size=22, weight=ft.FontWeight.BOLD),
                        ft.PopupMenuButton(
                            content=ft.Container(
                                content=ft.Text(
                                    self.user.username[0].upper(),
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color="white",
                                ),
                                width=36,
                                height=36,
                                border_radius=18,
                                bgcolor="blue",
                                alignment=ft.Alignment(0, 0),
                            ),
                            menu_position=ft.PopupMenuPosition.UNDER,
                            items=[
                                ft.PopupMenuItem(content=ft.Text("Profile"), on_click=self.go_to_profile),
                                ft.PopupMenuItem(content=ft.Text("Analytics"), on_click=self.go_to_analytics),
                                ft.PopupMenuItem(),
                                ft.PopupMenuItem(content=ft.Text("Logout"), on_click=self.logout),
                            ],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=700,
                ),
                ft.Divider(),

                # ── Monthly usage overview ────────────────────────────────────
                ft.Text("This Month's Overview", size=16, weight=ft.FontWeight.BOLD),
                self.usage_text,
                self.usage_bar,
                ft.Divider(),

                # ── Two column layout ─────────────────────────────────────────
                ft.Row(
                    [
                        # Income column
                        ft.Column(
                            [
                                ft.Text("Income Categories", size=16, weight=ft.FontWeight.BOLD, color="green"),
                                ft.Text("Track all money coming in.", size=12, color="grey"),
                                ft.Divider(),
                                ft.Text("New Income Category", size=13, weight=ft.FontWeight.W_500),
                                self.income_name_field,
                                self.income_form_message,
                                ft.ElevatedButton("Add Income Category", on_click=self.handle_add_income),
                                ft.Divider(),
                                self.income_list,
                            ],
                            width=340,
                            spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),

                        ft.VerticalDivider(width=1),

                        # Spending column
                        ft.Column(
                            [
                                ft.Text("Spending Categories", size=16, weight=ft.FontWeight.BOLD, color="red"),
                                ft.Text("Set budgets and track expenses.", size=12, color="grey"),
                                ft.Divider(),
                                ft.Text("New Spending Category", size=13, weight=ft.FontWeight.W_500),
                                self.spending_name_field,
                                self.spending_budget_field,
                                self.spending_form_message,
                                ft.ElevatedButton("Add Spending Category", on_click=self.handle_add_spending),
                                ft.Divider(),
                                self.toggle_btn,
                                self.spending_list,
                            ],
                            width=340,
                            spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=60,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    # ── Data loading ──────────────────────────────────────────────────────────

    def load_categories(self):
        self.categories = get_categories_by_user(self.user.user_id)
        self.refresh_category_lists()

    def refresh_category_lists(self):
        self.income_list.controls.clear()
        self.spending_list.controls.clear()

        income_cats = [c for c in self.categories if c.is_income()]
        spending_cats = [c for c in self.categories if c.is_spending()]

        if not self.show_inactive:
            income_cats = [c for c in income_cats if c.is_active]
            spending_cats = [c for c in spending_cats if c.is_active]

        if not income_cats:
            self.income_list.controls.append(
                ft.Text("No income categories yet.", italic=True, color="grey", size=12)
            )
        else:
            for cat in income_cats:
                self.income_list.controls.append(self.build_category_card(cat))

        if not spending_cats:
            self.spending_list.controls.append(
                ft.Text("No spending categories yet.", italic=True, color="grey", size=12)
            )
        else:
            for cat in spending_cats:
                self.spending_list.controls.append(self.build_category_card(cat))

        self.page.update()

    def compute_monthly_usage(self):
        """
        Computes total income and total spending for the current month
        and updates the usage bar and text.
        """
        try:
            from analytics.analysis import load_transactions
            import pandas as pd

            df = load_transactions(self.user.user_id)
            if df.empty:
                self.usage_text.value = "No transactions this month yet."
                self.usage_bar.value = 0
                return

            now = datetime.datetime.now()
            df_month = df[
                (df["transaction_date"].dt.month == now.month) &
                (df["transaction_date"].dt.year == now.year)
            ]

            total_income = df_month[df_month["category_type"] == "income"]["amount"].sum()
            total_spending = df_month[df_month["category_type"] == "spending"]["amount"].sum()

            if total_income == 0:
                self.usage_text.value = f"Total spending this month: ${total_spending:,.2f} — No income logged yet."
                self.usage_bar.value = 0
                self.usage_bar.color = "grey"
                return

            usage = total_spending / total_income
            pct = round(usage * 100, 1)

            self.usage_text.value = (
                f"This month you've spent ${total_spending:,.2f} out of ${total_income:,.2f} income "
                f"— {pct}% used"
            )
            self.usage_bar.value = min(usage, 1.0)
            if pct < 80:
                self.usage_bar.color = "green"
            elif pct < 100:
                self.usage_bar.color = "orange"
            else:
                self.usage_bar.color = "red"

        except Exception as ex:
            self.usage_text.value = "Could not load monthly overview."
            print(f"Monthly usage error: {ex}")

    # ── Category card ─────────────────────────────────────────────────────────

    def build_category_card(self, category):
        is_income = category.is_income()
        edit_name_field = ft.TextField(value=category.name, width=160, visible=False)
        edit_budget_field = ft.TextField(
            value=str(category.budget) if category.budget is not None else "",
            width=120,
            visible=False,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        edit_message = ft.Text("", color="red", size=11)
        save_btn = ft.ElevatedButton("Save", visible=False)

        def save_edit(e):
            new_name = edit_name_field.value.strip()
            if not new_name:
                edit_message.value = "Name cannot be empty."
                self.page.update()
                return

            if not is_income:
                try:
                    new_budget = float(edit_budget_field.value.strip())
                    if new_budget <= 0:
                        raise ValueError
                except ValueError:
                    edit_message.value = "Budget must be a positive number."
                    self.page.update()
                    return
                error = category.budget.__class__  # just a reference check
                category.budget = new_budget

            category.name = new_name
            edit_message.value = ""
            edit_name_field.visible = False
            edit_budget_field.visible = False
            save_btn.visible = False
            self.refresh_category_lists()

        save_btn.on_click = save_edit

        def toggle_edit(e):
            visible = not edit_name_field.visible
            edit_name_field.visible = visible
            edit_budget_field.visible = visible and not is_income
            save_btn.visible = visible
            self.page.update()

        def toggle_active(e):
            if category.is_active:
                def confirm_deactivate(e):
                    confirm_dialog.open = False
                    self.page.update()
                    category.soft_delete_category()
                    self.refresh_category_lists()

                def cancel(e):
                    confirm_dialog.open = False
                    self.page.update()

                confirm_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Deactivate Category"),
                    content=ft.Text(f"Are you sure you want to deactivate '{category.name}'?"),
                    actions=[
                        ft.TextButton("Cancel", on_click=cancel),
                        ft.TextButton(
                            "Deactivate",
                            on_click=confirm_deactivate,
                            style=ft.ButtonStyle(color={"": "orange"})
                        ),
                    ],
                )
                self.page.dialog = confirm_dialog
                confirm_dialog.open = True
                self.page.update()
            else:
                category.restore_category()
                self.refresh_category_lists()

        def go_to_detail(e):
            self.page.selected_category = category
            self.page.go("/category")

        # Budget display for spending categories
        budget_text = (
            ft.Text(f"Budget: ${category.budget:,.2f}/mo", size=12, color="grey")
            if not is_income and category.budget is not None
            else ft.Text("")
        )

        inactive_label = ft.Text("(inactive)", size=11, color="grey", italic=True) if not category.is_active else ft.Text("")

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Row([
                                            ft.TextButton(category.name, on_click=go_to_detail),
                                            inactive_label,
                                        ], spacing=4),
                                        budget_text,
                                    ],
                                    expand=True,
                                    spacing=2,
                                ),
                                ft.Row([
                                    ft.TextButton("Edit", on_click=toggle_edit),
                                    ft.TextButton(
                                        "Deactivate" if category.is_active else "Restore",
                                        on_click=toggle_active,
                                        style=ft.ButtonStyle(color={"": "orange" if category.is_active else "green"})
                                    ),
                                ]),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row([edit_name_field, edit_budget_field]),
                        edit_message,
                        save_btn,
                    ],
                    spacing=4,
                ),
                padding=10,
                width=300,
            ),
            width=310,
        )

    # ── Form handlers ─────────────────────────────────────────────────────────

    def handle_add_income(self, e):
        name = self.income_name_field.value.strip()
        if not name:
            self.income_form_message.value = "Category name cannot be empty."
            self.page.update()
            return

        category, error = create_category(self.user.user_id, name, 'income')
        if error:
            self.income_form_message.value = error
            self.page.update()
            return

        self.income_form_message.value = ""
        self.income_name_field.value = ""
        self.categories.append(category)
        self.refresh_category_lists()

    def handle_add_spending(self, e):
        name = self.spending_name_field.value.strip()
        budget_str = self.spending_budget_field.value.strip()

        if not name:
            self.spending_form_message.value = "Category name cannot be empty."
            self.page.update()
            return

        try:
            budget = float(budget_str)
            if budget <= 0:
                raise ValueError
        except ValueError:
            self.spending_form_message.value = "Please enter a valid budget greater than zero."
            self.page.update()
            return

        category, error = create_category(self.user.user_id, name, 'spending', budget)
        if error:
            self.spending_form_message.value = error
            self.page.update()
            return

        self.spending_form_message.value = ""
        self.spending_name_field.value = ""
        self.spending_budget_field.value = ""
        self.categories.append(category)
        self.refresh_category_lists()

    def toggle_inactive(self, e):
        self.show_inactive = not self.show_inactive
        self.toggle_btn.text = "Hide Inactive Categories" if self.show_inactive else "Show Inactive Categories"
        self.refresh_category_lists()

    def go_to_profile(self, e):
        self.page.go("/profile")

    def go_to_analytics(self, e):
        self.page.go("/analytics")

    def logout(self, e):
        self.page.data = None
        self.page.go("/")