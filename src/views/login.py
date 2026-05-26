import flet as ft
from src.models import authenticate

def login_view(page: ft.Page):

    login_input = ft.TextField(label="Логін")
    pass_input = ft.TextField(label="Пароль", password=True, can_reveal_password=True)
    err_msg = ft.Text(color = 'red')


    async def handle_login(e):

        login = login_input.value
        password = pass_input.value


        role = authenticate(login, password)

        if role == "admin":
            await page.push_route("/admin")
        elif role == "pharm":
            await page.push_route("/pharm")
        else:

            err_msg.value = "Невірний логін або пароль"
            page.update()


    return ft.View(
        route="/",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Вхід", size=30, weight=ft.FontWeight.BOLD),


                        login_input,
                        pass_input,


                        ft.Button(
                            "Увійти",
                            on_click=handle_login,
                            width=200,
                            bgcolor=ft.Colors.BLUE_700,
                            color=ft.Colors.WHITE,
                        ),
                        err_msg,
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=350,
                padding=20,
                border_radius=15,
                bgcolor=ft.Colors.WHITE,
                shadow=ft.BoxShadow(
                    blur_radius=15,
                    spread_radius=2,
                    color=ft.Colors.BLACK12
                ),
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )