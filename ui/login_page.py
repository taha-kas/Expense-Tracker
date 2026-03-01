import flet as ft
import bcrypt
from db.database import get_user_by_email


class LoginView:

    def __init__(self, page: ft.Page):
        self.page = page

        self.email_field = ft.TextField(
            label="Email",
            width=300
        )

        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300
        )

        self.message = ft.Text("", color="red")

        self.login_button = ft.ElevatedButton(
            "Login",
            width=300,
            on_click=self.handle_login
        )

        self.signup_link = ft.TextButton(
            "Don't have an account? Sign up",
            on_click=lambda e: self.page.go("/signup")
        )

    def build(self):
        return ft.Column(
            [
                ft.Text("Login", size=30, weight=ft.FontWeight.BOLD),
                self.email_field,
                self.password_field,
                self.login_button,
                self.message,
                self.signup_link,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def handle_login(self, e):
        email = self.email_field.value.strip().lower()
        password = self.password_field.value

        if not email or not password:
            self.message.value = "Please fill in all fields."
            self.page.update()
            return

        user = get_user_by_email(email)

        if not user:
            self.message.value = "User not found."
            self.page.update()
            return

        if not user.is_active:
            self.message.value = "Account is deactivated."
            self.page.update()
            return

        if bcrypt.checkpw(password.encode(), user.password.encode()):
            self.page.data = user
            self.page.go("/dashboard")
        else:
            self.message.value = "Incorrect password."
            self.page.update()