import flet as ft
import json
import os
from datetime import datetime

BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = os.path.join(BASE, "storages", "medicines.json")
HIST_FILE = os.path.join(BASE, "storages", "sales_history.json")

# ── Палітра ────────────────────────────────────────────────────
BG          = "#F0F4F0"
PANEL_BG    = "#FFFFFF"
NAV_BG      = "#1C2B1E"
NAV_ACCENT  = "#4ADE80"
GREEN_DARK  = "#166534"
GREEN_MID   = "#22C55E"
GREEN_LIGHT = "#DCFCE7"
AMBER       = "#F59E0B"
AMBER_LIGHT = "#FEF3C7"
RED         = "#EF4444"
RED_LIGHT   = "#FEE2E2"
BLUE        = "#3B82F6"
BLUE_LIGHT  = "#EFF6FF"
TEXT_MAIN   = "#111827"
TEXT_MUTED  = "#6B7280"
TEXT_WHITE  = "#FFFFFF"
BORDER      = "#E5E7EB"


# ── Дані: склад ────────────────────────────────────────────────

def load_data():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ── Дані: історія продажів ─────────────────────────────────────

def load_history():
    if not os.path.exists(HIST_FILE):
        with open(HIST_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(HIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def append_history(name: str, qty: int):
    history = load_history()
    history.append({
        "name":      name,
        "amount":    qty,
        "sold_at":   datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
    })
    with open(HIST_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


# ── UI-хелпери ─────────────────────────────────────────────────

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
        return badge("Немає", RED_LIGHT, RED)
    if n < 5:
        return badge(f"{n} шт  ⚠", AMBER_LIGHT, AMBER)
    return badge(f"{n} шт", GREEN_LIGHT, GREEN_DARK)


def notify_bar(msg: str, ok: bool):
    icon  = ft.Icons.CHECK_CIRCLE_ROUNDED if ok else ft.Icons.ERROR_ROUNDED
    color = GREEN_MID if ok else RED
    bg    = GREEN_LIGHT if ok else RED_LIGHT
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, color=color, size=20),
            ft.Text(msg, size=14, color=color, weight=ft.FontWeight.W_600),
        ], spacing=10),
        bgcolor=bg,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=18, vertical=12),
    )


# ── Картка препарату (сітка) ───────────────────────────────────

def grid_card(med, on_sell_click):
    try:
        n = int(med["amount"])
    except Exception:
        n = 0
    disabled = (n == 0)
    overlay  = "#80FFFFFF" if disabled else "#00FFFFFF"

    return ft.Container(
        height=175,
        border_radius=16,
        bgcolor=PANEL_BG,
        border=ft.border.all(1, BORDER),
        shadow=ft.BoxShadow(blur_radius=8, spread_radius=0,
                            offset=ft.Offset(0, 2), color="#0D000000"),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        on_click=(None if disabled else lambda e, m=med: on_sell_click(m)),
        content=ft.Stack([
            ft.Container(
                padding=ft.padding.all(20),
                content=ft.Column(spacing=10, controls=[
                    ft.Text(med["name"], size=17, weight=ft.FontWeight.BOLD,
                            color=TEXT_MAIN, max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    stock_badge(med["amount"]),
                    ft.Text(f"до {med['date']}", size=12, color=TEXT_MUTED),
                ]),
            ),
            ft.Container(bgcolor=overlay, expand=True),
            ft.Container(
                right=14, bottom=14,
                content=ft.Icon(
                    ft.Icons.SHOPPING_CART_CHECKOUT_ROUNDED,
                    color=NAV_ACCENT if not disabled else BORDER,
                    size=26,
                ),
            ),
        ]),
    )


# ── Рядок в історії ───────────────────────────────────────────

def history_row(entry, index):
    is_even = index % 2 == 0
    return ft.Container(
        bgcolor=PANEL_BG if is_even else BG,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=20, vertical=14),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                # індекс
                ft.Container(
                    width=36, height=36,
                    border_radius=18,
                    bgcolor=BLUE_LIGHT,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(str(index + 1), size=12,
                                    color=BLUE, weight=ft.FontWeight.W_700),
                ),
                ft.Container(width=14),
                # назва + час
                ft.Column(spacing=3, expand=True, controls=[
                    ft.Text(entry["name"], size=15,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Text(entry["sold_at"], size=11, color=TEXT_MUTED),
                ]),
                # кількість
                ft.Container(
                    content=ft.Text(
                        f"−{entry['amount']} шт",
                        size=14, color=RED, weight=ft.FontWeight.W_700,
                    ),
                    bgcolor=RED_LIGHT,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                ),
            ],
        ),
    )


