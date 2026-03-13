import flet as ft
from ui.login_page import LoginView
from ui.signup_page import SignupView
from ui.dashboard_view import DashboardView
from ui.category_view import CategoryDetailView
from ui.profile_view import ProfileView
from ui.analytics_view import AnalyticsView

def main(page: ft.Page):
    page.title = "Expense Manager"

    def on_window_event(e):
        if e.data == "focus":
            page.window_maximized = True
            page.on_window_event = None
            page.update()

    page.on_window_event = on_window_event

    def route_change(e):
        page.views.clear()
        route = page.route or "/"

        if route == "/":
            login = LoginView(page)

            page.views.append(
                ft.View(
                    route="/",
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [login.build()],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        )
                    ],
                )
            )

        elif route == "/signup":
            signup = SignupView(page)

            page.views.append(
                ft.View(
                    route="/signup",
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [signup.build()],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        )
                    ],
                )
            )

        elif route == "/dashboard":

            user = page.data
            if not user:
                page.go("/")
                return

            dashboard = DashboardView(page)

            page.views.append(
                ft.View(
                    route="/dashboard",
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [dashboard.build()],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        )
                    ],
                )
            )

        elif route == "/profile":
            user = page.data
            if not user:
                page.go("/")
                return

            profile = ProfileView(page)

            page.views.append(
                ft.View(
                    route="/profile",
                    vertical_alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [profile.build()],
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        )
                    ],
                )
            )

        elif route == "/category":
            user = page.data
            category = getattr(page, "selected_category", None)
            if not user or not category:
                page.go("/dashboard")
                return

            detail = CategoryDetailView(page)

            page.views.append(
                ft.View(
                    route="/category",
                    vertical_alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [detail.build()],
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        )
                    ],
                )
            )

        elif route == "/analytics":
            user = page.data
            if not user:
                page.go("/")
                return

            analytics = AnalyticsView(page)

            page.views.append(
                ft.View(
                    route="/analytics",
                    vertical_alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            [analytics.build()],
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True,
                        )
                    ],
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go("/")
    route_change(None)


ft.app(target=main)