import flet as ft
import json
import os
from datetime import datetime

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE, "storages", "medicines.json")
HIST_FILE = os.path.join(BASE, "storages", "sales_history.json")
INFO_FILE = os.path.join(BASE, "storages", "medicines_info.json")

BG          = "#F5F7FA"
PANEL_BG    = "#FFFFFF"
NAV_BG      = "#00539B"
NAV_ACCENT  = "#FF6B35"
GREEN_DARK  = "#1A7A3C"
GREEN_MID   = "#28A745"
GREEN_LIGHT = "#D4EDDA"
AMBER       = "#E6960C"
AMBER_LIGHT = "#FFF3CD"
RED         = "#DC3545"
RED_LIGHT   = "#F8D7DA"
BLUE        = "#00539B"
BLUE_LIGHT  = "#E8F0F9"
TEXT_MAIN   = "#1A1A2E"
TEXT_MUTED  = "#6C757D"
TEXT_WHITE  = "#FFFFFF"
BORDER      = "#DEE2E6"


CATEGORIES = {
    "all":        ("Всі",            ft.Icons.APPS_ROUNDED),
    "pain":       ("Знеболюючі",     ft.Icons.HEALING_ROUNDED),
    "fever":      ("Жарознижуючі",   ft.Icons.THERMOSTAT_ROUNDED),
    "antibiotic": ("Антибіотики",    ft.Icons.BIOTECH_ROUNDED),
    "cardio":     ("Кардіо",         ft.Icons.FAVORITE_ROUNDED),
    "gastro":     ("Шлунок",         ft.Icons.MEDICAL_SERVICES_ROUNDED),
    "vitamin":    ("Вітаміни",       ft.Icons.STAR_ROUNDED),
    "antiviral":  ("Противірусні",   ft.Icons.CORONAVIRUS_ROUNDED),
}

CATEGORY_COLORS = {
    "pain":       ("#E8F4FD", "#0068C2"),
    "fever":      ("#FFF3CD", "#856404"),
    "antibiotic": ("#F8D7DA", "#842029"),
    "cardio":     ("#F8D7DA", "#842029"),
    "gastro":     ("#D4EDDA", "#155724"),
    "vitamin":    ("#FFF3CD", "#856404"),
    "antiviral":  ("#E2D9F3", "#432874"),
}

DEFAULT_INFO = {
    "category":    "all",
    "rx":          "Без рецепту",
    "description": "Лікарський препарат.",
    "instruction": "Приймати відповідно до призначення лікаря або інструкції на упаковці. Зберігати у недоступному для дітей місці.",
    "warning":     "Перед застосуванням проконсультуйтеся з лікарем або фармацевтом."
}



def load_info() -> dict:
    if not os.path.exists(INFO_FILE):
        return {}
    with open(INFO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_med_info(name: str) -> dict:
    info = load_info()
    return info.get(name.strip().lower(), DEFAULT_INFO)

def load_data():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_history():
    if not os.path.exists(HIST_FILE):
        with open(HIST_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(HIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def append_history(name: str, qty: int):
    history = load_history()
    history.append({
        "name":    name,
        "amount":  qty,
        "sold_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
    })
    with open(HIST_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)




def badge(text, bg, color):
    return ft.Container(
        content=ft.Text(text, size=11, color=color, weight=ft.FontWeight.W_700),
        bgcolor=bg,
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=10, vertical=3),
    )

def stock_badge(amount):
    try:
        n = int(amount)
    except Exception:
        return badge("?", "#F3F4F6", TEXT_MUTED)
    if n == 0:
        return badge("Немає в наявності", RED_LIGHT, RED)
    if n < 5:
        return badge(f"Закінчується: {n} шт", AMBER_LIGHT, AMBER)
    return badge(f"В наявності: {n} шт", GREEN_LIGHT, GREEN_DARK)

def category_badge(cat_key: str):
    if cat_key == "all":
        return ft.Container()
    label, icon = CATEGORIES.get(cat_key, ("", ft.Icons.MEDICATION_ROUNDED))
    bg, clr = CATEGORY_COLORS.get(cat_key, (BLUE_LIGHT, BLUE))
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=11, color=clr),
            ft.Text(label, size=10, color=clr, weight=ft.FontWeight.W_600),
        ], spacing=4),
        bgcolor=bg,
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )

