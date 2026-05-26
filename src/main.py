import flet as ft

from views.login import login_view
from views.admin import admin_view

from views.pharmacist_view import pharmacist_view

def main(page: ft.Page):
    page.title = "Склад"
    page.window_width = 800
    page.theme_mode = ft.ThemeMode.LIGHT


    user_state = {"role": None}


    def route_change():
        page.views.clear()


        page.views.append(login_view(page))

        if page.route == "/admin":
            page.views.append(admin_view(page))


        elif page.route == "/pharm":
            page.views.append(pharmacist_view(page))

        page.update()


    async def view_pop(e):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop


    route_change()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)