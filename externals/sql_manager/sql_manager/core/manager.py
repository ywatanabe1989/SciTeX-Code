from numpy import isin
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.state import InstanceState

from simple_loggers import SimpleLogger


class Manager(object):
    """The Database Manager

    :param Base: ``Base`` object created by ``DynamicModel``
    :param dbfile: path of database file
    :param uri: uri of database. SQLite3: ``sqlite:///test.db``, MySQL: ``mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}/{DBNAME}``
    :param echo: turn echo on
    :param drop: drop table before create
    :param logger: a logging object
    """
    def __init__(self, Base, dbfile=':memory:', uri=None, echo=False, drop=False, logger=None):
        self.Base = Base
        self.drop = drop
        self.uri = uri if uri else f'sqlite:///{dbfile}'
        self.logger = logger or SimpleLogger('Manager')
        self.engine = sqlalchemy.create_engine(self.uri, echo=echo)
        self.engine.logger.level = self.logger.level
        self.session = self.connect()
    
    def __enter__(self):
        self.create_table(drop=self.drop)
        return self

    def __exit__(self, *exc_info):
        self.session.commit()
        self.session.close()
        self.logger.debug('database closed.')

    def connect(self):
        """create a connection
        """
        DBSession = sessionmaker(bind=self.engine)
        return DBSession()

    def create_table(self, drop=False):
        """create all table from Base and Model
        """
        if drop:
            self.Base.metadata.drop_all(self.engine)
        self.Base.metadata.create_all(self.engine)

    def query(self, key=None, value=None, like=False):
        """query database with key-value

        :param key: the field name
        :param value: the field value
        :returns: a query object of sqlalchemy
        """
        query = self.session.query(self.Base)
        if key:
            if key not in self.Base.__dict__:
                self.logger.warning(f'unavailable key: {key}')
                return None
            else:
                query = query.filter(self.Base.__dict__[key]==value)

        return query

    def delete(self, key, value):
        """delete row(s) by key-value

        :param key: the field name
        :param value: the field value
        """
        res = self.query(key, value)
        if res.count():
            self.logger.debug(f'delete {res.count()} row(s)')
            res.delete()
        else:
            self.logger.debug(f'key input not in database: {key}={value}')

    def insert(self, datas, key=None, update=True):
        """insert data row by row

        :param datas: an instance of Base, or a list of instance
        :param key: specify the key field
        :param update: update row when key is existing
        """
        if not isinstance(datas, list):
            datas = [datas]

        for data in datas:

            if not isinstance(data, self.Base):
                data = self.Base(**data)

            res = self.query(key, data.__dict__.get(key))

            if (not key) or (not res.count()):
                self.logger.debug(f'>>> insert data: {data}')
                self.session.add(data)
            elif update:
                self.logger.debug(f'>>> update data: {data}')
                context = {k: v for k, v in data.__dict__.items() if not isinstance(v, InstanceState)}
                res.update(context)
            else:
                self.logger.debug(f'>>> skip add existing data: {data}')

    def insert_bulk(self, datas, Meta=None):
        """insert data in bulk mode

        :param datas: a list of objects or mappings
        """
        if isinstance(datas[0], self.Base):
            self.session.bulk_save_objects(datas)
            self.logger.debug(f'>>> inserted {len(datas)} objects ...')
        else:
            self.session.bulk_insert_mappings(self.Base, datas)
            self.logger.debug(f'>>> inserted {len(datas)} mappings ...')