# ── Панель продажу (правий слайд-ін) ──────────────────────────

def build_sell_panel(med, on_confirm, on_cancel):
    f_amount = ft.TextField(
        label="Кількість", value="1",
        border_radius=10, border_color=NAV_ACCENT,
        focused_border_color=GREEN_DARK,
        label_style=ft.TextStyle(color=TEXT_MUTED),
        text_style=ft.TextStyle(color=TEXT_MAIN, size=18),
        bgcolor=BG, filled=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.CENTER,
        width=160,
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

    return ft.Container(
        width=320, bgcolor=PANEL_BG,
        border=ft.border.only(left=ft.BorderSide(1, BORDER)),
        padding=ft.padding.all(28),
        content=ft.Column(spacing=20, controls=[
            ft.Row([
                ft.Icon(ft.Icons.SELL_ROUNDED, color=NAV_ACCENT, size=22),
                ft.Text("Продаж", size=18, weight=ft.FontWeight.BOLD,
                        color=TEXT_MAIN),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED,
                              icon_color=TEXT_MUTED, icon_size=20,
                              on_click=on_cancel),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),

            ft.Divider(color=BORDER),

            ft.Container(
                bgcolor=BG, border_radius=12,
                padding=ft.padding.all(16),
                content=ft.Column(spacing=8, controls=[
                    ft.Text(med["name"], size=17,
                            weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                    ft.Row([
                        ft.Text("На складі:", size=13, color=TEXT_MUTED),
                        stock_badge(med["amount"]),
                    ], spacing=8),
                    ft.Text(f"Термін: до {med['date']}",
                            size=12, color=TEXT_MUTED),
                ]),
            ),

            ft.Column(spacing=8,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      controls=[
                ft.Text("Кількість для продажу", size=13,
                        color=TEXT_MUTED, weight=ft.FontWeight.W_500),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE_ROUNDED,
                                  icon_color=GREEN_DARK, icon_size=28,
                                  on_click=decrement),
                    f_amount,
                    ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                                  icon_color=GREEN_DARK, icon_size=28,
                                  on_click=increment),
                ], alignment=ft.MainAxisAlignment.CENTER,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ]),

            ft.ElevatedButton(
                "Підтвердити продаж",
                icon=ft.Icons.CHECK_ROUNDED,
                on_click=lambda e: on_confirm(med, f_amount.value),
                style=ft.ButtonStyle(
                    bgcolor=GREEN_DARK, color=TEXT_WHITE,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.padding.symmetric(horizontal=24, vertical=16),
                ),
                width=260,
            ),
        ]),
    )


# ── Головна функція view ───────────────────────────────────────

