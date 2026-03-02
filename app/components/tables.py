"""Reusable table components."""

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html


def create_data_table(
    row_data: list[dict],
    column_defs: list[dict],
    table_id: str = "data-table",
    height: int = 400,
    page_size: int = 50,
) -> dag.AgGrid:
    """Create an AG Grid table with sorting, filtering, and pagination."""
    default_col_def = {
        "sortable": True,
        "filter": True,
        "resizable": True,
        "floatingFilter": True,
    }

    return dag.AgGrid(
        id=table_id,
        rowData=row_data,
        columnDefs=column_defs,
        defaultColDef=default_col_def,
        dashGridOptions={
            "pagination": True,
            "paginationPageSize": page_size,
            "animateRows": True,
            "rowSelection": "single",
        },
        style={"height": f"{height}px"},
        className="ag-theme-alpine-dark",
    )


def metric_card(title: str, value: str, color: str = "primary", icon: str = "") -> dbc.Card:
    """Create a metric display card."""
    body_children = []
    if icon:
        body_children.append(html.I(className=f"bi {icon} fs-3 text-{color} mb-2 d-block"))
    body_children.extend([
        html.H6(title, className="card-subtitle text-muted mb-1"),
        html.H4(value, className=f"card-title text-{color} mb-0"),
    ])

    return dbc.Card(
        dbc.CardBody(body_children, className="text-center p-3"),
        className="shadow-sm",
    )