def notify_bar(msg: str, ok: bool):
    icon  = ft.Icons.CHECK_CIRCLE_ROUNDED if ok else ft.Icons.ERROR_ROUNDED
    color = GREEN_MID if ok else RED
    bg    = GREEN_LIGHT if ok else RED_LIGHT
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, color=color, size=18),
            ft.Text(msg, size=13, color=color, weight=ft.FontWeight.W_600),
        ], spacing=8),
        bgcolor=bg,
        border_radius=8,
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
    )




def grid_card(med, on_card_click):
    try:
        n = int(med["amount"])
    except Exception:
        n = 0
    disabled = (n == 0)
    info     = get_med_info(med["name"])
    cat_key  = info.get("category", "all")
    rx_text  = info.get("rx", "Без рецепту")
    rx_color = RED if rx_text == "За рецептом" else GREEN_DARK
    rx_bg    = RED_LIGHT if rx_text == "За рецептом" else GREEN_LIGHT

    return ft.Container(
        border_radius=12,
        bgcolor=PANEL_BG if not disabled else "#FAFAFA",
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(
            blur_radius=6, spread_radius=0,
            offset=ft.Offset(0, 2), color="#0A000000",
        ),
        ink=not disabled,
        on_click=(None if disabled else lambda e, m=med: on_card_click(m)),
        opacity=0.55 if disabled else 1.0,
        content=ft.Column(spacing=0, controls=[
            # ── Фото-зона ──
            ft.Container(
                height=110,
                bgcolor=BLUE_LIGHT if not disabled else "#F0F0F0",
                border_radius=ft.border_radius.only(top_left=12, top_right=12),
                padding=ft.padding.all(14),
                content=ft.Stack([
                    ft.Container(
                        alignment=ft.Alignment.CENTER,
                        content=ft.Container(
                            width=54, height=54,
                            border_radius=12,
                            bgcolor="#FFFFFF" if not disabled else "#E9ECEF",
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.MEDICATION_ROUNDED,
                                size=28,
                                color=BLUE if not disabled else TEXT_MUTED,
                            ),
                        ),
                    ),
                    ft.Container(top=0, right=0,  content=category_badge(cat_key)),
                    ft.Container(
                        bottom=0, left=0,
                        content=ft.Container(
                            content=ft.Text(rx_text, size=9, color=rx_color,
                                            weight=ft.FontWeight.W_600),
                            bgcolor=rx_bg,
                            border_radius=4,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        ),
                    ),
                ]),
            ),

            ft.Container(
                padding=ft.padding.all(12),
                content=ft.Column(spacing=6, controls=[
                    ft.Text(
                        med["name"], size=14,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_MAIN if not disabled else TEXT_MUTED,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    stock_badge(med["amount"]),
                    ft.Row([
                        ft.Icon(ft.Icons.EVENT_OUTLINED, size=11, color=TEXT_MUTED),
                        ft.Text(f"до {med['date']}", size=11, color=TEXT_MUTED),
                    ], spacing=4),
                    ft.Divider(height=8, color=BORDER),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(
                                ft.Icons.SHOPPING_CART_CHECKOUT_ROUNDED,
                                size=14,
                                color=TEXT_WHITE if not disabled else TEXT_MUTED,
                            ),
                            ft.Text(
                                "Продати" if not disabled else "Немає",
                                size=12, weight=ft.FontWeight.W_600,
                                color=TEXT_WHITE if not disabled else TEXT_MUTED,
                            ),
                        ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                        bgcolor=NAV_ACCENT if not disabled else "#E9ECEF",
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        alignment=ft.Alignment.CENTER,
                    ),
                ]),
            ),
        ]),
    )