def pharmacist_view(page: ft.Page):

    current_filter = {"value": "all"}
    active_tab     = {"value": "stock"}   # "stock" | "history"

    sell_panel_wrapper = ft.Container(visible=False, content=ft.Text(""))
    notify_wrapper     = ft.Container(visible=False, content=ft.Text(""))
    grid_column        = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
    history_column     = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=6,
                                   visible=False)

    # ── таб-перемикач у topbar ────────────────────────────────────

    tab_stock_ref   = ft.Ref[ft.TextButton]()
    tab_history_ref = ft.Ref[ft.TextButton]()

    def tab_style(active: bool):
        return ft.ButtonStyle(
            bgcolor=NAV_ACCENT if active else "#2D4A2F",
            color=GREEN_DARK if active else TEXT_MUTED,
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
        grid_column.update()
        history_column.update()
        search_row.update()

        # при відкритті вкладки «Історія» — завжди оновлюємо список
        if tab == "history":
            refresh_history()

        # сховати панель продажу якщо перейшли на інший таб
        hide_panel()

    # ── фільтрація складу ────────────────────────────────────────

    def filtered(query="", flt="all"):
        data = load_data()
        if query:
            data = [m for m in data if query.lower() in m["name"].lower()]
        if flt == "low":
            data = [m for m in data if int(m.get("amount", 0) or 0) < 5]
        elif flt == "ok":
            data = [m for m in data if int(m.get("amount", 0) or 0) >= 5]
        return data

    # ── сповіщення ───────────────────────────────────────────────

    def show_notify(msg, ok):
        notify_wrapper.content = notify_bar(msg, ok)
        notify_wrapper.visible = True
        notify_wrapper.update()

    # ── панель продажу ───────────────────────────────────────────

    def hide_panel(e=None):
        sell_panel_wrapper.visible = False
        sell_panel_wrapper.update()

    def open_sell_panel(med):
        sell_panel_wrapper.content = build_sell_panel(med, do_sell, hide_panel)
        sell_panel_wrapper.visible = True
        sell_panel_wrapper.update()

    def do_sell(med, qty_str):
        try:
            qty = int(qty_str)
            assert qty > 0
        except Exception:
            show_notify("Введіть коректну кількість!", ok=False)
            return

        data = load_data()
        found = False
        for m in data:
            if m["name"] == med["name"]:
                found = True
                available = int(m["amount"])
                if qty > available:
                    show_notify(
                        f"Недостатньо! На складі лише {available} шт.", ok=False)
                    return
                m["amount"] = str(available - qty)
                break

        if not found:
            show_notify("Препарат не знайдено!", ok=False)
            return

        save_data(data)
        append_history(med["name"], qty)   # ← запис в окремий JSON

        hide_panel()
        refresh_grid(search_field.value, current_filter["value"])
        show_notify(f"Продано: {med['name']} — {qty} шт.", ok=True)

    # ── оновлення сітки складу ───────────────────────────────────

    def build_grid_controls(query="", flt="all"):
        medicines = filtered(query, flt)
        if not medicines:
            return [ft.Container(
                alignment=ft.Alignment.CENTER, padding=60,
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=52, color=TEXT_MUTED),
                    ft.Text("Нічого не знайдено", size=17, color=TEXT_MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            )]
        return [ft.ResponsiveRow(
            spacing=8, run_spacing=8,
            controls=[
                ft.Column([grid_card(m, open_sell_panel)],
                          col={"xs": 12, "sm": 6, "md": 4, "lg": 4})
                for m in medicines
            ],
        )]

    def refresh_grid(query="", flt="all"):
        grid_column.controls = build_grid_controls(query, flt)
        grid_column.update()

    # ── оновлення списку історії ──────────────────────────────────

    def refresh_history():
        history = load_history()
        if not history:
            history_column.controls = [
                ft.Container(
                    alignment=ft.Alignment.CENTER, padding=60,
                    content=ft.Column([
                        ft.Icon(ft.Icons.HISTORY_ROUNDED, size=52, color=TEXT_MUTED),
                        ft.Text("Продажів ще не було", size=17, color=TEXT_MUTED),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                )
            ]
        else:
            # Найновіші зверху
            rows = list(reversed(history))
            history_column.controls = [
                ft.Container(
                    padding=ft.padding.only(bottom=4),
                    content=ft.Row([
                        ft.Text(
                            f"Всього продажів: {len(history)}",
                            size=13, color=TEXT_MUTED,
                        ),
                    ]),
                ),
                *[history_row(e, i) for i, e in enumerate(rows)],
            ]
        history_column.update()

    # ── пошук ────────────────────────────────────────────────────

    search_field = ft.TextField(
        hint_text="Пошук препарату…",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_radius=12,
        border_color=BORDER,
        focused_border_color=NAV_ACCENT,
        hint_style=ft.TextStyle(color=TEXT_MUTED),
        text_style=ft.TextStyle(color=TEXT_MAIN),
        bgcolor=PANEL_BG, filled=True, expand=True,
        on_change=lambda e: refresh_grid(e.control.value, current_filter["value"]),
    )

    # ── фільтр-чіпи ──────────────────────────────────────────────

    chip_row_ref = ft.Ref[ft.Row]()

    def chip(label, value):
        def on_tap(e):
            current_filter["value"] = value
            chip_row_ref.current.controls = make_chips()
            chip_row_ref.current.update()
            refresh_grid(search_field.value, value)

        selected = current_filter["value"] == value
        return ft.TextButton(
            label, on_click=on_tap,
            style=ft.ButtonStyle(
                bgcolor=NAV_ACCENT if selected else BG,
                color=GREEN_DARK if selected else TEXT_MUTED,
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
        )

    def make_chips():
        return [
            chip("Всі",          "all"),
            chip("Мало (<5)",    "low"),
            chip("В наявності",  "ok"),
        ]

    chip_row = ft.Row(ref=chip_row_ref, controls=make_chips(), spacing=8)

    search_row = ft.Column(
        [search_field, chip_row],
        spacing=10,
        visible=True,
    )

    # ── topbar ────────────────────────────────────────────────────

    async def go_back(e):
        await page.push_route("/")

    topbar = ft.Container(
        height=64, bgcolor=NAV_BG,
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.LOCAL_PHARMACY_ROUNDED, color=NAV_ACCENT, size=24),
                ft.Text("PharmDesk", size=17, weight=ft.FontWeight.BOLD,
                        color=TEXT_WHITE),
                ft.Container(width=16),

                # ── таби ──
                ft.TextButton(
                    "Склад",
                    ref=tab_stock_ref,
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    on_click=lambda e: switch_tab("stock"),
                    style=tab_style(True),        # активний за замовчуванням
                ),
                ft.TextButton(
                    "Історія продажів",
                    ref=tab_history_ref,
                    icon=ft.Icons.HISTORY_ROUNDED,
                    on_click=lambda e: switch_tab("history"),
                    style=tab_style(False),
                ),

                ft.Container(expand=True),
                ft.TextButton(
                    "Вийти",
                    icon=ft.Icons.LOGOUT_ROUNDED,
                    on_click=go_back,
                    style=ft.ButtonStyle(color=TEXT_MUTED),
                ),
            ],
        ),
    )

    # ── основна область ───────────────────────────────────────────

    main_area = ft.Container(
        expand=True, bgcolor=BG,
        padding=ft.padding.all(28),
        content=ft.Column(
            spacing=16, expand=True,
            controls=[
                ft.Row([
                    ft.Column([
                        ft.Text("Склад препаратів", size=24,
                                weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                        ft.Text("Натисніть на картку щоб продати",
                                size=13, color=TEXT_MUTED),
                    ], spacing=2),
                ]),
                notify_wrapper,
                search_row,
                ft.Divider(color=BORDER, height=1),
                grid_column,
                history_column,
            ],
        ),
    )

    # ── початкове заповнення без update() ────────────────────────
    grid_column.controls = build_grid_controls()

    return ft.View(
        route="/pharm",
        padding=0,
        bgcolor=BG,
        controls=[
            ft.Column(
                expand=True, spacing=0,
                controls=[
                    topbar,
                    ft.Row(
                        expand=True, spacing=0,
                        controls=[main_area, sell_panel_wrapper],
                    ),
                ],
            )
        ],
    )
