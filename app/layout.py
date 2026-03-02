"""Top-level layout: navbar + page container."""

from dash import html, dcc, page_container
import dash_bootstrap_components as dbc
from app.components.navbar import create_navbar


def create_layout():
    return html.Div([
        # Stores for shared state
        dcc.Store(id="connection-state-store", data={"state": "disconnected", "message": ""}),
        dcc.Store(id="account-store", data={}),
        dcc.Store(id="positions-store", data=[]),

        # Interval for periodic data refresh
        dcc.Interval(id="global-interval", interval=5000, n_intervals=0),

        # Navbar
        create_navbar(),

        # Page content
        dbc.Container(
            page_container,
            fluid=True,
            className="px-4",
        ),
    ])
