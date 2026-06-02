import flet as ft
import json
import os
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE, "storages", "medicines.json")


PRIMARY      = "#0F172A"
ACCENT       = "#38BDF8"
ACCENT_DARK  = "#0EA5E9"
SURFACE      = "#F8FAFC"
CARD_BG      = "#FFFFFF"
MUTED        = "#94A3B8"
DANGER       = "#F43F5E"
SUCCESS      = "#10B981"
TEXT_MAIN    = "#0F172A"
TEXT_LIGHT   = "#FFFFFF"
SIDEBAR_W    = 260


def load_data():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)






def section_title(text):
    return ft.Text(text, size=22, weight=ft.FontWeight.BOLD, color=TEXT_MAIN)


def styled_field(label, value=""):
    return ft.TextField(
        label=label,
        value=value,
        border_radius=10,
        border_color=ACCENT,
        focused_border_color=ACCENT_DARK,
        label_style=ft.TextStyle(color=MUTED),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        bgcolor=CARD_BG,
        filled=True,
    )


def primary_btn(text, icon, on_click):
    return ft.ElevatedButton(
        text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=ACCENT_DARK,
            color=TEXT_LIGHT,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=24, vertical=14),
        ),
    )


def success_text(msg):
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=SUCCESS),
            ft.Text(msg, size=16, color=SUCCESS, weight=ft.FontWeight.W_600),
        ], spacing=8),
        bgcolor="#ECFDF5",
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )





def med_card(med, index, on_edit, on_delete):
    try:
        qty = int(med["amount"])
        qty_color = DANGER if qty < 5 else SUCCESS
    except Exception:
        qty_color = MUTED

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        margin=ft.margin.only(bottom=10),
        border_radius=14,
        bgcolor=CARD_BG,
        shadow=ft.BoxShadow(
            blur_radius=12,
            spread_radius=0,
            offset=ft.Offset(0, 3),
            color="#1A0F172A",
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=6,
                    controls=[
                        ft.Text(med["name"], size=17, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    f"{med['amount']} шт",
                                    size=12, color=qty_color, weight=ft.FontWeight.W_600,
                                ),
                                bgcolor=f"{qty_color}22",
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                            ft.Container(
                                content=ft.Text(f"до {med['date']}", size=12, color=MUTED),
                                bgcolor="#F1F5F9",
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            ),
                        ], spacing=8),
                    ],
                ),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        icon_color=ACCENT_DARK,
                        icon_size=20,
                        tooltip="Редагувати",
                        on_click=lambda e, i=index: on_edit(i),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=DANGER,
                        icon_size=20,
                        tooltip="Видалити",
                        on_click=lambda e, i=index: on_delete(i),
                    ),
                ], spacing=0),
            ],
        ),
    )





