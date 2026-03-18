from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table


console = Console()


def print_json(data: Any) -> None:
    console.print_json(json.dumps(data, ensure_ascii=False, default=str))


def print_kv(title: str, values: dict[str, Any]) -> None:
    table = Table(title=title, show_header=False, box=None)
    table.add_column("key", style="bold")
    table.add_column("value")
    for key, value in values.items():
        table.add_row(str(key), "" if value is None else str(value))
    console.print(table)


def print_table(title: str, columns: list[str], rows: list[list[Any]]) -> None:
    table = Table(title=title)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(*["" if value is None else str(value) for value in row])
    console.print(table)


def print_message(message: str) -> None:
    console.print(message)
