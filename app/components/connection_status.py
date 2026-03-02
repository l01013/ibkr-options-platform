"""IBKR connection status badge component."""

from dash import html
import dash_bootstrap_components as dbc


def connection_badge(state: str = "disconnected", message: str = "") -> html.Div:
    """Render a connection status badge."""
    color_map = {
        "connected": "success",
        "connecting": "warning",
        "reconnecting": "warning",
        "disconnected": "secondary",
        "error": "danger",
    }
    icon_map = {
        "connected": "bi bi-circle-fill",
        "connecting": "bi bi-arrow-repeat",
        "reconnecting": "bi bi-arrow-repeat",
        "disconnected": "bi bi-circle",
        "error": "bi bi-exclamation-triangle-fill",
    }
    label_map = {
        "connected": "Connected",
        "connecting": "Connecting...",
        "reconnecting": "Reconnecting...",
        "disconnected": "Disconnected",
        "error": "Error",
    }

    color = color_map.get(state, "secondary")
    icon = icon_map.get(state, "bi bi-circle")
    label = label_map.get(state, state)

    return dbc.Badge(
        [html.I(className=f"{icon} me-1"), label],
        color=color,
        pill=True,
        className="fs-6",
        title=message,
    )
