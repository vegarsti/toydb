from typing import Dict, List, Union

from vgdb.statement import CreateTable, Insert, Select
from vgdb.table import Table


class Evaluator:
    def __init__(self, tables: Dict[str, Table]):
        self.tables = tables

    def handle_command(self, command: Union[CreateTable, Insert, Select]) -> Union[str, List[List[Union[str, int]]]]:
        result: Union[str, List[List[Union[str, int]]]]
        if isinstance(command, CreateTable):
            result = self.handle_create(command)
        elif isinstance(command, Select):
            result = self.handle_select(command=command)
        elif isinstance(command, Insert):
            result = self.handle_insert(command=command)
        else:
            raise ValueError("Command not handled. This shouldn't happen")
        return result

    def handle_create(self, command: CreateTable) -> str:
        table = self.tables.get(command.table_name)
        if table is not None:
            raise ValueError(f"table {table.name} already exists with schema {table.columns}")
        else:
            table = Table(name=command.table_name, columns=command.columns)
            table.persist()
            return f"Created table {table.name} with schema {table.columns}."

    def handle_insert(self, command: Insert) -> str:
        table = self.tables.get(command.table_name)
        if table is None:
            raise ValueError(f"table {command.table_name} does not exist")
        try:
            table.insert(command.values)
        except ValueError:
            raise ValueError(f"attempted to insert invalid record, table has schema {table.columns}")
        return "OK"

    def handle_select(self, command: Select) -> List[List[Union[str, int]]]:
        table = self.tables.get(command.table_name)
        if table is None:
            raise ValueError(f"table {command.table_name} does not exist")
        table_indices = table.column_indices_from_names(command.columns)
        if table_indices is None:
            raise ValueError(
                f"incorrect columns {', '.join(command.columns)} in SELECT: table has schema {table.columns}"
            )
        rows = table.all_rows()
        if command.where is not None:
            rows = table.where(rows=rows, where=command.where)
        if command.order_by is not None:
            rows = table.order_by(rows=rows, order_by=command.order_by)
        if command.limit is not None:
            rows = table.limit(rows=rows, limit=command.limit, offset=command.offset)
        to_return = []
        for row in rows:
            row_subset = [row[i] for i in table_indices]
            to_return.append(row_subset)
        return to_return