def admin_view(page: ft.Page):

    content_area = ft.Container(

        expand=True,
        bgcolor=SURFACE,
        padding=ft.padding.all(32),
        content=ft.Column([
            ft.Icon(ft.Icons.DASHBOARD_OUTLINED, size=52, color=ACCENT),
            ft.Text("Оберіть дію у меню зліва", size=18, color=MUTED),
        ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),

    )

    async def go_back(e):
        await page.push_route("/")

    # ── ПЕРЕГЛЯД ──
    async def show_storage(e):
        medicines = load_data()

        def on_delete(index):
            data = load_data()
            data.pop(index)
            save_data(data)
            page.run_task(show_storage, None)

        def on_edit_inline(index):
            data = load_data()
            med = data[index]
            f_name   = styled_field("Назва", med["name"])
            f_amount = styled_field("Кількість", str(med["amount"]))
            f_date   = styled_field("Термін", med["date"])

            def save_edit(ev):
                data = load_data()
                data[index] = {"name": f_name.value, "amount": f_amount.value, "date": f_date.value}
                save_data(data)
                page.run_task(show_storage, None)

            content_area.content = ft.Column([
                section_title("Редагування картки"),
                ft.Divider(color="#E2E8F0"),
                f_name, f_amount, f_date,
                primary_btn("Зберегти", ft.Icons.SAVE_OUTLINED, save_edit),
            ], spacing=16,horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,)
            page.update()

        cards = [med_card(m, i, on_edit_inline, on_delete) for i, m in enumerate(medicines)]

        if not cards:
            cards = [ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=48, color=MUTED),
                    ft.Text("Склад порожній", size=18, color=MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment.CENTER,
                padding=40,
            )]

        content_area.content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            controls=[
                ft.Row([
                    section_title("Склад препаратів"),
                    ft.Container(
                        content=ft.Text(f"{len(medicines)} позицій", size=13, color=MUTED),
                        bgcolor="#F1F5F9",
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    ),
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Divider(color="#E2E8F0", height=24),
                *cards,
            ],
        )
        page.update()


    async def add_product(e):
        f_name   = styled_field("Назва препарату")
        f_amount = styled_field("Кількість")
        f_date   = styled_field("Термін придатності (дд.мм.рррр)")

        async def save_product(ev):
            data = load_data()
            data.append({"name": f_name.value, "amount": f_amount.value, "date": f_date.value})
            save_data(data)
            content_area.content = ft.Column([
                section_title("Додати препарат"),
                ft.Divider(color="#E2E8F0"),
                success_text("Препарат успішно додано!"),
            ], spacing=16,horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,)
            page.update()

        content_area.content = ft.Column([
            section_title("Додати препарат"),
            ft.Divider(color="#E2E8F0"),
            f_name, f_amount, f_date,
            primary_btn("Зберегти", ft.Icons.ADD_CIRCLE_OUTLINE, save_product),
        ], spacing=16,horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,)
        page.update()


    async def sell_product(e):
        f_name   = styled_field("Назва препарату")
        f_amount = styled_field("Кількість")

        async def confirm_sell(ev):
            data = load_data()
            for med in data:
                if med["name"].lower() == f_name.value.lower():
                    med["amount"] = str(int(med["amount"]) - int(f_amount.value))
            save_data(data)
            content_area.content = ft.Column([
                section_title("Продаж"),
                ft.Divider(color="#E2E8F0"),
                success_text("Продаж виконано успішно!"),
            ], spacing=16)
            page.update()

        content_area.content = ft.Column([
            section_title("Продаж препарату"),
            ft.Divider(color="#E2E8F0"),
            f_name, f_amount,
            primary_btn("Продати", ft.Icons.SELL_OUTLINED, confirm_sell),
        ], spacing=16,horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,)
        page.update()


    async def return_product(e):
        f_name   = styled_field("Назва препарату")
        f_amount = styled_field("Кількість")

        async def confirm_return(ev):
            data = load_data()
            for med in data:
                if med["name"].lower() == f_name.value.lower():
                    med["amount"] = str(int(med["amount"]) + int(f_amount.value))
            save_data(data)
            content_area.content = ft.Column([
                section_title("Повернення"),
                ft.Divider(color="#E2E8F0"),
                success_text("Повернення виконано!"),
            ], spacing=16)
            page.update()

        content_area.content = ft.Column([
            section_title("Повернення препарату"),
            ft.Divider(color="#E2E8F0"),
            f_name, f_amount,
            primary_btn("Повернути", ft.Icons.ASSIGNMENT_RETURN_OUTLINED, confirm_return),
        ], spacing=16)
        page.update()


    async def delete_expired(e):
        data = load_data()
        now = datetime.now()
        valid, deleted = [], 0
        for med in data:
            try:
                if datetime.strptime(med["date"], "%d.%m.%Y") >= now:
                    valid.append(med)
                else:
                    deleted += 1
            except Exception:
                valid.append(med)
        save_data(valid)
        content_area.content = ft.Column([
            section_title("Видалення прострочених"),
            ft.Divider(color="#E2E8F0"),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_SWEEP_OUTLINED, color=DANGER),
                    ft.Text(f"Видалено: {deleted} препарат(ів)", size=16,
                            color=DANGER, weight=ft.FontWeight.W_600),
                ], spacing=8),
                bgcolor="#FFF1F2",
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            ),
        ], spacing=16)
        page.update()


    async def edit_product(e):
        f_old    = styled_field("Поточна назва")
        f_name   = styled_field("Нова назва")
        f_amount = styled_field("Нова кількість")
        f_date   = styled_field("Новий термін")

        async def confirm_edit(ev):
            data = load_data()
            for med in data:
                if med["name"].lower() == f_old.value.lower():
                    med["name"] = f_name.value
                    med["amount"] = f_amount.value
                    med["date"] = f_date.value
            save_data(data)
            content_area.content = ft.Column([
                section_title("Редагування"),
                ft.Divider(color="#E2E8F0"),
                success_text("Препарат оновлено!"),
            ], spacing=16)
            page.update()

        content_area.content = ft.Column([
            section_title("Редагування препарату"),
            ft.Divider(color="#E2E8F0"),
            f_old, f_name, f_amount, f_date,
            primary_btn("Зберегти зміни", ft.Icons.EDIT_OUTLINED, confirm_edit),
        ], spacing=16)
        page.update()


    sidebar = ft.Container(
        width=300,
        bgcolor=PRIMARY,
        padding=ft.padding.symmetric(horizontal=16, vertical=24),
        content=ft.Column(
            spacing=4,
            expand=True,
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCAL_PHARMACY, color=ACCENT, size=26),
                        ft.Text("PharmAdmin", size=18, color=TEXT_LIGHT, weight=ft.FontWeight.BOLD),
                    ], spacing=10),
                    margin=ft.margin.only(bottom=20),
                ),
                ft.Button("Переглянути склад",  icon = ft.Icons.INVENTORY_2_OUTLINED,on_click = show_storage, width = 250,),
                ft.Button("Продаж", icon = ft.Icons.SELL_OUTLINED,on_click =sell_product, width = 250,),
                ft.Button("Повернення",icon = ft.Icons.ASSIGNMENT_RETURN_OUTLINED, on_click =return_product, width = 250,),
                ft.Button("Додати препарат",icon =ft.Icons.ADD_CIRCLE_OUTLINE,         on_click =add_product, width = 250,),
                ft.Button("Видалити прострочені",icon =ft.Icons.DELETE_SWEEP_OUTLINED,      on_click =delete_expired, width = 250,),
                ft.Button("Редагувати препарат",icon =ft.Icons.EDIT_OUTLINED,              on_click =edit_product, width = 250,),
                ft.Container(expand=True),
                ft.Divider(color="#1E293B"),
                ft.Button("Вийти",icon = ft.Icons.LOGOUT_OUTLINED, on_click =go_back,),
            ],
        ),
    )

    return ft.View(
        route="/admin",
        padding=0,
        bgcolor=SURFACE,

        controls=[
            ft.Row(
                expand=True,
                spacing=0,
                controls=[sidebar, content_area],
            )
        ],
    )
