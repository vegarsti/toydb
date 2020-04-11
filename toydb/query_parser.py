from typing import List, Optional, Sequence, Tuple, Type

from toydb.command import Command, Commands, CreateTable, Exit, Insert, Select


def parse_columns(columns_: List[str]) -> Optional[Sequence[Tuple[str, Type]]]:
    number_of_columns = len(columns_) // 2
    columns = []
    for i in range(number_of_columns):
        column_name = columns_[i * 2]
        column_type_str = columns_[i * 2 + 1]
        column_type = {"str": str, "int": int}.get(column_type_str)
        if column_type is None:
            return None
        else:
            columns.append((column_name, column_type))
    return columns


def parse_command(command: str) -> Optional[Command]:
    args = command.split()
    if len(args) == 0:
        return None
    c = args[0]
    if c == Commands.EXIT.value:
        return Exit()
    elif c == Commands.CREATE.value:
        if len(args) < 4:
            return None
        if args[1] != "table":
            return None
        table_name = args[2]
        columns_ = args[3:]
        if len(columns_) % 2 != 0:
            return None
        columns = parse_columns(columns_)
        if columns is None:
            return None
        return CreateTable(table_name=table_name, columns=columns)
    elif c == Commands.INSERT.value:
        if len(args) == 1:
            return None
        values = args[1:]
        return Insert(values=values)
    elif c == Commands.SELECT.value:
        if len(args) == 1:
            return None
        columns_str = " ".join(args[1:])
        columns_ = [c.strip().replace("*", "all") for c in columns_str.split(",")]
        if len(columns_) == len(args) - 1:
            return Select(columns=columns_)
    return None