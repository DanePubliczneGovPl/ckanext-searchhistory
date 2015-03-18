import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import types
from sqlalchemy.orm import class_mapper
from ckan import model

search_history_table = None

class SearchHistory(model.DomainObject):

    @classmethod
    def search_history(cls, **kw):
        '''Finds search history according to given params.'''
        limit = kw.pop('limit', None)
        query = model.Session.query(cls).autoflush(False)
        query = query.filter_by(**kw)
        query = query.order_by(sa.desc(cls.created))
        query = query.limit(limit)
        return query.all()


def make_uuid():
    return unicode(uuid.uuid4())


def init_db():
    global search_history_table

    if search_history_table is None:
        search_history_table = sa.Table('ckanext_searchhistory', model.meta.metadata,
            sa.Column('id', types.UnicodeText, primary_key=True, default=make_uuid),
            sa.Column('params', types.UnicodeText, default=u''),
            sa.Column('user_id', types.UnicodeText, default=u''),
            sa.Column('created', types.DateTime, default=datetime.datetime.utcnow),
        )

        model.meta.mapper(
            SearchHistory,
            search_history_table,
        )

    if not search_history_table.exists():
        search_history_table.create()


def table_dictize(obj, context, **kw):
    '''Get any model object and represent it as a dict'''
    result_dict = {}

    if isinstance(obj, sa.engine.RowProxy):
        fields = obj.keys()
    else:
        ModelClass = obj.__class__
        table = class_mapper(ModelClass).mapped_table
        fields = [field.name for field in table.c]

    for field in fields:
        name = field
        if name in ('current', 'expired_timestamp', 'expired_id'):
            continue
        if name == 'continuity_id':
            continue
        value = getattr(obj, name)
        if value is None:
            result_dict[name] = value
        elif isinstance(value, dict):
            result_dict[name] = value
        elif isinstance(value, int):
            result_dict[name] = value
        elif isinstance(value, datetime.datetime):
            result_dict[name] = value.isoformat()
        elif isinstance(value, list):
            result_dict[name] = value
        else:
            result_dict[name] = unicode(value)

    result_dict.update(kw)

    return result_dict