def history_row(entry, index):
    is_even = index % 2 == 0
    return ft.Container(
        bgcolor=PANEL_BG if is_even else BG,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=36, height=36, border_radius=18,
                    bgcolor=BLUE_LIGHT, alignment=ft.Alignment.CENTER,
                    content=ft.Text(str(index + 1), size=12,
                                    color=BLUE, weight=ft.FontWeight.W_700),
                ),
                ft.Container(width=14),
                ft.Column(spacing=3, expand=True, controls=[
                    ft.Text(entry["name"], size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text(entry["sold_at"], size=11, color=TEXT_MUTED),
                ]),
                ft.Container(
                    content=ft.Text(f"−{entry['amount']} шт",
                                    size=14, color=RED,
                                    weight=ft.FontWeight.W_700),
                    bgcolor=RED_LIGHT, border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                ),
            ],
        ),
    )




def build_detail_panel(med, on_confirm, on_cancel):
    info        = get_med_info(med["name"])
    cat_key     = info.get("category", "all")
    cat_label, cat_icon = CATEGORIES.get(cat_key, ("Препарат", ft.Icons.MEDICATION_ROUNDED))

    f_amount = ft.TextField(
        label="Кількість", value="1",
        border_radius=10, border_color=NAV_ACCENT,
        focused_border_color=NAV_BG,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        text_style=ft.TextStyle(color=TEXT_MAIN, size=18),
        bgcolor=BG, filled=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
        width=140,
    )

    def decrement(e):
        try:
            f_amount.value = str(max(1, int(f_amount.value) - 1))
            f_amount.update()
        except Exception:
            pass

    def increment(e):
        try:
            f_amount.value = str(int(f_amount.value) + 1)
            f_amount.update()
        except Exception:
            pass

    rx_text  = info.get("rx", "Без рецепту")
    rx_color = RED if rx_text == "За рецептом" else GREEN_DARK
    rx_bg    = RED_LIGHT if rx_text == "За рецептом" else GREEN_LIGHT

    return ft.Container(
        width=360, bgcolor=PANEL_BG,
        border=ft.border.only(left=ft.BorderSide(1, BORDER)),
        content=ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0, controls=[


            ft.Container(
                bgcolor=NAV_BG,
                padding=ft.padding.all(20),
                content=ft.Column(spacing=10, controls=[
                    ft.Row([
                        ft.Container(
                            width=48, height=48, border_radius=10,
                            bgcolor="#FFFFFF22", alignment=ft.Alignment.CENTER,
                            content=ft.Icon(ft.Icons.MEDICATION_ROUNDED,
                                            size=26, color=TEXT_WHITE),
                        ),
                        ft.Column(spacing=4, expand=True, controls=[
                            ft.Text(med["name"], size=17,
                                    weight=ft.FontWeight.BOLD, color=TEXT_WHITE,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Row([
                                ft.Icon(cat_icon, size=12, color="#FFFFFFAA"),
                                ft.Text(cat_label, size=11, color="#FFFFFFAA"),
                            ], spacing=4),
                        ]),
                        ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED,
                                      icon_color="#FFFFFFAA", icon_size=20,
                                      on_click=on_cancel),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    ft.Row([
                        stock_badge(med["amount"]),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.EVENT_OUTLINED, size=11, color="#FFFFFFAA"),
                                ft.Text(f"до {med['date']}", size=11, color="#FFFFFFAA"),
                            ], spacing=4),
                            bgcolor="#FFFFFF15", border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10, vertical=3),
                        ),
                        ft.Container(
                            content=ft.Text(rx_text, size=10,
                                            color=rx_color, weight=ft.FontWeight.W_600),
                            bgcolor=rx_bg, border_radius=20,
                            padding=ft.padding.symmetric(horizontal=10, vertical=3),
                        ),
                    ], spacing=8),
                ]),
            ),


            ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(spacing=14, controls=[

                    ft.Text("Про препарат", size=13,
                            weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                    ft.Container(
                        bgcolor=BLUE_LIGHT, border_radius=10,
                        padding=ft.padding.all(14),
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=16, color=BLUE),
                            ft.Text(info.get("description", ""), size=13,
                                    color=BLUE, expand=True),
                        ], spacing=10,
                           vertical_alignment=ft.CrossAxisAlignment.START),
                    ),

                    ft.Text("Спосіб застосування", size=13,
                            weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                    ft.Container(
                        bgcolor=BG, border_radius=10,
                        padding=ft.padding.all(14),
                        content=ft.Text(info.get("instruction", ""),
                                        size=13, color=TEXT_MAIN, selectable=True),
                    ),

                    ft.Container(
                        bgcolor=AMBER_LIGHT, border_radius=10,
                        padding=ft.padding.all(14),
                        content=ft.Row([
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, size=16, color=AMBER),
                            ft.Text(info.get("warning", ""), size=12,
                                    color="#856404", expand=True),
                        ], spacing=10,
                           vertical_alignment=ft.CrossAxisAlignment.START),
                    ),

                    ft.Divider(color=BORDER),

                    ft.Text("Кількість для продажу", size=13,
                            weight=ft.FontWeight.BOLD, color=TEXT_MUTED),
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE_ROUNDED,
                                      icon_color=NAV_BG, icon_size=28,
                                      on_click=decrement),
                        f_amount,
                        ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                                      icon_color=NAV_BG, icon_size=28,
                                      on_click=increment),
                    ], alignment=ft.MainAxisAlignment.CENTER,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),

                    ft.ElevatedButton(
                        "Підтвердити продаж",
                        icon=ft.Icons.SHOPPING_CART_CHECKOUT_ROUNDED,
                        on_click=lambda e: on_confirm(med, f_amount.value),
                        style=ft.ButtonStyle(
                            bgcolor=NAV_ACCENT, color=TEXT_WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(horizontal=24, vertical=16),
                        ),
                        width=320,
                    ),
                ]),
            ),
        ]),
    )




