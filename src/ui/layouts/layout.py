import dash_bootstrap_components as dbc
from dash import html, dcc
from ui.info.dashboard_info import get_dashboard_info
from helpers.config_parser import load_ui_config

ui_config = load_ui_config("config/ui_config.yaml")
theme_config = ui_config.get("theme", {})

BRAND_COLORS = {
    "primary": theme_config.get("primary", "#1dd74e"),
    "light_bg": theme_config.get("light_bg", "#ffffff"),
    "dark_bg": theme_config.get("dark_bg", "#2c3e50"),
    "text_light": theme_config.get("text_light", "#ecf0f1"),
    "text_dark": theme_config.get("text_dark", "#212529")
}

BUTTON_COLOR = theme_config.get("button", BRAND_COLORS["primary"])

def get_master_layout():
    return html.Div([
        dbc.NavbarSimple(
            brand="DeepLens Dashboard",
            brand_href="/dashboard",
            color=BRAND_COLORS["primary"],
            dark=True,
            children=[
                dbc.NavItem(dbc.NavLink("Home", href="/dashboard")),
                dbc.Button("Learn More", id="open-info", color="light", size="sm", n_clicks=0,
                           style={"marginLeft": "auto", "backgroundColor": BUTTON_COLOR, "borderColor": BUTTON_COLOR})
            ]
        ),
        get_dashboard_info(),

        dcc.Store(id="shared-upload-image", storage_type="memory"),

        html.Div(id="page-content")
    ])
