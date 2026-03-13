import flet as ft
import datetime
import bcrypt
from db.database import update_username, update_user_password, update_user_email


class ProfileView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user = page.data

        self.new_username_field = ft.TextField(label="New Username", width=300, hint_text=f"Current: {self.user.username}")
        self.username_message = ft.Text("", size=12)

        self.new_email_field = ft.TextField(label="New Email", width=300, hint_text=f"Current: {self.user.email}")
        self.email_message = ft.Text("", size=12)

        self.birthday_display = ft.Text(f"Birthday: {self.user.birthday}", size=18, color="grey")
        self.birthday_date_picker = ft.DatePicker(
            first_date=datetime.datetime(1900, 1, 1),
            last_date=datetime.datetime.now(),
            on_change=self.handle_birthday_picked,
        )
        page.overlay.append(self.birthday_date_picker)
        self.birthday_message = ft.Text("", size=12)

        self.current_password_field = ft.TextField(label="Current Password", password=True, can_reveal_password=True, width=300)
        self.new_password_field = ft.TextField(label="New Password", password=True, can_reveal_password=True, width=300)
        self.confirm_password_field = ft.TextField(label="Confirm New Password", password=True, can_reveal_password=True, width=300)
        self.password_message = ft.Text("", size=12)

        self.selected_birthday = None

    def build(self):
        return ft.Column(
            [
                ft.Row(
                    [ft.TextButton("← Back to Dashboard", on_click=self.go_back)],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text("Profile", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),

                ft.Text("Account Information", size=20, weight=ft.FontWeight.BOLD),
                ft.Text(f"Username: {self.user.username}", size=18),
                ft.Text(f"Email: {self.user.email}", size=18),
                self.birthday_display,
                ft.Divider(),

                ft.Text("Change Username", size=20, weight=ft.FontWeight.BOLD),
                self.new_username_field,
                self.username_message,
                ft.ElevatedButton("Update Username", on_click=self.handle_update_username),
                ft.Divider(),

                ft.Text("Change Email", size=20, weight=ft.FontWeight.BOLD),
                self.new_email_field,
                self.email_message,
                ft.ElevatedButton("Update Email", on_click=self.handle_update_email),
                ft.Divider(),

                ft.Text("Change Birthday", size=20, weight=ft.FontWeight.BOLD),
                ft.Row(
                    [
                        self.birthday_display,
                        ft.TextButton("Pick new birthday", on_click=self.open_birthday_picker),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                self.birthday_message,
                ft.ElevatedButton("Update Birthday", on_click=self.handle_update_birthday),
                ft.Divider(),

                ft.Text("Change Password", size=20, weight=ft.FontWeight.BOLD),
                self.current_password_field,
                self.new_password_field,
                self.confirm_password_field,
                self.password_message,
                ft.ElevatedButton("Update Password", on_click=self.handle_update_password),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

    def open_birthday_picker(self, e):
        self.birthday_date_picker.open = True
        self.page.update()

    def handle_birthday_picked(self, e):
        v = e.control.value
        self.selected_birthday = datetime.date(v.year, v.month, v.day)
        self.birthday_display.value = f"Birthday: {self.selected_birthday}"
        self.page.update()

    def handle_update_username(self, e):
        new_username = self.new_username_field.value.strip()
        if not new_username:
            self._set_message(self.username_message, "Username cannot be empty.", "red")
            return
        if new_username == self.user.username:
            self._set_message(self.username_message, "That's already your current username.", "red")
            return
        self.user.username = new_username
        self.new_username_field.hint_text = f"Current: {self.user.username}"
        self.new_username_field.value = ""
        self._set_message(self.username_message, "Username updated successfully!", "green")

    def handle_update_email(self, e):
        new_email = self.new_email_field.value.strip().lower()
        if not new_email:
            self._set_message(self.email_message, "Email cannot be empty.", "red")
            return
        if new_email == self.user.email:
            self._set_message(self.email_message, "That's already your current email.", "red")
            return
        if "@" not in new_email or "." not in new_email:
            self._set_message(self.email_message, "Please enter a valid email address.", "red")
            return
        update_user_email(self.user.user_id, new_email)
        self.user.email = new_email
        self.new_email_field.hint_text = f"Current: {self.user.email}"
        self.new_email_field.value = ""
        self._set_message(self.email_message, "Email updated successfully!", "green")

    def handle_update_birthday(self, e):
        if not self.selected_birthday:
            self._set_message(self.birthday_message, "Please pick a new birthday first.", "red")
            return
        from db.database import update_user_birthday
        error = update_user_birthday(self.user.user_id, str(self.selected_birthday))
        if error:
            self._set_message(self.birthday_message, error, "red")
            return
        self.user.birthday = self.selected_birthday
        self._set_message(self.birthday_message, "Birthday updated successfully!", "green")

    def handle_update_password(self, e):
        current_password = self.current_password_field.value
        new_password = self.new_password_field.value
        confirm_password = self.confirm_password_field.value

        if not all([current_password, new_password, confirm_password]):
            self._set_message(self.password_message, "Please fill in all password fields.", "red")
            return
        if not bcrypt.checkpw(current_password.encode(), self.user.password.encode()):
            self._set_message(self.password_message, "Current password is incorrect.", "red")
            return
        if new_password != confirm_password:
            self._set_message(self.password_message, "New passwords do not match.", "red")
            return
        if new_password == current_password:
            self._set_message(self.password_message, "New password must be different from current.", "red")
            return

        error = update_user_password(self.user.user_id, new_password)
        if error:
            self._set_message(self.password_message, error, "red")
            return

        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.user._password = new_hash
        self.current_password_field.value = ""
        self.new_password_field.value = ""
        self.confirm_password_field.value = ""
        self._set_message(self.password_message, "Password updated successfully!", "green")

    def _set_message(self, text_control, message, color):
        text_control.value = message
        text_control.color = color
        self.page.update()

    def go_back(self, e):
        self.page.go("/dashboard")