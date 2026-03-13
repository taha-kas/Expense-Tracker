import flet as ft
import base64
import datetime
from analytics.analysis import (
    load_transactions,
    load_categories,
    summary,
    spending_by_category,
    monthly_overview,
    top_spending_categories,
    budget_vs_spending,
)
from analytics.charts import (
    chart_income_vs_spending_by_month,
    chart_spending_by_category,
)


class AnalyticsView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = page.data

        placeholder = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        self.monthly_chart = ft.Image(src=placeholder, visible=False, width=700)
        self.category_chart = ft.Image(src=placeholder, visible=False, width=700)
        self.summary_row = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=16)
        self.top_spending_col = ft.Column(spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.budget_usage_col = ft.Column(spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.status_text = ft.Text("Loading analytics...", italic=True, color="grey")

    def build(self):
        self.load_data()

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.TextButton("← Back to Dashboard", on_click=self.go_back),
                        ft.ElevatedButton("Logout", on_click=self.logout),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=700,
                ),
                ft.Text("Analytics", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),

                ft.Text("Overview", size=16, weight=ft.FontWeight.BOLD),
                self.summary_row,
                ft.Divider(),

                ft.Text("Top Spending Categories", size=16, weight=ft.FontWeight.BOLD),
                self.top_spending_col,
                ft.Divider(),

                ft.Text("This Month's Budget Usage", size=16, weight=ft.FontWeight.BOLD),
                self.budget_usage_col,
                ft.Divider(),

                ft.Text("Income vs Spending by Month", size=16, weight=ft.FontWeight.BOLD),
                self.status_text,
                self.monthly_chart,
                ft.Divider(),

                ft.Text("Spending by Category", size=16, weight=ft.FontWeight.BOLD),
                self.category_chart,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def load_data(self):
        try:
            df = load_transactions(self.user.user_id)
            categories_df = load_categories(self.user.user_id)

            if df.empty:
                self.status_text.value = "No transactions yet. Start logging to see your analytics!"
                return

            # Summary cards
            stats = summary(df)
            self.summary_row.controls = [
                self._stat_card("Total Income", f"${stats['total_income']:,.2f}", "green"),
                self._stat_card("Total Spending", f"${stats['total_spending']:,.2f}", "red"),
                self._stat_card("Transactions", str(stats["num_transactions"]), "blue"),
            ]

            # Top spending categories
            top = top_spending_categories(df, n=3)
            if top.empty:
                self.top_spending_col.controls.append(
                    ft.Text("No spending recorded yet.", italic=True, color="grey")
                )
            else:
                for i, row in top.iterrows():
                    self.top_spending_col.controls.append(
                        ft.Row(
                            [
                                ft.Text(f"{i + 1}. {row['category_name']}", size=13, expand=True),
                                ft.Text(f"${row['total_spent']:,.2f}", size=13, color="red", weight=ft.FontWeight.BOLD),
                            ],
                            width=500,
                        )
                    )

            # Monthly budget usage per spending category
            import pandas as pd
            now = datetime.datetime.now()
            df_this_month = df[
                (df["transaction_date"].dt.month == now.month) &
                (df["transaction_date"].dt.year == now.year)
            ]
            df_budget = budget_vs_spending(df_this_month, categories_df)
            spending_budget = df_budget[df_budget["category_type"] == "spending"]

            if spending_budget.empty:
                self.budget_usage_col.controls.append(
                    ft.Text("No spending this month yet.", italic=True, color="grey")
                )
            else:
                for _, row in spending_budget.iterrows():
                    usage = row["usage_%"] if not pd.isna(row["usage_%"]) else 0
                    color = "green" if usage < 80 else ("orange" if usage < 100 else "red")
                    self.budget_usage_col.controls.append(
                        ft.Column([
                            ft.Row([
                                ft.Text(row["category_name"], size=13, expand=True),
                                ft.Text(
                                    f"${row['total_spent']:,.2f} / ${row['budget']:,.2f} ({usage}%)",
                                    size=13, color=color, weight=ft.FontWeight.BOLD
                                ),
                            ], width=500),
                            ft.ProgressBar(value=min(usage / 100, 1.0), width=500, color=color, bgcolor="#3a3a3a"),
                        ], spacing=4)
                    )
            df_overview = monthly_overview(df)
            monthly_bytes = chart_income_vs_spending_by_month(df_overview)
            if monthly_bytes:
                self.status_text.visible = False
                self.monthly_chart.src = base64.b64encode(monthly_bytes).decode("utf-8")
                self.monthly_chart.visible = True

            # Spending by category chart
            df_cat = spending_by_category(df)
            category_bytes = chart_spending_by_category(df_cat)
            if category_bytes:
                self.category_chart.src = base64.b64encode(category_bytes).decode("utf-8")
                self.category_chart.visible = True

        except Exception as ex:
            self.status_text.value = f"Error loading analytics: {ex}"

    def _stat_card(self, label, value, color):
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(label, size=12, color="grey"),
                        ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color=color),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                padding=16,
                width=160,
                alignment=ft.Alignment(0, 0),
            )
        )

    def go_back(self, e):
        self.page.go("/dashboard")

    def logout(self, e):
        self.page.data = None
        self.page.go("/")