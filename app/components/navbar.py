"""Navigation bar component."""

import dash_bootstrap_components as dbc
from dash import html


def create_navbar():
    return dbc.Navbar(
        dbc.Container(
            [
                dbc.NavbarBrand(
                    [html.I(className="bi bi-graph-up-arrow me-2"), "IBKR Options Platform"],
                    href="/",
                    className="fw-bold",
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                            dbc.NavItem(dbc.NavLink("Market Data", href="/market-data", active="exact")),
                            dbc.NavItem(dbc.NavLink("Screener", href="/screener", active="exact")),
                            dbc.NavItem(dbc.NavLink("Options Chain", href="/options-chain", active="exact")),
                            dbc.NavItem(dbc.NavLink("Backtester", href="/backtester", active="exact")),
                            dbc.NavItem(dbc.NavLink("Settings", href="/settings", active="exact")),
                        ],
                        className="ms-auto",
                        navbar=True,
                    ),
                    id="navbar-collapse",
                    navbar=True,
                ),
                html.Div(id="connection-badge", className="ms-3"),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-4",
        sticky="top",
    )