def pharmacist_view(page: ft.Page):

    current_filter   = {"value": "all"}
    current_category = {"value": "all"}
    active_tab       = {"value": "stock"}

    sell_panel_wrapper = ft.Container(visible=False, content=ft.Text(""))
    notify_wrapper     = ft.Container(visible=False, content=ft.Text(""))
    grid_column        = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
    history_column     = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True,
                                   spacing=6, visible=False)


    tab_stock_ref   = ft.Ref[ft.TextButton]()
    tab_history_ref = ft.Ref[ft.TextButton]()

    def tab_style(active: bool):
        return ft.ButtonStyle(
            bgcolor="#FFFFFF22" if active else "transparent",
            color=TEXT_WHITE if active else "#FFFFFFAA",
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.padding.symmetric(horizontal=18, vertical=8),
        )

    def switch_tab(tab: str):
        active_tab["value"] = tab
        tab_stock_ref.current.style   = tab_style(tab == "stock")
        tab_history_ref.current.style = tab_style(tab == "history")
        tab_stock_ref.current.update()
        tab_history_ref.current.update()
        grid_column.visible    = (tab == "stock")
        history_column.visible = (tab == "history")
        search_row.visible     = (tab == "stock")
        category_row.visible   = (tab == "stock")
        grid_column.update()
        history_column.update()
        search_row.update()
        category_row.update()
        if tab == "history":
            refresh_history()
        hide_panel()



    def filtered(query="", flt="all", cat="all"):
        data = load_data()
        info = load_info()
        if query:
            data = [m for m in data if query.lower() in m["name"].lower()]
        if cat != "all":
            data = [m for m in data
                    if info.get(m["name"].strip().lower(), {}).get("category", "all") == cat]
        if flt == "low":
            data = [m for m in data if int(m.get("amount", 0) or 0) < 5]
        elif flt == "ok":
            data = [m for m in data if int(m.get("amount", 0) or 0) >= 5]
        return data



    def show_notify(msg, ok):
        notify_wrapper.content = notify_bar(msg, ok)
        notify_wrapper.visible = True
        notify_wrapper.update()



    def hide_panel(e=None):
        sell_panel_wrapper.visible = False
        sell_panel_wrapper.update()

    def open_detail_panel(med):
        sell_panel_wrapper.content = build_detail_panel(med, do_sell, hide_panel)
        sell_panel_wrapper.visible = True
        sell_panel_wrapper.update()

    def do_sell(med, qty_str):
        try:
            qty = int(qty_str)
            assert qty > 0
        except Exception:
            show_notify("Введіть коректну кількість!", ok=False)
            return
        data  = load_data()
        found = False
        for m in data:
            if m["name"] == med["name"]:
                found     = True
                available = int(m["amount"])
                if qty > available:
                    show_notify(f"Недостатньо! На складі лише {available} шт.", ok=False)
                    return
                m["amount"] = str(available - qty)
                break
        if not found:
            show_notify("Препарат не знайдено!", ok=False)
            return
        save_data(data)
        append_history(med["name"], qty)
        hide_panel()
        refresh_grid(search_field.value, current_filter["value"], current_category["value"])
        show_notify(f"Продано: {med['name']} — {qty} шт.", ok=True)



    def build_grid_controls(query="", flt="all", cat="all"):
        medicines = filtered(query, flt, cat)
        if not medicines:
            return [ft.Container(
                alignment=ft.Alignment.CENTER, padding=60,
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=52, color=TEXT_MUTED),
                    ft.Text("Нічого не знайдено", size=17, color=TEXT_MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            )]
        return [ft.ResponsiveRow(
            spacing=12, run_spacing=12,
            controls=[
                ft.Column([grid_card(m, open_detail_panel)],
                          col={"xs": 12, "sm": 6, "md": 4, "lg": 3})
                for m in medicines
            ],
        )]

    def refresh_grid(query="", flt="all", cat="all"):
        grid_column.controls = build_grid_controls(query, flt, cat)
        grid_column.update()



    def refresh_history():
        history = load_history()
        if not history:
            history_column.controls = [ft.Container(
                alignment=ft.Alignment.CENTER, padding=60,
                content=ft.Column([
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, size=52, color=TEXT_MUTED),
                    ft.Text("Продажів ще не було", size=17, color=TEXT_MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            )]
        else:
            rows = list(reversed(history))
            history_column.controls = [
                ft.Container(
                    padding=ft.padding.only(bottom=4),
                    content=ft.Text(f"Всього продажів: {len(history)}",
                                    size=13, color=TEXT_MUTED),
                ),
                *[history_row(e, i) for i, e in enumerate(rows)],
            ]
        history_column.update()


    search_field = ft.TextField(
        hint_text="Пошук препарату…",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=10, border_color=BORDER,
        focused_border_color=NAV_BG,
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        bgcolor=PANEL_BG, filled=True, expand=True,
        on_change=lambda e: refresh_grid(
            e.control.value, current_filter["value"], current_category["value"]),
    )


    stock_chip_row_ref = ft.Ref[ft.Row]()

    def stock_chip(label, value):
        def on_tap(e):
            current_filter["value"] = value
            stock_chip_row_ref.current.controls = make_stock_chips()
            stock_chip_row_ref.current.update()
            refresh_grid(search_field.value, value, current_category["value"])
        selected = current_filter["value"] == value
        return ft.TextButton(label, on_click=on_tap,
            style=ft.ButtonStyle(
                bgcolor=NAV_BG if selected else BG,
                color=TEXT_WHITE if selected else TEXT_MUTED,
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=14, vertical=6),
            ))

    def make_stock_chips():
        return [stock_chip("Всі", "all"),
                stock_chip("В наявності", "ok"),
                stock_chip("Закінчується", "low")]

    search_row = ft.Row([
        search_field,
        ft.Row(ref=stock_chip_row_ref, controls=make_stock_chips(), spacing=6),
    ], spacing=12, visible=True,
       vertical_alignment=ft.CrossAxisAlignment.CENTER)


    cat_row_ref = ft.Ref[ft.Row]()

    def cat_chip(cat_key):
        label, icon = CATEGORIES[cat_key]
        def on_tap(e):
            current_category["value"] = cat_key
            cat_row_ref.current.controls = make_cat_chips()
            cat_row_ref.current.update()
            refresh_grid(search_field.value, current_filter["value"], cat_key)
        selected = current_category["value"] == cat_key
        return ft.TextButton(label, icon=icon, on_click=on_tap,
            style=ft.ButtonStyle(
                bgcolor=NAV_ACCENT if selected else PANEL_BG,
                color=TEXT_WHITE if selected else TEXT_MAIN,
                side=ft.BorderSide(1, NAV_ACCENT if selected else BORDER),
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=14, vertical=7),
            ))

    def make_cat_chips():
        return [cat_chip(k) for k in CATEGORIES]

    category_row = ft.Container(
        bgcolor=PANEL_BG, border_radius=10,
        padding=ft.padding.symmetric(horizontal=4, vertical=8),
        border=ft.border.all(1, BORDER),
        content=ft.Row(ref=cat_row_ref, controls=make_cat_chips(),
                       spacing=6, scroll=ft.ScrollMode.AUTO),
        visible=True,
    )



    async def go_back(e):
        await page.push_route("/")

    topbar = ft.Container(
        height=64, bgcolor=NAV_BG,
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.LOCAL_PHARMACY_ROUNDED, color=TEXT_WHITE, size=24),
                ft.Text("PharmDesk", size=17, weight=ft.FontWeight.BOLD, color=TEXT_WHITE),
                ft.Container(width=24),
                ft.TextButton("Склад", ref=tab_stock_ref,
                              icon=ft.Icons.INVENTORY_2_OUTLINED,
                              on_click=lambda e: switch_tab("stock"),
                              style=tab_style(True)),
                ft.TextButton("Історія продажів", ref=tab_history_ref,
                              icon=ft.Icons.HISTORY_ROUNDED,
                              on_click=lambda e: switch_tab("history"),
                              style=tab_style(False)),
                ft.Container(expand=True),
                ft.TextButton("Вийти", icon=ft.Icons.LOGOUT_ROUNDED,
                              on_click=go_back,
                              style=ft.ButtonStyle(color="#FFFFFFAA")),
            ],
        ),
    )


    main_area = ft.Container(
        expand=True, bgcolor=BG,
        padding=ft.padding.all(24),
        content=ft.Column(spacing=14, expand=True, controls=[
            ft.Row([ft.Column([
                ft.Text("Склад препаратів", size=22,
                        weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ft.Text("Натисніть на картку щоб переглянути інструкцію та продати",
                        size=12, color=TEXT_MUTED),
            ], spacing=2)]),
            notify_wrapper,
            search_row,
            category_row,
            ft.Divider(color=BORDER, height=1),
            grid_column,
            history_column,
        ]),
    )

    grid_column.controls = build_grid_controls()

    return ft.View(
        route="/pharm",
        padding=0,
        bgcolor=BG,
        controls=[
            ft.Column(expand=True, spacing=0, controls=[
                topbar,
                ft.Row(expand=True, spacing=0,
                       controls=[main_area, sell_panel_wrapper]),
            ])
        ],
    )
