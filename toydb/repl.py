import sys
from functools import partial
from typing import Callable, Optional

from blessed import Terminal
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from toydb.query_parser import parse_command
from toydb.statement import CreateTable, Exit, Insert, Select, handle_command
from toydb.table import Table


def create_table(table: Table) -> None:
    try:
        with open(f"{table.name}.db", "x") as f:
            f.write(table.columns)
            f.write("\n")
    except FileExistsError:
        raise ValueError


def loop(prompt: Callable[[], str]) -> None:
    table: Optional[Table] = None
    while True:
        try:
            c = prompt()
        except (KeyboardInterrupt, EOFError):
            sys.exit(1)
        command = parse_command(c.lower().strip())
        if command is None:
            print(f"invalid command: {c}")
            continue
        if isinstance(command, Exit):
            break
        if isinstance(command, CreateTable):
            table = Table(name=command.table_name, columns=command.columns)
            try:
                create_table(table)
                print(f"created table {table.name} with schema {table.columns}")
            except ValueError:
                existing_table = Table.from_file(command.table_name)
                print(f"table {existing_table.name} already exists with schema {existing_table.columns}")
        else:
            if table is None:
                print("please create a table")
            if isinstance(command, Select) or isinstance(command, Insert):
                handle_command(command=command)


def main() -> None:
    style = Style.from_dict({"prompt": "red"})
    message = [("class:prompt", "toydb> ")]
    session = PromptSession(style=style)
    toydb_prompt = partial(session.prompt, message)
    fullscreen = False
    if fullscreen:
        term = Terminal()
        with term.fullscreen(), term.location(0, 0):
            loop(toydb_prompt)
    else:
        loop(toydb_prompt)


if __name__ == "__main__":
    main()
