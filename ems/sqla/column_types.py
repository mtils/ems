
from decimal import Decimal

import six

import sqlalchemy.types as types
from sqlalchemy.dialects.sqlite.base import SQLiteDialect

class Monetary(types.TypeDecorator):
    """
    Store all currency values (prices, taxes, money) as Numeric data types to keep optimal precision
    Taken and modified from http://stackoverflow.com/a/10386911/1043456
    Since SQLite does not have native support for Decimal data types,
    this TypeDecorator implements either a Numeric data type or a String data type,
    depending on the backend.
    """
    impl = types.TypeEngine

    def is_sqlite(self, dialect):
        """
        Returns true if the given dialect is any SQLite dialect.
        """
        return isinstance(dialect, SQLiteDialect)

    def load_dialect_impl(self, dialect):
        if self.is_sqlite(dialect):
            return dialect.type_descriptor(types.VARCHAR(100))
        else:
            return dialect.type_descriptor(types.Numeric(10, 4))

    def process_bind_param(self, value, dialect):
        if self.is_sqlite(dialect):
            return six.text_type(value)
        else:
            return value

    def process_result_value(self, value, dialect):
        if self.is_sqlite(dialect):
            try:
                return Decimal(value)
            except:
                return None
        else:
            return value