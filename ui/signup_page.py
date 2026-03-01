import flet as ft
import datetime
from db.database import create_user


class SignupView:

    def __init__(self, page: ft.Page):
        self.page = page

        self.username_field = ft.TextField(
            label="Username",
            width=300
        )

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

        self.confirm_password_field = ft.TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            width=300
        )

        self.birthday_field = ft.TextField(
            label="Birthday (YYYY-MM-DD)",
            width=300
        )

        self.message = ft.Text("", color="red")

        self.signup_button = ft.ElevatedButton(
            "Sign Up",
            width=300,
            on_click=self.handle_signup
        )

        self.login_link = ft.TextButton(
            "Already have an account? Log in",
            on_click=lambda e: self.page.go("/")
        )

    def build(self):
        return ft.Column(
            [
                ft.Text("Sign Up", size=30, weight=ft.FontWeight.BOLD),
                self.username_field,
                self.email_field,
                self.password_field,
                self.confirm_password_field,
                self.birthday_field,
                self.signup_button,
                self.message,
                self.login_link,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def show_error(self, message):
        self.message.value = message
        self.message.color = "red"
        self.page.update()

    def handle_signup(self, e):
        username = self.username_field.value.strip()
        email = self.email_field.value.strip().lower()
        password = self.password_field.value
        confirm_password = self.confirm_password_field.value
        birthday = self.birthday_field.value.strip()

        if not all([username, email, password, confirm_password, birthday]):
            self.show_error("Please fill in all fields.")
            return

        if password != confirm_password:
            self.show_error("Passwords do not match.")
            return

        try:
            datetime.datetime.strptime(birthday, "%Y-%m-%d")
        except ValueError:
            self.show_error("Invalid birthday format. Please use YYYY-MM-DD.")
            return

        # create_user now returns (user, error_message)
        user, error = create_user(username, email, password, birthday)

        if error:
            self.show_error(error)
            return

        self.page.data = user
        self.page.go("/dashboard")