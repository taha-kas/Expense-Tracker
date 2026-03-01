import flet as ft
from db.database import get_categories_by_user, create_category


class DashboardView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = page.data
        self.categories = []
        self.show_inactive = False

        self.new_category_name = ft.TextField(label="Category Name", width=220)
        self.new_category_budget = ft.TextField(label="Budget (optional)", width=220, keyboard_type=ft.KeyboardType.NUMBER)
        self.form_message = ft.Text("", color="red", size=12)
        self.category_list = ft.Column(spacing=8)

    def build(self):
        self.load_categories()

        self.toggle_btn = ft.TextButton(
            "Show Inactive Categories",
            on_click=self.toggle_inactive
        )

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(f"Welcome, {self.user.username}!", size=22, weight=ft.FontWeight.BOLD),
                        ft.ElevatedButton("Logout", on_click=self.logout),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Text("Create New Category", size=16, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [self.new_category_name, self.new_category_budget],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self.form_message,
                ft.ElevatedButton("Add Category", on_click=self.handle_create_category),
                ft.Divider(),
                ft.Text("Your Categories", size=16, weight=ft.FontWeight.BOLD),
                self.toggle_btn,
                self.category_list,
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def load_categories(self):
        self.categories = get_categories_by_user(self.user.user_id)
        self.refresh_category_list()

    def refresh_category_list(self):
        self.category_list.controls.clear()

        visible = [c for c in self.categories if c.is_active or self.show_inactive]

        if not visible:
            self.category_list.controls.append(
                ft.Text("No categories yet. Create one above!", italic=True, color="grey")
            )
        else:
            for cat in visible:
                self.category_list.controls.append(self.build_category_card(cat))

        self.page.update()

    def open_category(self, category):
        self.page.selected_category = category
        self.page.go("/category")

    def build_category_card(self, category):
        is_active = category.is_active

        edit_name_field = ft.TextField(value=category.name, width=180, visible=False)
        edit_budget_field = ft.TextField(value=str(category.budget), width=180, visible=False, keyboard_type=ft.KeyboardType.NUMBER)
        edit_message = ft.Text("", color="red", size=11)
        edit_row = ft.Row([edit_name_field, edit_budget_field], visible=False)
        save_btn = ft.ElevatedButton("Save", visible=False)

        def save_edit(e):
            new_name = edit_name_field.value.strip()
            new_budget_str = edit_budget_field.value.strip()

            if not new_name:
                edit_message.value = "Name cannot be empty."
                self.page.update()
                return

            try:
                new_budget = float(new_budget_str) if new_budget_str else category.budget
                if new_budget < 0:
                    raise ValueError
            except ValueError:
                edit_message.value = "Budget must be a positive number."
                self.page.update()
                return

            category.name = new_name
            category.budget = new_budget
            edit_message.value = ""
            edit_row.visible = False
            save_btn.visible = False
            self.refresh_category_list()

        save_btn.on_click = save_edit

        def toggle_edit(e):
            edit_row.visible = not edit_row.visible
            edit_name_field.visible = edit_row.visible
            edit_budget_field.visible = edit_row.visible
            save_btn.visible = edit_row.visible
            self.page.update()

        def toggle_active(e):
            if category.is_active:
                category.soft_delete_category()
            else:
                category.restore_category()
            self.refresh_category_list()

        status_color = "green" if is_active else "grey"
        status_label = "Active" if is_active else "Inactive"
        toggle_label = "Deactivate" if is_active else "Restore"

        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.TextButton(
                                            category.name,
                                            on_click=lambda e, cat=category: self.open_category(cat),
                                            style=ft.ButtonStyle(
                                                text_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD)
                                            ),
                                        ),
                                        ft.Text(f"Budget: ${category.budget:.2f}", size=13),
                                        ft.Text(status_label, size=11, color=status_color),
                                    ],
                                    expand=True,
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton("Edit", on_click=toggle_edit),
                                        ft.TextButton(
                                            toggle_label,
                                            on_click=toggle_active,
                                            style=ft.ButtonStyle(
                                                color={"": "red"} if is_active else {"": "green"}
                                            )
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

    def handle_create_category(self, e):
        name = self.new_category_name.value.strip()
        budget_str = self.new_category_budget.value.strip()

        if not name:
            self.form_message.value = "Category name cannot be empty."
            self.page.update()
            return

        try:
            budget = float(budget_str) if budget_str else 0
            if budget < 0:
                raise ValueError
        except ValueError:
            self.form_message.value = "Budget must be a positive number."
            self.page.update()
            return

        category, error = create_category(self.user.user_id, name, budget)

        if error:
            self.form_message.value = error
            self.page.update()
            return

        self.form_message.value = ""
        self.new_category_name.value = ""
        self.new_category_budget.value = ""
        self.categories.append(category)
        self.refresh_category_list()

    def toggle_inactive(self, e):
        self.show_inactive = not self.show_inactive
        self.toggle_btn.text = "Hide Inactive Categories" if self.show_inactive else "Show Inactive Categories"
        self.refresh_category_list()

    def logout(self, e):
        self.page.data = None
        self.page.go("/")