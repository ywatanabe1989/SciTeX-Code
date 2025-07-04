from functools import partial

import prettytable

from sqlalchemy import Column
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.ext.declarative import declarative_base


def as_dict(self):
    """convert columns to ``dict``
    """
    return {k: v for k, v in self.__dict__.items() if not isinstance(v, InstanceState)}


def get_table(columns):
    table = prettytable.PrettyTable(['Key', 'Comment', 'Type', 'Default'])
    for k, v in columns.items():
        table.add_row([k, v.comment, v.type, v.default])
    for field in table._field_names:
        table.align[field] = 'l'
    return table


def __str__(self):
    return f'{self.__name__} <{self.as_dict()}>'


def DynamicModel(name, columns, tablename='data'):
    """Create a Base Model

    :param name: name of model
    :param columns: dict of sqlalchemy columns, eg. {'id': Column(...)}
    :param tablename: name of table
    
    :returns: (Base, Model)
    """
    Base = declarative_base()

    map_data = {
        '__name__': name,
        '__tablename__': tablename,
        'as_dict': as_dict,
        '__str__': __str__,
        '__repr__': __str__,
        'get_table': partial(get_table, columns),
    }

    return type(name, (Base,), dict(columns, **map_data))
